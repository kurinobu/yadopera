"""
質問パターン解決率モデル
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class QuestionPattern(Base):
    """
    質問パターン解決率モデル
    """
    __tablename__ = "question_patterns"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_embedding = Column(Vector(1536), nullable=False)  # 質問パターンの埋め込みベクトル
    total_count = Column(Integer, default=0)
    resolved_count = Column(Integer, default=0)  # エスカレーションなしで完了した回数
    # resolution_rateはGENERATED ALWAYS ASで計算されるため、マイグレーションで定義
    # ここでは型のみ定義（実際の計算はデータベース側で行う）
    resolution_rate = Column(DECIMAL(3, 2), index=True)
    last_asked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    facility = relationship("Facility", back_populates="question_patterns")

