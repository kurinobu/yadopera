"""
メッセージモデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MessageRole(str, enum.Enum):
    """
    メッセージロールEnum
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """
    メッセージモデル
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    ai_confidence = Column(DECIMAL(3, 2))  # 0.00-1.00（条件付きインデックスはマイグレーションで設定）
    matched_faq_ids = Column(ARRAY(Integer))  # 使用したFAQ IDリスト
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # リレーションシップ
    conversation = relationship("Conversation", back_populates="messages")
    guest_feedbacks = relationship("GuestFeedback", back_populates="message", cascade="all, delete-orphan")

