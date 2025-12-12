"""
QRコードモデル
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class QRCode(Base):
    """
    QRコードモデル
    生成済みQRコード一覧の永続化用
    """
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)  # 'entrance', 'room', 'kitchen', 'lounge', 'custom'
    custom_location_name = Column(String(50), nullable=True)
    qr_code_url = Column(Text, nullable=False)  # Base64エンコードされたQRコード画像URL
    qr_code_data = Column(Text, nullable=False)  # QRコードに埋め込まれたURL
    format = Column(String(10), nullable=False)  # 'pdf', 'png', 'svg'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="qr_codes")


