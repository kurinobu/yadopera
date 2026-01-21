"""
宿泊事業者向けヘルプシステム - データベースモデル
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OperatorFaq(Base):
    """
    事業者向けFAQマスターテーブル
    言語非依存の基本情報を管理
    """
    __tablename__ = "operator_faqs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True, comment="カテゴリ（setup, qrcode, faq_management等）")
    intent_key = Column(String(100), nullable=False, unique=True, comment="意図識別キー（ユニーク）")
    display_order = Column(Integer, default=0, index=True, comment="表示順序")
    is_active = Column(Boolean, default=True, index=True, comment="有効フラグ")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    translations = relationship(
        "OperatorFaqTranslation", 
        back_populates="faq", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OperatorFaq(id={self.id}, intent_key={self.intent_key}, category={self.category})>"


class OperatorFaqTranslation(Base):
    """
    FAQ翻訳テーブル
    各言語のQ&A本文を管理
    """
    __tablename__ = "operator_faq_translations"

    id = Column(Integer, primary_key=True, index=True)
    faq_id = Column(Integer, ForeignKey("operator_faqs.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="ja", index=True, comment="言語コード（ja, en）")
    question = Column(Text, nullable=False, comment="質問文")
    answer = Column(Text, nullable=False, comment="回答文")
    keywords = Column(Text, nullable=True, comment="検索キーワード（カンマ区切り）")
    related_url = Column(Text, nullable=True, comment="関連する管理画面URL")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    faq = relationship("OperatorFaq", back_populates="translations")

    # 複合ユニーク制約
    __table_args__ = (
        Index('idx_faq_language', 'faq_id', 'language', unique=True),
    )

    def __repr__(self):
        return f"<OperatorFaqTranslation(id={self.id}, faq_id={self.faq_id}, language={self.language})>"

