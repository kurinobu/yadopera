"""
エスカレーション関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class EscalationResponse(BaseModel):
    """
    エスカレーション情報レスポンス
    """
    id: int
    facility_id: int
    conversation_id: int
    trigger_type: str = Field(..., description="エスカレーション理由（low_confidence/keyword/multiple_turns/staff_mode/safety_category）")
    ai_confidence: Optional[Decimal] = Field(None, description="エスカレーション時の信頼度")
    escalation_mode: str = Field(default="normal", description="エスカレーションモード（normal/early）")
    notified_at: Optional[datetime] = None
    notification_channels: List[str] = Field(default_factory=lambda: ["email"])
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EscalationListResponse(BaseModel):
    """
    エスカレーション一覧レスポンス
    """
    escalations: List[EscalationResponse] = Field(default_factory=list)
    total: int = Field(..., description="総件数")
    unresolved: int = Field(..., description="未解決件数")


class EscalationResolveRequest(BaseModel):
    """
    エスカレーション解決リクエスト
    """
    resolution_notes: Optional[str] = Field(None, description="解決メモ")

    class Config:
        json_schema_extra = {
            "example": {
                "resolution_notes": "ゲストに直接対応し、問題を解決しました。"
            }
        }


class EscalationScheduleCreate(BaseModel):
    """
    エスカレーションスケジュール作成リクエスト
    """
    day_of_week: List[str] = Field(
        ...,
        description="曜日配列（['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']）または['all']で全曜日"
    )
    time_start: str = Field(..., description="開始時間（HH:MM形式）")
    time_end: str = Field(..., description="終了時間（HH:MM形式）")
    mode: str = Field(..., description="エスカレーションモード（normal/early）")
    threshold: Decimal = Field(..., ge=0.0, le=1.0, description="信頼度閾値（0.0-1.0）")
    languages: List[str] = Field(default=["en", "ja"], description="対応言語リスト")
    notify_channels: List[str] = Field(default=["email"], description="通知チャネルリスト（['email', 'slack', 'line']）")
    is_active: bool = Field(default=True, description="有効/無効")

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
                "time_start": "09:00",
                "time_end": "18:00",
                "mode": "early",
                "threshold": 0.85,
                "languages": ["en", "ja"],
                "notify_channels": ["email"],
                "is_active": True
            }
        }


class EscalationScheduleUpdate(BaseModel):
    """
    エスカレーションスケジュール更新リクエスト
    """
    day_of_week: Optional[List[str]] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    mode: Optional[str] = None
    threshold: Optional[Decimal] = Field(None, ge=0.0, le=1.0)
    languages: Optional[List[str]] = None
    notify_channels: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EscalationScheduleResponse(BaseModel):
    """
    エスカレーションスケジュールレスポンス
    """
    id: int
    facility_id: int
    day_of_week: List[str]
    time_start: str
    time_end: str
    mode: str
    threshold: Decimal
    languages: List[str]
    notify_channels: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

