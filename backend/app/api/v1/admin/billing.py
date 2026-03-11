"""
プラン・請求・解約 API（Phase 4 Phase C）
GET /admin/plans, POST /admin/plans/change, POST /admin/subscription/cancel,
GET /admin/invoices, GET /admin/invoices/{invoice_id}/receipt
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.facility import Facility
from app.schemas.billing import (
    PLAN_DISPLAY,
    PlanInfo,
    PlansResponse,
    PlanChangeRequest,
    PlanChangeResponse,
    SubscriptionCancelRequest,
    SubscriptionCancelResponse,
    InvoiceItemResponse,
    InvoicesResponse,
    ReceiptResponse,
)
from app.core.cache import cache_key, delete_cache
from app.services.auth_service import get_plan_defaults
from app.services import stripe_service

logger = logging.getLogger(__name__)


async def _invalidate_dashboard_cache(facility_id: int) -> None:
    """プラン変更後、ダッシュボードAPIのキャッシュを無効化する。"""
    key = cache_key("dashboard:data", facility_id=facility_id)
    await delete_cache(key)

router = APIRouter(prefix="/admin", tags=["admin", "billing"])


async def _get_facility_for_user(db: AsyncSession, facility_id: int) -> Facility:
    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found")
    return facility


def _build_plans_list() -> list[PlanInfo]:
    """変更可能なプラン一覧を組み立てる。"""
    plan_types = ["Free", "Mini", "Small", "Standard", "Premium"]
    out = []
    for pt in plan_types:
        defaults = get_plan_defaults(pt)
        display = PLAN_DISPLAY.get(pt, {"name_ja": pt, "price_yen": 0})
        out.append(PlanInfo(
            plan_type=pt,
            name_ja=display["name_ja"],
            price_yen=display["price_yen"],
            monthly_question_limit=defaults.get("monthly_question_limit"),
            faq_limit=defaults.get("faq_limit"),
            language_limit=defaults.get("language_limit"),
        ))
    return out


@router.get("/plans", response_model=PlansResponse)
async def get_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """変更可能なプラン一覧と現在プランを返す。"""
    if not current_user.facility_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with any facility")
    facility = await _get_facility_for_user(db, current_user.facility_id)
    return PlansResponse(
        current_plan_type=facility.plan_type or "Free",
        plans=_build_plans_list(),
        stripe_configured=stripe_service.is_stripe_configured(),
    )


@router.post("/plans/change", response_model=PlanChangeResponse)
async def change_plan(
    body: PlanChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """プラン変更（アップグレード/ダウングレード）。Stripe 更新 + DB の plan_type / 制限値更新。"""
    if not current_user.facility_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with any facility")
    target = body.target_plan_type
    if target not in ("Free", "Mini", "Small", "Standard", "Premium"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target_plan_type")

    facility = await _get_facility_for_user(db, current_user.facility_id)

    if target == "Free":
        if not stripe_service.is_stripe_configured():
            # Stripe 未設定の場合は DB のみ Free に更新
            defaults = get_plan_defaults("Free")
            facility.plan_type = "Free"
            facility.subscription_plan = "free"
            facility.monthly_question_limit = defaults.get("monthly_question_limit")
            facility.faq_limit = defaults.get("faq_limit")
            facility.language_limit = defaults.get("language_limit")
            facility.plan_updated_at = datetime.now(timezone.utc)
            facility.stripe_subscription_id = None
            facility.subscription_status = "canceled"
            facility.cancel_at_period_end = False
            await db.commit()
            await _invalidate_dashboard_cache(facility.id)
            return PlanChangeResponse(plan_type="Free", message="プランを Free に変更しました。")
        if facility.stripe_subscription_id:
            try:
                stripe_service.cancel_subscription(facility.stripe_subscription_id, at_period_end=False)
            except Exception as e:
                logger.exception("Stripe cancel on plan change to Free: %s", e)
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to cancel subscription")
        defaults = get_plan_defaults("Free")
        facility.plan_type = "Free"
        facility.subscription_plan = "free"
        facility.monthly_question_limit = defaults.get("monthly_question_limit")
        facility.faq_limit = defaults.get("faq_limit")
        facility.language_limit = defaults.get("language_limit")
        facility.plan_updated_at = datetime.now(timezone.utc)
        facility.stripe_subscription_id = None
        facility.subscription_status = "canceled"
        facility.cancel_at_period_end = False
        await db.commit()
        await _invalidate_dashboard_cache(facility.id)
        return PlanChangeResponse(plan_type="Free", message="プランを Free に変更しました。")

    # 有料プランへ変更
    if not stripe_service.is_stripe_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe is not configured")
    price_id = stripe_service.get_price_id_for_plan(target)
    if not price_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Price not configured for plan: {target}")

    now = datetime.now(timezone.utc)
    defaults = get_plan_defaults(target)

    # Stripe Customer がなければ作成
    if not facility.stripe_customer_id:
        try:
            customer = stripe_service.create_customer(
                email=facility.email,
                name=facility.name,
                facility_id=facility.id,
            )
            facility.stripe_customer_id = customer.id
            await db.commit()
        except Exception as e:
            logger.exception("Stripe Customer create failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to create Stripe customer")

    # サブスクがなければ作成、あれば Price 変更（解約済みサブスクの場合は新規作成に切り替え）
    sub = None
    if not facility.stripe_subscription_id:
        try:
            sub = stripe_service.create_subscription(
                customer_id=facility.stripe_customer_id,
                price_id=price_id,
                facility_id=facility.id,
            )
        except Exception as e:
            logger.exception("Stripe Subscription create failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to create subscription")
    else:
        try:
            sub = stripe_service.update_subscription_price(facility.stripe_subscription_id, price_id)
        except Exception as e:
            err_msg = str(e).lower()
            # 解約済みサブスクは Stripe が更新を拒否する。DB をクリアして新規サブスク作成に切り替え
            if "canceled subscription" in err_msg or "incomplete_expired" in err_msg:
                logger.warning(
                    "Stripe subscription is canceled/invalid (facility_id=%s), creating new subscription: %s",
                    facility.id,
                    e,
                )
                facility.stripe_subscription_id = None
                facility.subscription_status = "canceled"
                await db.commit()
                try:
                    sub = stripe_service.create_subscription(
                        customer_id=facility.stripe_customer_id,
                        price_id=price_id,
                        facility_id=facility.id,
                    )
                except Exception as e2:
                    logger.exception("Stripe Subscription create failed (after canceled sub): %s", e2)
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Failed to create subscription",
                    )
            else:
                logger.exception("Stripe Subscription update failed: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to update subscription",
                )

    if sub:
        facility.stripe_subscription_id = sub.id
        facility.subscription_status = sub.get("status") or "active"
        facility.cancel_at_period_end = False

    facility.plan_type = target
    facility.subscription_plan = target.lower()
    facility.monthly_question_limit = defaults.get("monthly_question_limit")
    facility.faq_limit = defaults.get("faq_limit")
    facility.language_limit = defaults.get("language_limit")
    facility.plan_updated_at = now
    await db.commit()
    await _invalidate_dashboard_cache(facility.id)
    return PlanChangeResponse(plan_type=target, message=f"プランを {target} に変更しました。")


@router.post("/subscription/cancel", response_model=SubscriptionCancelResponse)
async def cancel_subscription(
    body: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解約（期間末または即時）。Stripe で解約し、DB を更新。"""
    if not current_user.facility_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with any facility")
    facility = await _get_facility_for_user(db, current_user.facility_id)
    if not facility.stripe_subscription_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active subscription to cancel")
    if not stripe_service.is_stripe_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe is not configured")

    try:
        sub = stripe_service.cancel_subscription(
            facility.stripe_subscription_id,
            at_period_end=body.at_period_end,
        )
    except Exception as e:
        logger.exception("Stripe cancel failed: %s", e)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to cancel subscription")

    if body.at_period_end:
        facility.cancel_at_period_end = True
        facility.subscription_status = sub.get("status") or "active"
        await db.commit()
        return SubscriptionCancelResponse(message="期間末で解約するよう設定しました。")
    else:
        facility.stripe_subscription_id = None
        facility.subscription_status = "canceled"
        facility.cancel_at_period_end = False
        facility.plan_type = "Free"
        facility.subscription_plan = "free"
        defaults = get_plan_defaults("Free")
        facility.monthly_question_limit = defaults.get("monthly_question_limit")
        facility.faq_limit = defaults.get("faq_limit")
        facility.language_limit = defaults.get("language_limit")
        facility.plan_updated_at = datetime.now(timezone.utc)
        await db.commit()
        await _invalidate_dashboard_cache(facility.id)
        return SubscriptionCancelResponse(message="解約しました。")


