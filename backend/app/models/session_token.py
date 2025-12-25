"""
会話引き継ぎコードモデル（v0.3新規）
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SessionToken(Base):
    """
    会話引き継ぎコードモデル
    デバイス間会話引き継ぎ機能用（v0.3新規）
    """
    __tablename__ = "session_tokens"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(10), unique=True, nullable=False, index=True)  # 4桁英数字（例: 'AB12'）
    primary_session_id = Column(String(100), nullable=False, index=True)  # ForeignKeyはマイグレーションで設定
    linked_session_ids = Column(ARRAY(TEXT), default=[])  # 統合されたセッションID配列
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)  # 24時間後

    # リレーションシップ
    facility = relationship("Facility", back_populates="session_tokens")
    # primary_conversationはsession_idで結合（ForeignKeyではないため、手動で結合）

