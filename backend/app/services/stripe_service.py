"""
Stripe 連携サービス（Phase 4 Phase B / Phase E）
Customer 作成、Subscription 作成/更新/解約、Invoice 一覧・領収書 URL 取得。
Phase E: 従量課金メーターへの使用量イベント送信。
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional, List, Any

import httpx
import stripe
from stripe.util import convert_to_dict
from app.core.config import settings

logger = logging.getLogger(__name__)

# 設定があれば Stripe API キーをセット（Docker 起動時は未設定でも可）
if getattr(settings, "stripe_secret_key", None):
    stripe.api_key = settings.stripe_secret_key

# 2026-04-15 時点の税率ID（Stripe test）
# A1: 新規作成とプラン変更で同じ税率を適用し、請求表示を対称化する。
DEFAULT_SUBSCRIPTION_TAX_RATE_IDS = ["txr_1TGKOzLnkMufdVquYoyM7JZB"]


def _ensure_stripe_configured() -> None:
    if not settings.stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY is not configured. Set it in .env or environment.")


def get_price_id_for_plan(plan_type: str) -> Optional[str]:
    """
    plan_type（Free/Mini/Small/Standard/Premium）に対応する Stripe 月額 Price ID を返す。
    Free は Stripe で契約しないため None。
    """
    mapping = {
        "Mini": settings.stripe_price_id_mini,
        "Small": settings.stripe_price_id_small,
        "Standard": settings.stripe_price_id_standard,
        "Premium": settings.stripe_price_id_premium,
    }
    return mapping.get(plan_type) or None


def create_customer(
    email: str,
    name: str,
    facility_id: int,
) -> Optional[stripe.Customer]:
    """
    Stripe Customer を作成する。
    未設定時は None を返す（Free のみ等で Stripe を使わない場合）。
    """
    _ensure_stripe_configured()
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name or None,
            metadata={"facility_id": str(facility_id)},
            # Stripe の請求書/領収書PDF・メール等の表示言語を日本語に寄せる。
            # 既存顧客の言語は Stripe 側で変更が必要（PDF確定後は過去分に反映されない）。
            preferred_locales=["ja"],
        )
        return customer
    except stripe.StripeError as e:
        logger.exception("Stripe Customer create failed: %s", e)
        raise


def create_subscription(
    customer_id: str,
    price_id: str,
    facility_id: int,
    metadata: Optional[dict] = None,
) -> stripe.Subscription:
    """
    月額サブスクリプションを作成する。
    従量課金（usage）は Phase E で追加する想定。ここでは月額のみ。
    """
    _ensure_stripe_configured()
    try:
        sub = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price": price_id,
                "tax_rates": DEFAULT_SUBSCRIPTION_TAX_RATE_IDS
            }],
            payment_behavior="default_incomplete",
            metadata=metadata or {"facility_id": str(facility_id)},
            expand=["latest_invoice.payment_intent"],
        )
        return sub
    except stripe.StripeError as e:
        logger.exception("Stripe Subscription create failed: %s", e)
        raise


def update_subscription_price(
    subscription_id: str,
    new_price_id: str,
) -> stripe.Subscription:
    """サブスクリプションの Price を変更（プラン変更）する。"""
    _ensure_stripe_configured()
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        if not sub["items"]["data"]:
            raise ValueError("Subscription has no items")
        si_id = sub["items"]["data"][0]["id"]
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": si_id,
                "price": new_price_id,
                "tax_rates": DEFAULT_SUBSCRIPTION_TAX_RATE_IDS,
            }],
            proration_behavior="create_prorations",
        )
        return stripe.Subscription.retrieve(subscription_id)
    except stripe.StripeError as e:
        logger.exception("Stripe Subscription update failed: %s", e)
        raise


def cancel_subscription(
    subscription_id: str,
    at_period_end: bool = True,
) -> stripe.Subscription:
    """
    サブスクリプションを解約する。
    at_period_end=True の場合は期間末で解約、False の場合は即時解約。
    """
    _ensure_stripe_configured()
    try:
        if at_period_end:
            sub = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
        else:
            sub = stripe.Subscription.delete(subscription_id)
        return sub
    except stripe.StripeError as e:
        logger.exception("Stripe Subscription cancel failed: %s", e)
        raise


def retrieve_subscription(subscription_id: str) -> Optional[stripe.Subscription]:
    """サブスクリプションを取得する。"""
    _ensure_stripe_configured()
    try:
        return stripe.Subscription.retrieve(subscription_id)
    except stripe.StripeError as e:
        logger.warning("Stripe Subscription retrieve failed: %s", e)
        return None


def list_invoices(
    customer_id: str,
    limit: int = 100,
) -> List[dict[str, Any]]:
    """顧客の請求書一覧を取得する。API 層では dict のみを扱うため StripeObject は dict に正規化する。"""
    _ensure_stripe_configured()
    try:
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit,
        )
        # stripe-python 7+ の ListObject は dict ではないため .get("data") は不可（KeyError: 'get' 相当）
        if isinstance(invoices, dict):
            rows: List[Any] = list(invoices.get("data", []))
        else:
            rows = list(getattr(invoices, "data", None) or [])
        out: List[dict[str, Any]] = []
        for inv in rows:
            if isinstance(inv, dict):
                out.append(inv)
            else:
                out.append(convert_to_dict(inv))
        return out
    except stripe.StripeError as e:
        logger.exception("Stripe Invoice list failed: %s", e)
        raise


def retrieve_invoice(invoice_id: str) -> Optional[Any]:
    """請求書を取得する（領収書URL取得・顧客一致確認用）。"""
    _ensure_stripe_configured()
    try:
        return stripe.Invoice.retrieve(invoice_id)
    except stripe.StripeError as e:
        logger.warning("Stripe Invoice retrieve failed: %s", e)
        return None


def get_invoice_receipt_url(invoice_id: str) -> Optional[str]:
    """
    請求書の領収書 URL（Hosted Invoice Page または invoice_pdf）を返す。
    先に Invoice を retrieve して hosted_invoice_url または invoice_pdf を返す。
    """
    inv = retrieve_invoice(invoice_id)
    if not inv:
        return None
    return inv.get("hosted_invoice_url") or inv.get("invoice_pdf")


def get_usage_price_id() -> Optional[str]:
    """従量課金（¥30/質問）用 Price ID。Phase E で使用。"""
    return settings.stripe_price_id_usage_per_question or None


def get_meter_event_name() -> str:
    """従量メーターのイベント名（Stripe ダッシュボードと一致させる）。"""
    return settings.stripe_meter_event_name or "Usage-based"


def report_usage_to_meter(
    stripe_customer_id: str,
    value: int = 1,
    identifier: Optional[str] = None,
    timestamp: Optional[int] = None,
) -> bool:
    """
    Stripe 従量課金メーターに使用量イベントを送信する（Phase E）。
    イベント名は設定（STRIPE_METER_EVENT_NAME、例: Usage-based）と一致させる。

    Args:
        stripe_customer_id: Stripe 顧客 ID（cus_xxx）
        value: 使用量（件数）。1 質問 = 1。
        identifier: 重複防止用の一意 ID（未指定時は UUID を生成）
        timestamp: イベント発生日時（Unix 秒）。未指定時は現在時刻。

    Returns:
        送信成功時 True、未設定・失敗時 False（ログは出力する）
    """
    if not is_stripe_configured():
        return False
    if not stripe_customer_id:
        logger.warning("report_usage_to_meter: stripe_customer_id is empty, skip")
        return False
    event_name = get_meter_event_name()
    identifier_val = identifier or str(uuid.uuid4())
    try:
        # Stripe Python SDK の公開 API（stripe.billing.MeterEvent.create）を優先。
        # 古い SDK（例: 7.x）では billing.MeterEvent が無く AttributeError になるため、httpx でフォールバック。
        try:
            create_params: dict = {
                "event_name": event_name,
                "payload": {"stripe_customer_id": stripe_customer_id, "value": value},
                "identifier": identifier_val,
            }
            if timestamp is not None:
                create_params["timestamp"] = timestamp
            stripe.billing.MeterEvent.create(**create_params)
        except AttributeError:
            _report_usage_to_meter_v1_http(
                event_name=event_name,
                stripe_customer_id=stripe_customer_id,
                value=value,
                identifier=identifier_val,
                timestamp=timestamp,
            )
        logger.debug(
            "Stripe meter event reported: customer=%s value=%s event_name=%s",
            stripe_customer_id,
            value,
            event_name,
        )
        return True
    except stripe.StripeError as e:
        logger.warning(
            "Stripe meter event report failed (customer=%s): %s",
            stripe_customer_id,
            e,
            exc_info=False,
        )
        return False
    except Exception as e:
        logger.warning(
            "Stripe meter event report error (customer=%s): %s",
            stripe_customer_id,
            e,
            exc_info=True,
        )
        return False


def _report_usage_to_meter_v1_http(
    event_name: str,
    stripe_customer_id: str,
    value: int,
    identifier: str,
    timestamp: Optional[int] = None,
) -> None:
    """
    Stripe /v1/billing/meter_events に httpx で POST する（SDK に MeterEvent がない場合のフォールバック）。
    """
    url = "https://api.stripe.com/v1/billing/meter_events"
    auth = (settings.stripe_secret_key, "")
    data: dict = {
        "event_name": event_name,
        "payload[stripe_customer_id]": stripe_customer_id,
        "payload[value]": str(value),
        "identifier": identifier,
    }
    if timestamp is not None:
        data["timestamp"] = str(timestamp)
    with httpx.Client() as client:
        resp = client.post(url, auth=auth, data=data)
        resp.raise_for_status()


def is_stripe_configured() -> bool:
    """Stripe が利用可能かどうか。"""
    return bool(settings.stripe_secret_key)
