"""
リード（クーポン取得）モデル
決済なしリード獲得機能: ゲスト名・メールアドレスを施設に紐付けて保存
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class GuestLead(Base):
    """
    ゲストリードモデル（クーポンエントリーで取得したメールアドレス等）
    """
    __tablename__ = "guest_leads"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    coupon_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # リレーションシップ
    facility = relationship("Facility", back_populates="guest_leads")
