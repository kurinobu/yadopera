"""
チャット関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class EscalationInfo(BaseModel):
    """
    エスカレーション情報
    """
    needed: bool = Field(..., description="エスカレーションが必要か")
    mode: Optional[str] = Field(None, description="エスカレーションモード（normal/early）")
    trigger_type: Optional[str] = Field(None, description="エスカレーション理由（low_confidence/keyword/multiple_turns）")
    reason: Optional[str] = Field(None, description="エスカレーション理由の詳細")
    notified: Optional[bool] = Field(None, description="通知済みか")


class ChatRequest(BaseModel):
    """
    チャットメッセージ送信リクエスト
    """
    facility_id: int = Field(..., description="施設ID")
    message: str = Field(..., min_length=1, max_length=1000, description="メッセージ内容")
    language: str = Field(default="en", description="言語コード")
    location: Optional[str] = Field(None, description="QRコード設置場所（entrance/room/kitchen/lounge）")
    session_id: Optional[str] = Field(None, description="既存セッションID（オプション）")


class MessageResponse(BaseModel):
    """
    メッセージレスポンス
    """
    id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    ai_confidence: Optional[Decimal] = None
    matched_faq_ids: Optional[List[int]] = None
    response_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RAGEngineResponse(BaseModel):
    """
    RAGエンジンのレスポンス（中間形式）
    メッセージ保存前の情報を返す
    """
    response: str = Field(..., description="AI応答テキスト")
    ai_confidence: Decimal = Field(..., description="AI信頼度（0.0-1.0）")
    matched_faq_ids: List[int] = Field(default_factory=list, description="マッチしたFAQ IDリスト")
    response_time_ms: int = Field(..., description="応答時間（ミリ秒）")
    escalation: EscalationInfo = Field(..., description="エスカレーション情報")


class ChatResponse(BaseModel):
    """
    チャットレスポンス
    """
    message: MessageResponse = Field(..., description="AI応答メッセージ")
    session_id: str = Field(..., description="セッションID")
    ai_confidence: Optional[Decimal] = Field(None, description="AI信頼度（0.0-1.0）")
    is_escalated: bool = Field(..., description="エスカレーションが必要か")
    escalation_id: Optional[int] = Field(None, description="エスカレーションID")
    escalation: EscalationInfo = Field(..., description="エスカレーション情報")


class ChatHistoryResponse(BaseModel):
    """
    会話履歴レスポンス
    """
    session_id: str
    facility_id: int
    language: str
    location: Optional[str] = None
    started_at: datetime
    last_activity_at: datetime
    messages: List[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    """
    フィードバック送信リクエスト
    """
    message_id: int = Field(..., description="メッセージID")
    feedback_type: str = Field(..., description="フィードバックタイプ（positive/negative）")

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 123,
                "feedback_type": "positive"
            }
        }


class FeedbackResponse(BaseModel):
    """
    フィードバック送信レスポンス
    """
    id: int = Field(..., description="フィードバックID")
    message_id: int = Field(..., description="メッセージID")
    feedback_type: str = Field(..., description="フィードバックタイプ（positive/negative）")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class EscalationRequest(BaseModel):
    """
    エスカレーションリクエスト（ゲスト側）
    """
    facility_id: int = Field(..., description="施設ID")
    session_id: str = Field(..., description="セッションID")

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": 1,
                "session_id": "abc123-def456-ghi789"
            }
        }


class EscalationResponse(BaseModel):
    """
    エスカレーションレスポンス（ゲスト側）
    """
    success: bool = Field(..., description="エスカレーション作成成功")
    escalation_id: int = Field(..., description="エスカレーションID")
    message: str = Field(..., description="メッセージ")

