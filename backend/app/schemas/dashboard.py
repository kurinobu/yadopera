"""
ダッシュボード関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CategoryBreakdown(BaseModel):
    """カテゴリ別内訳"""
    basic: int = Field(default=0, description="基本情報")
    facilities: int = Field(default=0, description="設備・サービス")
    location: int = Field(default=0, description="周辺情報")
    trouble: int = Field(default=0, description="トラブル対応")


class TopQuestion(BaseModel):
    """TOP質問"""
    question: str = Field(..., description="質問内容")
    count: int = Field(..., description="質問回数")


class WeeklySummary(BaseModel):
    """週次サマリー"""
    period: dict = Field(..., description="期間（start, end）")
    total_questions: int = Field(..., description="総質問数")
    auto_response_rate: Decimal = Field(..., description="自動応答率（0.0-1.0）")
    average_response_time_ms: int = Field(..., description="平均レスポンス時間（ミリ秒）")
    average_confidence: Decimal = Field(..., description="平均信頼度（0.0-1.0）")
    category_breakdown: CategoryBreakdown = Field(..., description="カテゴリ別内訳")
    top_questions: List[TopQuestion] = Field(default_factory=list, description="TOP5質問")
    unresolved_count: int = Field(..., description="未解決数")


class ChatHistory(BaseModel):
    """リアルタイムチャット履歴"""
    session_id: str = Field(..., description="セッションID")
    guest_language: str = Field(..., description="ゲスト言語")
    last_message: str = Field(..., description="最後のメッセージ")
    ai_confidence: Optional[Decimal] = Field(None, description="AI信頼度（0.0-1.0）")
    created_at: datetime = Field(..., description="作成日時")


class OvernightQueueItem(BaseModel):
    """夜間対応キュー項目"""
    id: int = Field(..., description="キューID")
    facility_id: int = Field(..., description="施設ID")
    escalation_id: int = Field(..., description="エスカレーションID")
    guest_message: str = Field(..., description="ゲストメッセージ")
    language: str = Field(..., description="言語")
    scheduled_notify_at: datetime = Field(..., description="通知予定時刻（翌朝8:00）")
    notified_at: Optional[datetime] = Field(None, description="通知日時")
    resolved_at: Optional[datetime] = Field(None, description="解決日時")
    resolved_by: Optional[int] = Field(None, description="解決者ID")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class LowRatedAnswer(BaseModel):
    """低評価回答"""
    message_id: int = Field(..., description="メッセージID")
    question: str = Field(..., description="質問内容")
    answer: str = Field(..., description="回答内容")
    negative_count: int = Field(..., description="低評価数（2回以上）")


class FeedbackStats(BaseModel):
    """ゲストフィードバック統計"""
    positive_count: int = Field(..., description="肯定評価数")
    negative_count: int = Field(..., description="否定評価数")
    positive_rate: Decimal = Field(..., description="肯定率（0.0-1.0）")
    low_rated_answers: List[LowRatedAnswer] = Field(default_factory=list, description="低評価回答リスト（2回以上）")


class DashboardResponse(BaseModel):
    """ダッシュボードレスポンス"""
    summary: WeeklySummary = Field(..., description="週次サマリー")
    recent_conversations: List[ChatHistory] = Field(default_factory=list, description="リアルタイムチャット履歴（最新10件）")
    overnight_queue: List[OvernightQueueItem] = Field(default_factory=list, description="夜間対応キュー")
    feedback_stats: FeedbackStats = Field(..., description="ゲストフィードバック統計")


