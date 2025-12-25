"""
ゲストフィードバックモデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GuestFeedback(Base):
    """
    ゲストフィードバックモデル
    """
    __tablename__ = "guest_feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_type = Column(String(10), nullable=False, index=True)  # 'positive', 'negative'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # リレーションシップ
    message = relationship("Message", back_populates="guest_feedbacks")
    facility = relationship("Facility", back_populates="guest_feedbacks")


