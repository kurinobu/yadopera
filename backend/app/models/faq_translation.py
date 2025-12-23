"""
FAQ翻訳モデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class FAQTranslation(Base):
    """
    FAQ翻訳モデル（言語ごとの質問・回答・埋め込みベクトル）
    
    同じFAQ（インテント）の複数言語版を保存します。
    """
    __tablename__ = "faq_translations"

    id = Column(Integer, primary_key=True, index=True)
    faq_id = Column(Integer, ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="en")  # 'en', 'ja', 'zh-TW', 'fr'
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    faq = relationship("FAQ", back_populates="translations")

