"""
プラン・請求・解約 API 用スキーマ（Phase 4 Phase C）
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# 料金表示用（要約定義書 0.6 に準拠）
PLAN_DISPLAY = {
    "Free": {"name_ja": "Free", "price_yen": 0},
    "Mini": {"name_ja": "Mini", "price_yen": 1980},
    "Small": {"name_ja": "Small", "price_yen": 3980},
    "Standard": {"name_ja": "Standard", "price_yen": 5980},
    "Premium": {"name_ja": "Premium", "price_yen": 7980},
}


class PlanInfo(BaseModel):
    """プラン一覧用の1件"""
    plan_type: str = Field(..., description="プラン種別（Free, Mini, Small, Standard, Premium）")
    name_ja: str = Field(..., description="表示名")
    price_yen: int = Field(..., description="月額（円）。Free は 0")
    monthly_question_limit: Optional[int] = Field(None, description="月間質問数上限（None=従量/無制限）")
    faq_limit: Optional[int] = Field(None, description="FAQ登録数上限（None=無制限）")
    language_limit: Optional[int] = Field(None, description="同時利用言語数上限（None=無制限）")


class PlansResponse(BaseModel):
    """GET /admin/plans のレスポンス"""
    current_plan_type: str = Field(..., description="現在のプラン")
    plans: List[PlanInfo] = Field(..., description="変更可能なプラン一覧")
    stripe_configured: bool = Field(False, description="Stripe が利用可能か（プラン変更・解約が可能か）")
    current_overage_behavior: Optional[str] = Field(
        None,
        description="現在のプラン超過時挙動（continue_billing | faq_only）",
    )


class PlanChangeRequest(BaseModel):
    """POST /admin/plans/change のリクエスト"""
    target_plan_type: str = Field(..., description="変更先プラン（Free, Mini, Small, Standard, Premium）")


class PlanChangeResponse(BaseModel):
    """POST /admin/plans/change のレスポンス"""
    plan_type: str = Field(..., description="変更後のプラン")
    message: str = Field(..., description="完了メッセージ")


class SubscriptionCancelRequest(BaseModel):
    """POST /admin/subscription/cancel のリクエスト"""
    at_period_end: bool = Field(True, description="True=期間末解約, False=即時解約")


class SubscriptionCancelResponse(BaseModel):
    """POST /admin/subscription/cancel のレスポンス"""
    message: str = Field(..., description="完了メッセージ")


class InvoiceItemResponse(BaseModel):
    """請求書1件（一覧用）"""
    id: str = Field(..., description="Stripe Invoice ID")
    amount_due: int = Field(0, description="請求額（セント）。0の場合は0")
    status: Optional[str] = Field(None, description="draft, open, paid, uncollectible, void 等")
    created: Optional[int] = Field(None, description="作成日時（Unix タイムスタンプ）")
    hosted_invoice_url: Optional[str] = Field(None, description="領収書ページURL（あれば）")


class InvoicesResponse(BaseModel):
    """GET /admin/invoices のレスポンス"""
    invoices: List[InvoiceItemResponse] = Field(default_factory=list)


class ReceiptResponse(BaseModel):
    """GET /admin/invoices/{invoice_id}/receipt のレスポンス"""
    url: str = Field(..., description="領収書・PDF の URL")
