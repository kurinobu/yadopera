"""
広告モデル（Freeプラン ゲスト画面固定フッター用）
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Ad(Base):
    """
    広告マスタ（アフィリエイトリンク等）
    Freeプラン施設のゲスト画面でのみ表示。
    """
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # 表示用タイトル
    description = Column(Text, nullable=True)     # 説明（任意）
    url = Column(String(500), nullable=True)      # 正規URL（表示用）
    affiliate_url = Column(Text, nullable=False)  # アフィリエイトリンク先URL
    priority = Column(Integer, default=0, nullable=False)  # 表示順（昇順）
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
