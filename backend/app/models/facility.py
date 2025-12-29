"""
施設モデル
"""

from datetime import time
from sqlalchemy import Column, Integer, String, Text, Time, ARRAY, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Facility(Base):
    """
    宿泊施設モデル
    """
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # URL用識別子
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    wifi_ssid = Column(String(100))
    wifi_password = Column(String(100))  # 暗号化保存
    check_in_time = Column(Time, default=time(15, 0))
    check_out_time = Column(Time, default=time(11, 0))
    house_rules = Column(Text)
    local_info = Column(Text)
    languages = Column(ARRAY(String), default=["en"])
    timezone = Column(String(50), default="Asia/Tokyo")
    subscription_plan = Column(String(50), default="small")  # 'free', 'mini', 'small', 'standard', 'premium'
    monthly_question_limit = Column(Integer, default=200)
    staff_absence_periods = Column(JSON, default=[])  # スタッフ不在時間帯（JSON配列）
    icon_url = Column(String(255), nullable=True)  # アイコンURL（Phase 1では任意）
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    users = relationship("User", back_populates="facility", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="facility", cascade="all, delete-orphan")
    session_tokens = relationship("SessionToken", back_populates="facility", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="facility", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="facility", cascade="all, delete-orphan")
    escalation_schedules = relationship("EscalationSchedule", back_populates="facility", cascade="all, delete-orphan")
    overnight_queues = relationship("OvernightQueue", back_populates="facility", cascade="all, delete-orphan")
    question_patterns = relationship("QuestionPattern", back_populates="facility", cascade="all, delete-orphan")
    guest_feedbacks = relationship("GuestFeedback", back_populates="facility", cascade="all, delete-orphan")
    faq_suggestions = relationship("FAQSuggestion", back_populates="facility", cascade="all, delete-orphan")
    qr_codes = relationship("QRCode", back_populates="facility", cascade="all, delete-orphan")

