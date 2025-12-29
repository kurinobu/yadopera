"""
施設関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class TopQuestion(BaseModel):
    """
    よくある質問TOP3の項目
    """
    id: int
    question: str
    answer: str
    category: str


class FacilityPublicResponse(BaseModel):
    """
    施設情報公開レスポンス（ゲスト側用）
    """
    id: int
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    check_in_time: Optional[str] = None  # "15:00"形式
    check_out_time: Optional[str] = None  # "11:00"形式
    wifi_ssid: Optional[str] = None
    top_questions: List[TopQuestion] = Field(default_factory=list, description="よくある質問TOP3")

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
    languages: List[str] = Field(default_factory=list)
    timezone: str = "Asia/Tokyo"
    subscription_plan: Literal["free", "mini", "small", "standard", "premium"] = "small"
    monthly_question_limit: int = 200
    is_active: bool = True
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
    house_rules: Optional[str] = Field(None, max_length=1000, description="館内ルール（1000文字以内）")
    local_info: Optional[str] = Field(None, max_length=1000, description="周辺情報（1000文字以内）")
    staff_absence_periods: Optional[List[StaffAbsencePeriod]] = None

