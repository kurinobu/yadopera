"""
施設関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# プラン超過時の挙動（管理者選択制）
OverageBehaviorLiteral = Literal["continue_billing", "faq_only"]


class TopQuestion(BaseModel):
    """
    よくある質問TOP3の項目
    """
    id: int
    question: str
    answer: str
    category: str


class CouponPublic(BaseModel):
    """
    クーポン設定（公開用・クーポン有効時のみ返す）
    """
    enabled: bool = True
    discount_percent: int = Field(..., ge=1, le=100)
    description: Optional[str] = None
    validity_months: Optional[int] = Field(None, ge=1, le=24)


class FacilityPublicResponse(BaseModel):
    """
    施設情報公開レスポンス（ゲスト側用）
    """
    id: int
    name: str
    slug: str
    email: Optional[str] = None  # show_email_on_guest_screen が False のときは null
    phone: Optional[str] = None
    check_in_time: Optional[str] = None  # "15:00"形式
    check_out_time: Optional[str] = None  # "11:00"形式
    wifi_ssid: Optional[str] = None
    top_questions: List[TopQuestion] = Field(default_factory=list, description="よくある質問TOP3")
    plan_type: Optional[str] = Field(None, description="料金プラン（Free, Mini, Small, Standard, Premium）")
    available_languages: List[str] = Field(default_factory=list, description="利用可能言語リスト")
    coupon: Optional[CouponPublic] = Field(None, description="クーポン有効時のみ設定")

    class Config:
        from_attributes = True


class FacilityResponse(BaseModel):
    """
    施設情報レスポンス（管理側用）
    """
    id: int
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    wifi_ssid: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    house_rules: Optional[str] = None
    local_info: Optional[str] = None
    prohibited_items: Optional[str] = None
    # 互換目的の旧フィールド。管理画面の表示ロジックは allowed_faq_languages を正として扱う。
    languages: List[str] = Field(default_factory=list, description="(legacy) 施設の保存言語設定")
    # プラン制限に基づく正規化済みのFAQ対応言語（管理画面表示の単一ソース）
    allowed_faq_languages: List[str] = Field(default_factory=list, description="プランに基づくFAQ対応言語")
    timezone: str = "Asia/Tokyo"
    subscription_plan: Literal["free", "mini", "small", "standard", "premium"] = "small"
    plan_type: Optional[str] = Field(None, description="料金プラン表示用（Free, Mini, Small, Standard, Premium）")
    monthly_question_limit: int = 200
    is_active: bool = True
    coupon_enabled: bool = False
    coupon_discount_percent: Optional[int] = Field(None, ge=1, le=100)
    coupon_description: Optional[str] = None
    coupon_validity_months: Optional[int] = Field(None, ge=1, le=24)
    official_website_url: Optional[str] = Field(None, max_length=500, description="公式サイトURL（クーポン送付メールで案内）")
    show_email_on_guest_screen: bool = True
    overage_behavior: str = Field(
        default="continue_billing",
        description="プラン超過時の挙動（continue_billing=従量課金継続, faq_only=AI停止・FAQ限定）",
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StaffAbsencePeriod(BaseModel):
    """
    スタッフ不在時間帯
    """
    start_time: str = Field(..., description="開始時刻（HH:MM形式）")
    end_time: str = Field(..., description="終了時刻（HH:MM形式）")
    days_of_week: List[str] = Field(..., description="曜日（['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']）")


class FacilitySettingsResponse(BaseModel):
    """
    施設設定レスポンス
    """
    facility: FacilityResponse
    staff_absence_periods: List[StaffAbsencePeriod] = Field(default_factory=list)
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class FacilitySettingsUpdateRequest(BaseModel):
    """
    施設設定更新リクエスト
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    wifi_ssid: Optional[str] = Field(None, max_length=100)
    wifi_password: Optional[str] = Field(None, max_length=100, description="変更時のみ")
    check_in_time: Optional[str] = Field(None, description="時刻形式（HH:MM）")
    check_out_time: Optional[str] = Field(None, description="時刻形式（HH:MM）")
    house_rules: Optional[str] = Field(None, max_length=500, description="館内ルール（500文字以内）")
    local_info: Optional[str] = Field(None, max_length=500, description="周辺情報（500文字以内）")
    prohibited_items: Optional[str] = Field(None, max_length=500, description="禁止事項（500文字以内）")
    staff_absence_periods: Optional[List[StaffAbsencePeriod]] = None
    # クーポン（リードゲット）設定
    coupon_enabled: Optional[bool] = None
    coupon_discount_percent: Optional[int] = Field(None, ge=1, le=100)
    coupon_description: Optional[str] = Field(None, max_length=500)
    coupon_validity_months: Optional[int] = Field(None, ge=1, le=24)
    official_website_url: Optional[str] = Field(None, max_length=500, description="公式サイトURL（任意）")
    show_email_on_guest_screen: Optional[bool] = None
    overage_behavior: Optional[OverageBehaviorLiteral] = Field(
        None,
        description="プラン超過時の挙動（continue_billing | faq_only）",
    )

