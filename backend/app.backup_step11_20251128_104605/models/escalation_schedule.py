"""
エスカレーションスケジュールモデル
"""

from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EscalationSchedule(Base):
    """
    エスカレーションスケジュールモデル
    """
    __tablename__ = "escalation_schedules"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(ARRAY(String), nullable=False)  # ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] or ['all']
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    mode = Column(String(50), default="normal")  # 'normal', 'early'
    threshold = Column(DECIMAL(3, 2), default=0.70)  # 0.70 (normal) or 0.85 (early)
    languages = Column(ARRAY(String), default=["en", "ja"])
    notify_channels = Column(ARRAY(String), default=["email"])  # ['email', 'slack', 'line']
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="escalation_schedules")

