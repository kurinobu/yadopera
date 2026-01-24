"""
FAQ閲覧ログモデル
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FAQViewLog(Base):
    """
    FAQ閲覧ログモデル
    """
    __tablename__ = "faq_view_logs"

    id = Column(Integer, primary_key=True, index=True)
    faq_id = Column(Integer, ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False, index=True, comment='FAQ ID')
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True, comment='施設ID')
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, comment='会話ID')
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, comment='メッセージID')
    guest_language = Column(String(10), nullable=True, comment='ゲスト言語')
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, comment='閲覧日時')

    # リレーションシップ
    faq = relationship("FAQ", backref="view_logs")
    facility = relationship("Facility", backref="faq_view_logs")
    conversation = relationship("Conversation", backref="faq_view_logs")
    message = relationship("Message", backref="faq_view_logs")

