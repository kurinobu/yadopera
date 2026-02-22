"""
リード（クーポン取得）関連スキーマ
決済なしリード獲得: ゲスト名・メールアドレスエントリー
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class LeadEntryRequest(BaseModel):
    """
    リードエントリーリクエスト（ゲストがクーポン取得時に送信）
    """
    guest_name: Optional[str] = Field(None, max_length=255)
    email: EmailStr = Field(..., description="送付先メールアドレス")


class LeadEntryResponse(BaseModel):
    """
    リードエントリー成功レスポンス
    """
    success: bool = True
    message: str = Field(default="クーポンを送信しました。")


class LeadListItem(BaseModel):
    """
    リード一覧の1件
    """
    id: int
    facility_id: int
    guest_name: Optional[str] = None
    email: str
    coupon_sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """
    リード一覧レスポンス（管理画面用）
    """
    leads: List[LeadListItem] = Field(default_factory=list)
    total: int = 0
