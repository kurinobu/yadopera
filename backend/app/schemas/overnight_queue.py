"""
夜間対応キュー関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OvernightQueueResponse(BaseModel):
    """夜間対応キューレスポンス"""
    id: int = Field(..., description="キューID")
    facility_id: int = Field(..., description="施設ID")
    escalation_id: int = Field(..., description="エスカレーションID")
    guest_message: str = Field(..., description="ゲストメッセージ")
    scheduled_notify_at: datetime = Field(..., description="通知予定時刻（翌朝8:00）")
    notified_at: Optional[datetime] = Field(None, description="通知日時")
    resolved_at: Optional[datetime] = Field(None, description="解決日時")
    resolved_by: Optional[int] = Field(None, description="解決者ID")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class OvernightQueueListResponse(BaseModel):
    """夜間対応キュー一覧レスポンス"""
    queues: List[OvernightQueueResponse] = Field(default_factory=list, description="キューリスト")
    total: int = Field(..., description="総件数")
    pending_count: int = Field(..., description="未対応数")
    resolved_count: int = Field(..., description="対応済み数")


class ProcessNotificationsResponse(BaseModel):
    """通知処理レスポンス"""
    processed_count: int = Field(..., description="処理件数")
    total_count: int = Field(..., description="総件数")
