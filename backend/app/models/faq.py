"""
FAQモデル（インテントベース構造）
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class FAQCategory(str, enum.Enum):
    """
    FAQカテゴリEnum
    """
    BASIC = "basic"  # 基本情報
    FACILITIES = "facilities"  # 設備・サービス
    LOCATION = "location"  # 周辺情報
    TROUBLE = "trouble"  # トラブル対応


class FAQ(Base):
    """
    FAQモデル（インテントベース構造）
    
    注意: 言語ごとの質問・回答は`FAQTranslation`モデルに分離されています。
    """
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 'basic', 'facilities', 'location', 'trouble'
    intent_key = Column(String(100), nullable=False)  # インテント識別キー（例: 'basic_checkout_time'）
    priority = Column(Integer, default=1)  # 1-5
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="faqs")
    creator = relationship("User")
    translations = relationship("FAQTranslation", back_populates="faq", cascade="all, delete-orphan")


