"""
FAQ提案モデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class FAQSuggestionStatus(str, enum.Enum):
    """
    FAQ提案ステータスEnum
    """
    PENDING = "pending"  # 承認待ち
    APPROVED = "approved"  # 承認済み（FAQ作成済み）
    REJECTED = "rejected"  # 却下済み


class FAQSuggestion(Base):
    """
    FAQ提案モデル
    """
    __tablename__ = "faq_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    source_message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    suggested_question = Column(Text, nullable=False)
    suggested_answer = Column(Text, nullable=False)
    suggested_category = Column(String(50), nullable=False)  # 'basic', 'facilities', 'location', 'trouble'
    language = Column(String(10), default="en")  # 'en', 'ja', 'zh-TW', 'fr'
    status = Column(String(20), default="pending", index=True)  # 'pending', 'approved', 'rejected'
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_faq_id = Column(Integer, ForeignKey("faqs.id", ondelete="SET NULL"))  # 承認時に作成されたFAQ ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # リレーションシップ
    facility = relationship("Facility", back_populates="faq_suggestions")
    source_message = relationship("Message")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    created_faq = relationship("FAQ", foreign_keys=[created_faq_id])

