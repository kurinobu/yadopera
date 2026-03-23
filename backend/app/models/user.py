"""
ユーザーモデル
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    管理者ユーザーモデル
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt
    role = Column(String(50), default="staff")  # 'owner', 'staff', 'admin'
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # メールアドレス確認関連（★追加）
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), index=True)
    verification_token_expires = Column(DateTime(timezone=True))
    
    last_login_at = Column(DateTime(timezone=True))
    password_reset_token = Column(String(255), index=True)  # 条件付きインデックス（WHERE句はマイグレーションで設定）
    password_reset_expires = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="users")


