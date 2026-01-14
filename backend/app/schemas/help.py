"""
ヘルプシステム用Pydanticスキーマ
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FaqResponse(BaseModel):
    """FAQ単体レスポンス"""
    id: int
    category: str
    question: str
    answer: str
    keywords: Optional[str] = None
    related_url: Optional[str] = None
    display_order: int


class FaqListResponse(BaseModel):
    """FAQ一覧レスポンス"""
    faqs: List[FaqResponse]
    total: int
    categories: List[str]


class FaqSearchResponse(BaseModel):
    """FAQ検索レスポンス"""
    results: List[FaqResponse]
    total: int
    query: str


class RelatedFaq(BaseModel):
    """関連FAQ"""
    id: int
    question: str
    category: str


class ChatRequest(BaseModel):
    """チャットリクエスト"""
    message: str = Field(..., min_length=1, max_length=500, description="ユーザーメッセージ")
    language: str = Field(default='ja', pattern='^(ja|en)$', description="言語コード")


class ChatResponse(BaseModel):
    """チャットレスポンス"""
    response: str = Field(..., description="AI回答")
    related_faqs: List[int] = Field(default_factory=list, description="関連FAQ IDリスト")
    related_url: Optional[str] = Field(None, description="関連URL")
    timestamp: str = Field(..., description="タイムスタンプ")

