"""
処理済み低評価回答モデル
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProcessedFeedback(Base):
    """
    処理済み低評価回答モデル
    FAQ承認により処理済みとなった低評価回答を記録
    """
    __tablename__ = "processed_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    faq_suggestion_id = Column(Integer, ForeignKey("faq_suggestions.id", ondelete="SET NULL"), nullable=True, index=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # リレーションシップ
    message = relationship("Message")
    facility = relationship("Facility")
    faq_suggestion = relationship("FAQSuggestion")
    processed_by_user = relationship("User", foreign_keys=[processed_by])

    __table_args__ = (
        UniqueConstraint('message_id', 'facility_id', name='uq_processed_feedback_message_facility'),
    )

