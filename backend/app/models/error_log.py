"""
エラーログモデル
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ErrorLog(Base):
    """
    エラーログモデル
    """
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_level = Column(String(20), nullable=False, comment='エラーレベル（error, warning, critical）')
    error_code = Column(String(50), nullable=False, comment='エラーコード（UNAUTHORIZED, INTERNAL_ERROR等）')
    error_message = Column(Text, nullable=False, comment='エラーメッセージ')
    stack_trace = Column(Text, nullable=True, comment='スタックトレース')
    request_path = Column(String(500), nullable=True, comment='リクエストパス')
    request_method = Column(String(10), nullable=True, comment='HTTPメソッド')
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True, index=True, comment='施設ID')
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment='ユーザーID')
    ip_address = Column(INET, nullable=True, comment='IPアドレス')
    user_agent = Column(Text, nullable=True, comment='User-Agent')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, comment='作成日時')

    # リレーションシップ
    facility = relationship("Facility", backref="error_logs")
    user = relationship("User", backref="error_logs")

