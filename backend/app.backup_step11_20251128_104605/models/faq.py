"""
FAQモデル
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
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
    FAQモデル（埋め込みベクトル含む）
    """
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 'basic', 'facilities', 'location', 'trouble'
    language = Column(String(10), default="en")  # 'en', 'ja', 'zh-TW', 'fr'
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small
    priority = Column(Integer, default=1)  # 1-5
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="faqs")
    creator = relationship("User")

