"""
Stripe Webhook 受信（Phase 4 Phase B）
署名検証のため生ボディを使用。認証不要（Stripe の署名で検証）。
"""

import logging
from typing import Any

import stripe
from fastapi import APIRouter, Request, Response, status
from sqlalchemy import select

from app.core.config import settings
from app.database import AsyncSessionLocal
from app.models.facility import Facility

logger = logging.getLogger(__name__)

router = APIRouter()


async def _update_facility_subscription(
    facility_id: int,
    stripe_subscription_id: str | None,
    subscription_status: str | None,
    cancel_at_period_end: bool | None = None,
    plan_type_to_free: bool = False,
) -> None:
    """施設の Stripe サブスク関連カラムを更新する。"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Facility).where(Facility.id == facility_id))
        facility = result.scalar_one_or_none()
        if not facility:
            logger.warning("Webhook: facility_id=%s not found", facility_id)
            return
        if stripe_subscription_id is not None:
            facility.stripe_subscription_id = stripe_subscription_id
        if subscription_status is not None:
            facility.subscription_status = subscription_status
        if cancel_at_period_end is not None:
            facility.cancel_at_period_end = cancel_at_period_end
        if plan_type_to_free:
            facility.plan_type = "Free"
            facility.subscription_plan = "free"
            facility.stripe_subscription_id = None
            facility.subscription_status = "canceled"
        await db.commit()


async def _handle_subscription_created(subscription: Any) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Facility).where(Facility.stripe_customer_id == customer_id)
        )
        facility = result.scalar_one_or_none()
    if not facility:
        fid = subscription.get("metadata", {}).get("facility_id")
        if fid:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Facility).where(Facility.id == int(fid)))
                facility = result.scalar_one_or_none()
    if facility:
        await _update_facility_subscription(
            facility.id,
            stripe_subscription_id=subscription.get("id"),
            subscription_status=subscription.get("status"),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
        )
        logger.info("Webhook subscription.created: facility_id=%s subscription_id=%s", facility.id, subscription.get("id"))


async def _handle_subscription_updated(subscription: Any) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Facility).where(Facility.stripe_customer_id == customer_id)
        )
        facility = result.scalar_one_or_none()
    if not facility:
        fid = subscription.get("metadata", {}).get("facility_id")
        if fid:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Facility).where(Facility.id == int(fid)))
                facility = result.scalar_one_or_none()
    if facility:
        await _update_facility_subscription(
            facility.id,
            stripe_subscription_id=subscription.get("id"),
            subscription_status=subscription.get("status"),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
        )
        logger.info("Webhook subscription.updated: facility_id=%s status=%s", facility.id, subscription.get("status"))


async def _handle_subscription_deleted(subscription: Any) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Facility).where(Facility.stripe_customer_id == customer_id)
        )
        facility = result.scalar_one_or_none()
    if not facility:
        fid = subscription.get("metadata", {}).get("facility_id")
        if fid:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Facility).where(Facility.id == int(fid)))
                facility = result.scalar_one_or_none()
    if facility:
        await _update_facility_subscription(
            facility.id,
            stripe_subscription_id=None,
            subscription_status="canceled",
            cancel_at_period_end=False,
            plan_type_to_free=True,
        )
        logger.info("Webhook subscription.deleted: facility_id=%s -> plan_type=Free", facility.id)


async def _handle_invoice_paid(invoice: Any) -> None:
    """請求書支払い完了。必要なら施設別ログや通知を行う。"""
    customer_id = invoice.get("customer")
    logger.info("Webhook invoice.paid: customer_id=%s invoice_id=%s", customer_id, invoice.get("id"))


async def _handle_invoice_payment_failed(invoice: Any) -> None:
    """請求書支払い失敗。必要ならアラートや施設への通知を行う。"""
    customer_id = invoice.get("customer")
    logger.warning("Webhook invoice.payment_failed: customer_id=%s invoice_id=%s", customer_id, invoice.get("id"))


@router.post(
    "/stripe",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def stripe_webhook(request: Request) -> Response:
    """
    Stripe Webhook 受信。
    署名検証に生ボディが必要なため、JSON ではなく bytes で受け取り検証する。
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        logger.warning("Stripe Webhook: STRIPE_WEBHOOK_SECRET not set, rejecting")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except ValueError as e:
        logger.warning("Stripe Webhook invalid payload: %s", e)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except stripe.SignatureVerificationError as e:
        logger.warning("Stripe Webhook signature verification failed: %s", e)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    ev_type = event.get("type")
    data = event.get("data", {})
    obj = data.get("object") or {}

    try:
        if ev_type == "customer.subscription.created":
            await _handle_subscription_created(obj)
        elif ev_type == "customer.subscription.updated":
            await _handle_subscription_updated(obj)
        elif ev_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(obj)
        elif ev_type == "invoice.paid":
            await _handle_invoice_paid(obj)
        elif ev_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(obj)
        else:
            logger.debug("Stripe Webhook unhandled event type: %s", ev_type)
    except Exception as e:
        logger.exception("Stripe Webhook handler error for %s: %s", ev_type, e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status_code=status.HTTP_200_OK)
