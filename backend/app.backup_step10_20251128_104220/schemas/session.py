"""
セッション統合トークン関連スキーマ（v0.3新規）
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SessionLinkRequest(BaseModel):
    """
    セッション統合リクエスト
    """
    facility_id: int = Field(..., description="施設ID")
    token: str = Field(..., min_length=4, max_length=10, description="セッション統合トークン（4桁英数字）")
    current_session_id: str = Field(..., description="現在のセッションID")


class SessionLinkResponse(BaseModel):
    """
    セッション統合レスポンス
    """
    success: bool = Field(..., description="統合成功か")
    message: str = Field(..., description="メッセージ")
    primary_session_id: str = Field(..., description="プライマリセッションID")
    linked_session_ids: List[str] = Field(default_factory=list, description="統合されたセッションIDリスト")


class SessionTokenResponse(BaseModel):
    """
    セッション統合トークン情報レスポンス
    """
    token: str = Field(..., description="トークン（4桁英数字）")
    primary_session_id: str = Field(..., description="プライマリセッションID")
    linked_session_ids: List[str] = Field(default_factory=list, description="統合されたセッションIDリスト")
    expires_at: datetime = Field(..., description="有効期限")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class SessionTokenVerifyResponse(BaseModel):
    """
    セッション統合トークン検証レスポンス
    """
    valid: bool = Field(..., description="トークンが有効か")
    token: Optional[str] = Field(None, description="トークン")
    primary_session_id: Optional[str] = Field(None, description="プライマリセッションID")
    linked_session_ids: Optional[List[str]] = Field(None, description="統合されたセッションIDリスト")
    expires_at: Optional[datetime] = Field(None, description="有効期限")
    message: Optional[str] = Field(None, description="メッセージ（無効な場合の理由など）")

