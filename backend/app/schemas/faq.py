"""
FAQ関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FAQRequest(BaseModel):
    """FAQ作成リクエスト"""
    category: str = Field(..., description="カテゴリ（basic/facilities/location/trouble）")
    language: str = Field(default="en", description="言語コード")
    question: str = Field(..., min_length=1, max_length=500, description="質問文")
    answer: str = Field(..., min_length=1, max_length=2000, description="回答文")
    priority: int = Field(default=1, ge=1, le=5, description="優先度（1-5）")
    is_active: Optional[bool] = Field(default=True, description="有効/無効")


class FAQUpdateRequest(BaseModel):
    """FAQ更新リクエスト"""
    category: Optional[str] = Field(None, description="カテゴリ（basic/facilities/location/trouble）")
    language: Optional[str] = Field(None, description="言語コード")
    question: Optional[str] = Field(None, min_length=1, max_length=500, description="質問文")
    answer: Optional[str] = Field(None, min_length=1, max_length=2000, description="回答文")
    priority: Optional[int] = Field(None, ge=1, le=5, description="優先度（1-5）")
    is_active: Optional[bool] = Field(None, description="有効/無効")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "basic",
                "language": "en",
                "question": "What time is check-in?",
                "answer": "Check-in is from 3pm to 10pm.",
                "priority": 5,
                "is_active": True
            }
        }


class FAQResponse(BaseModel):
    """FAQレスポンス"""
    id: int = Field(..., description="FAQ ID")
    facility_id: int = Field(..., description="施設ID")
    category: str = Field(..., description="カテゴリ")
    language: str = Field(..., description="言語コード")
    question: str = Field(..., description="質問文")
    answer: str = Field(..., description="回答文")
    priority: int = Field(..., description="優先度（1-5）")
    is_active: bool = Field(..., description="有効/無効")
    created_by: Optional[int] = Field(None, description="作成者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True


class FAQListResponse(BaseModel):
    """FAQ一覧レスポンス"""
    faqs: list[FAQResponse] = Field(default_factory=list, description="FAQリスト")
    total: int = Field(..., description="総件数")

