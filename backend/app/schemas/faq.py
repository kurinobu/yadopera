"""
FAQ関連スキーマ（インテントベース構造）
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FAQTranslationRequest(BaseModel):
    """FAQ翻訳作成リクエスト"""
    language: str = Field(..., description="言語コード（en/ja/zh-TW/fr）")
    question: str = Field(..., min_length=1, max_length=500, description="質問文")
    answer: str = Field(..., min_length=1, max_length=2000, description="回答文")


class FAQTranslationResponse(BaseModel):
    """FAQ翻訳レスポンス"""
    id: int = Field(..., description="翻訳ID")
    faq_id: int = Field(..., description="FAQ ID")
    language: str = Field(..., description="言語コード")
    question: str = Field(..., description="質問文")
    answer: str = Field(..., description="回答文")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        from_attributes = True


class FAQRequest(BaseModel):
    """FAQ作成リクエスト（インテントベース構造）"""
    category: str = Field(..., description="カテゴリ（basic/facilities/location/trouble）")
    intent_key: Optional[str] = Field(None, description="インテント識別キー（自動生成される場合は省略可能）")
    translations: List[FAQTranslationRequest] = Field(..., min_items=1, description="翻訳リスト（最低1つの言語が必要）")
    priority: int = Field(default=1, ge=1, le=5, description="優先度（1-5）")
    is_active: Optional[bool] = Field(default=True, description="有効/無効")


class FAQUpdateRequest(BaseModel):
    """FAQ更新リクエスト（インテントベース構造）"""
    category: Optional[str] = Field(None, description="カテゴリ（basic/facilities/location/trouble）")
    intent_key: Optional[str] = Field(None, description="インテント識別キー")
    translations: Optional[List[FAQTranslationRequest]] = Field(None, description="翻訳リスト")
    priority: Optional[int] = Field(None, ge=1, le=5, description="優先度（1-5）")
    is_active: Optional[bool] = Field(None, description="有効/無効")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "basic",
                "intent_key": "basic_checkout_time",
                "translations": [
                    {
                        "language": "en",
                        "question": "What time is check-out?",
                        "answer": "Check-out is by 11:00 AM."
                    },
                    {
                        "language": "ja",
                        "question": "チェックアウトは何時ですか？",
                        "answer": "チェックアウトは11時までです。"
                    }
                ],
                "priority": 5,
                "is_active": True
            }
        }


class FAQResponse(BaseModel):
    """FAQレスポンス（インテントベース構造）"""
    id: int = Field(..., description="FAQ ID")
    facility_id: int = Field(..., description="施設ID")
    category: str = Field(..., description="カテゴリ")
    intent_key: str = Field(..., description="インテント識別キー")
    translations: List[FAQTranslationResponse] = Field(..., description="翻訳リスト")
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
    total: int = Field(..., description="総件数（インテント単位でカウント）")


class BulkFAQCreateResponse(BaseModel):
    """一括FAQ作成レスポンス"""
    created_count: int = Field(..., description="作成されたFAQ数")
    faqs: List[FAQResponse] = Field(default_factory=list, description="作成されたFAQリスト")

