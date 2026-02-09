"""
開発者管理ページ関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class DeveloperLoginRequest(BaseModel):
    """
    開発者ログインリクエスト
    """
    password: str = Field(..., min_length=1, description="開発者パスワード")


class DeveloperLoginResponse(BaseModel):
    """
    開発者ログインレスポンス
    """
    access_token: str = Field(..., description="JWTアクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
    expires_in: int = Field(..., description="トークン有効期限（秒）")


class ErrorLogResponse(BaseModel):
    """
    エラーログレスポンス（一覧用）
    """
    id: int
    level: str = Field(..., description="エラーレベル（error, warning, critical）")
    code: str = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    request_path: Optional[str] = None
    facility_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ErrorLogDetailResponse(BaseModel):
    """
    エラーログ詳細レスポンス
    """
    id: int
    level: str
    code: str
    message: str
    stack_trace: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    facility: Optional[dict] = None
    user: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """
    ページネーション情報
    """
    page: int
    per_page: int
    total: int
    total_pages: int


class ErrorLogListResponse(BaseModel):
    """
    エラーログ一覧レスポンス
    """
    errors: List[ErrorLogResponse]
    pagination: PaginationInfo


class Errors24hResponse(BaseModel):
    """
    24時間以内のエラー数
    """
    critical: int = 0
    error: int = 0
    warning: int = 0


class SystemOverviewResponse(BaseModel):
    """
    システム全体概要レスポンス
    """
    total_facilities: int
    active_facilities: int
    total_faqs: int
    errors_24h: Errors24hResponse
    chats_7d: int
    escalations_7d: int


class FacilitySummaryResponse(BaseModel):
    """
    施設サマリーレスポンス
    """
    id: int
    name: str
    is_active: bool
    plan_type: str = "Free"  # Free, Mini, Small, Standard, Premium
    faq_count: int = 0
    chats_7d: int = 0
    errors_7d: int = 0
    last_admin_login: Optional[datetime] = None


class FacilityListResponse(BaseModel):
    """
    施設一覧レスポンス
    """
    facilities: List[FacilitySummaryResponse]


class HealthStatusResponse(BaseModel):
    """
    ヘルスステータスレスポンス
    """
    status: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """
    システムヘルスレスポンス
    """
    database: HealthStatusResponse
    redis: HealthStatusResponse
    openai_api: Optional[HealthStatusResponse] = None