@router.get("/invoices", response_model=InvoicesResponse)
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """請求履歴一覧（Stripe Invoice 一覧）。"""
    if not current_user.facility_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with any facility")
    facility = await _get_facility_for_user(db, current_user.facility_id)
    if not facility.stripe_customer_id:
        return InvoicesResponse(invoices=[])
    if not stripe_service.is_stripe_configured():
        return InvoicesResponse(invoices=[])

    try:
        raw = stripe_service.list_invoices(facility.stripe_customer_id)
    except Exception as e:
        logger.exception("Stripe Invoice list failed: %s", e)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to list invoices")

    invoices = []
    for inv in raw:
        invoices.append(InvoiceItemResponse(
            id=inv.get("id", ""),
            amount_due=inv.get("amount_due") or 0,
            status=inv.get("status"),
            created=inv.get("created"),
            hosted_invoice_url=inv.get("hosted_invoice_url"),
        ))
    return InvoicesResponse(invoices=invoices)


@router.get("/invoices/{invoice_id}/receipt", response_model=ReceiptResponse)
async def get_invoice_receipt(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """領収書 URL（Hosted Invoice Page または PDF）を返す。"""
    if not current_user.facility_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with any facility")
    facility = await _get_facility_for_user(db, current_user.facility_id)
    if not facility.stripe_customer_id or not stripe_service.is_stripe_configured():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    inv = stripe_service.retrieve_invoice(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    if inv.get("customer") != facility.stripe_customer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    url = stripe_service.get_invoice_receipt_url(invoice_id)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt URL not available")
    return ReceiptResponse(url=url)
