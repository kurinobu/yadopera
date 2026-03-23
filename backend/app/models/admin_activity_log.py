"""
管理者アクティビティログモデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AdminActivityLog(Base):
    """
    管理者アクティビティログモデル
    """
    __tablename__ = "admin_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True, comment='ユーザーID')
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=True, index=True, comment='施設ID')
    action_type = Column(String(50), nullable=False, index=True, comment='アクションタイプ（login, faq_create, faq_update, faq_delete等）')
    target_resource_type = Column(String(50), nullable=True, comment='対象リソースタイプ（faq, user, facility等）')
    target_resource_id = Column(Integer, nullable=True, comment='対象リソースID')
    description = Column(Text, nullable=True, comment='説明')
    ip_address = Column(INET, nullable=True, comment='IPアドレス')
    user_agent = Column(Text, nullable=True, comment='User-Agent')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, comment='作成日時')

    # リレーションシップ
    user = relationship("User", backref="admin_activity_logs")
    facility = relationship("Facility", backref="admin_activity_logs")

