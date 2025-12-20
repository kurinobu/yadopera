"""
FAQ提案関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FAQSuggestionResponse(BaseModel):
    """FAQ提案レスポンス"""
    id: int = Field(..., description="提案ID")
    facility_id: int = Field(..., description="施設ID")
    source_message_id: int = Field(..., description="元メッセージID")
    suggested_question: str = Field(..., description="提案質問文")
    suggested_answer: str = Field(..., description="提案回答文")
    suggested_category: str = Field(..., description="提案カテゴリ")
    language: str = Field(..., description="言語コード")
    status: str = Field(..., description="ステータス（pending/approved/rejected）")
    reviewed_at: Optional[datetime] = Field(None, description="レビュー日時")
    reviewed_by: Optional[int] = Field(None, description="レビュー者ID")
    created_faq_id: Optional[int] = Field(None, description="作成されたFAQ ID")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class ApproveSuggestionRequest(BaseModel):
    """提案承認リクエスト（編集可能）"""
    question: Optional[str] = Field(None, min_length=1, max_length=500, description="質問文（編集可能）")
    answer: Optional[str] = Field(None, min_length=1, max_length=2000, description="回答文（編集可能）")
    category: Optional[str] = Field(None, description="カテゴリ（編集可能）")
    priority: int = Field(default=1, ge=1, le=5, description="優先度（1-5）")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What time is check-out?",
                "answer": "Check-out is by 11:00 AM.",
                "category": "basic",
                "priority": 5
            }
        }


class FAQSuggestionListResponse(BaseModel):
    """FAQ提案一覧レスポンス"""
    suggestions: list[FAQSuggestionResponse] = Field(default_factory=list, description="提案リスト")
    total: int = Field(..., description="総件数")


