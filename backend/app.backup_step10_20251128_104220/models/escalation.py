"""
エスカレーションモデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Escalation(Base):
    """
    エスカレーションモデル
    """
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False, index=True)  # 'low_confidence', 'keyword', 'multiple_turns', 'staff_mode', 'safety_category'
    ai_confidence = Column(DECIMAL(3, 2))  # エスカレーション時の信頼度
    escalation_mode = Column(String(50), default="normal")  # 'normal', 'early'
    notified_at = Column(DateTime(timezone=True))
    notification_channels = Column(ARRAY(String), default=["email"])  # ['email', 'slack', 'line']
    resolved_at = Column(DateTime(timezone=True), index=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    resolution_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="escalations")
    conversation = relationship("Conversation", back_populates="escalations")
    resolver = relationship("User")
    overnight_queue = relationship("OvernightQueue", back_populates="escalation", uselist=False)

