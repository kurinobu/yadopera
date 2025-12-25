"""
夜間対応キューモデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OvernightQueue(Base):
    """
    夜間対応キューモデル
    """
    __tablename__ = "overnight_queue"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    escalation_id = Column(Integer, ForeignKey("escalations.id", ondelete="CASCADE"), nullable=False)
    guest_message = Column(Text, nullable=False)
    scheduled_notify_at = Column(DateTime(timezone=True), nullable=False, index=True)  # 翌朝8:00
    notified_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True), index=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="overnight_queues")
    escalation = relationship("Escalation", back_populates="overnight_queue")
    resolver = relationship("User")

