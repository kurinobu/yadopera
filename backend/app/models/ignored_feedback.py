"""
無視された低評価回答モデル
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class IgnoredFeedback(Base):
    """
    無視された低評価回答モデル
    管理者が無視した低評価回答を記録
    """
    __tablename__ = "ignored_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    ignored_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ignored_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # リレーションシップ
    message = relationship("Message")
    facility = relationship("Facility")
    ignored_by_user = relationship("User", foreign_keys=[ignored_by])

    __table_args__ = (
        UniqueConstraint('message_id', 'facility_id', name='uq_ignored_feedback_message_facility'),
    )

