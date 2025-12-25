"""
夜間対応キュー関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OvernightQueueResponse(BaseModel):
    """
    夜間対応キュー情報レスポンス
    """
    id: int
    facility_id: int
    escalation_id: int
    guest_message: str = Field(..., description="ゲストメッセージ")
    scheduled_notify_at: datetime = Field(..., description="通知予定時刻（翌朝8:00）")
    notified_at: Optional[datetime] = Field(None, description="通知済み時刻")
    resolved_at: Optional[datetime] = Field(None, description="解決済み時刻")
    resolved_by: Optional[int] = Field(None, description="解決者ID")
    created_at: datetime

    class Config:
        from_attributes = True


class OvernightQueueListResponse(BaseModel):
    """
    夜間対応キュー一覧レスポンス
    """
    queues: List[OvernightQueueResponse] = Field(default_factory=list)
    total: int = Field(..., description="総件数")
    unresolved: int = Field(..., description="未解決件数")


class OvernightQueueResolveRequest(BaseModel):
    """
    夜間対応キュー解決リクエスト
    """
    resolution_notes: Optional[str] = Field(None, description="解決メモ")

    class Config:
        json_schema_extra = {
            "example": {
                "resolution_notes": "ゲストに直接対応し、問題を解決しました。"
            }
        }

