"""
広告API用スキーマ（Freeプラン ゲスト画面固定フッター用）
"""

from pydantic import BaseModel, Field
from typing import Optional


class AdItem(BaseModel):
    """広告1件（ゲスト向け返却用）"""
    id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    affiliate_url: str
    priority: int = 0

    class Config:
        from_attributes = True


class AdListResponse(BaseModel):
    """広告一覧レスポンス（Freeプラン時のみ要素あり）"""
    ads: list[AdItem] = Field(default_factory=list, description="広告一覧（active かつ priority 昇順）")
