"""
施設関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


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
    top_questions: List[str] = Field(default_factory=list, description="よくある質問TOP3")

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
    subscription_plan: str = "small"
    monthly_question_limit: int = 200
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

