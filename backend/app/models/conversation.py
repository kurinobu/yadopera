"""
会話セッションモデル
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Conversation(Base):
    """
    会話セッションモデル
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)  # Cookie保存用（UUID文字列）
    guest_language = Column(String(10), default="en")
    location = Column(String(50))  # 'entrance', 'room', 'kitchen', 'lounge'
    user_agent = Column(Text)
    ip_address = Column(INET)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 24時間判定用
    ended_at = Column(DateTime(timezone=True))
    is_escalated = Column(Boolean, default=False, index=True)
    total_messages = Column(Integer, default=0)
    auto_resolved = Column(Boolean, default=False)

    # リレーションシップ
    facility = relationship("Facility", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="conversation", cascade="all, delete-orphan")
    # session_tokensはsession_idで結合（ForeignKeyではないため、手動で結合）

