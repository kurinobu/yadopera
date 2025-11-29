"""
エスカレーション判定・管理サービス
"""

import logging
from typing import Optional
from datetime import datetime, time
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pytz
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.escalation import Escalation
from app.models.escalation_schedule import EscalationSchedule
from app.schemas.chat import EscalationInfo
from app.ai.safety_check import check_safety_category

logger = logging.getLogger(__name__)


class EscalationService:
    """
    エスカレーション管理サービス（v0.3詳細化）
    """
    
    # 緊急キーワードリスト
    EMERGENCY_KEYWORDS = [
        "emergency", "help", "urgent", "locked out", 
        "lost key", "sick", "injured", "fire", "police",
        "accident", "medical", "hospital"
    ]
    
    async def check_escalation_needed(
        self,
        facility_id: int,
        confidence: Decimal,
        message: str,
        session_id: str,
        language: str,
        conversation_id: int,
        db: AsyncSession
    ) -> EscalationInfo:
        """
        エスカレーション必要か判定（v0.3改善）
        - 施設のタイムゾーン基準で時刻判定
        - 安全カテゴリは即エスカレ★新規
        
        Args:
            facility_id: 施設ID
            confidence: AI信頼度スコア（0.0-1.0）
            message: ゲストのメッセージ
            session_id: セッションID
            language: 言語コード
            conversation_id: 会話ID
            db: データベースセッション
        
        Returns:
            EscalationInfo: エスカレーション情報
        """
        # Step 0: 安全カテゴリ判定（v0.3新規） - 即エスカレーション
        if check_safety_category(message):
            trigger_type = "safety_category"
            reason = "Safety category detected (medical/safety keywords)"
            # 安全カテゴリは即座にエスカレーション
            escalation = await self.create_escalation(
                facility_id=facility_id,
                conversation_id=conversation_id,
                trigger_type=trigger_type,
                ai_confidence=float(confidence),
                escalation_mode="normal",
                notification_channels=["email"],
                db=db
            )
            return EscalationInfo(
                needed=True,
                mode="normal",
                trigger_type=trigger_type,
                reason=reason,
                notified=escalation.notified_at is not None
            )
        
        # 施設のタイムゾーンを取得
        facility = await db.get(Facility, facility_id)
        timezone_str = facility.timezone if facility else 'Asia/Tokyo'
        
        # UTC → 施設のタイムゾーンに変換（v0.3改善）
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        facility_tz = pytz.timezone(timezone_str)
        local_now = utc_now.astimezone(facility_tz)
        
        current_time = local_now.time()
        current_weekday = local_now.strftime("%a").lower()  # 'mon', 'tue', etc.
        
        # エスカレーションスケジュール検索
        schedule = await self.get_escalation_schedule(
            facility_id=facility_id,
            weekday=current_weekday,
            current_time=current_time,
            language=language,
            db=db
        )
        
        # 閾値決定
        if schedule:
            threshold = float(schedule.threshold)
            mode = schedule.mode
            notify_channels = schedule.notify_channels
        else:
            threshold = 0.7  # デフォルト
            mode = "normal"
            notify_channels = ["email"]
        
        # 判定1: 信頼度 < 閾値
        if float(confidence) < threshold:
            trigger_type = "low_confidence"
            reason = f"AI confidence below threshold ({float(confidence):.2f} < {threshold})"
        
        # 判定2: 緊急キーワード検出
        elif self._detect_emergency_keywords(message):
            trigger_type = "keyword"
            reason = "Emergency keyword detected in message"
            # 緊急時は即座に通知
            escalation = await self.create_escalation(
                facility_id=facility_id,
                conversation_id=conversation_id,
                trigger_type=trigger_type,
                ai_confidence=float(confidence),
                escalation_mode=mode,
                notification_channels=notify_channels,
                db=db
            )
            return EscalationInfo(
                needed=True,
                mode=mode,
                trigger_type=trigger_type,
                reason=reason,
                notified=escalation.notified_at is not None
            )
        
        # 判定3: 3往復以上未解決
        elif await self._check_multiple_turns_unresolved(conversation_id, db):
            trigger_type = "multiple_turns"
            reason = "3 or more turns without resolution"
        
        else:
            # エスカレーション不要
            return EscalationInfo(needed=False)
        
        # エスカレーション作成
        escalation = await self.create_escalation(
            facility_id=facility_id,
            conversation_id=conversation_id,
            trigger_type=trigger_type,
            ai_confidence=float(confidence),
            escalation_mode=mode,
            notification_channels=notify_channels,
            db=db
        )
        
        return EscalationInfo(
            needed=True,
            mode=mode,
            trigger_type=trigger_type,
            reason=reason,
            notified=escalation.notified_at is not None
        )
    
    async def get_escalation_schedule(
        self,
        facility_id: int,
        weekday: str,
        current_time: time,
        language: str,
        db: AsyncSession
    ) -> Optional[EscalationSchedule]:
        """
        該当するエスカレーションスケジュールを取得（v0.3詳細化）
        
        Args:
            facility_id: 施設ID
            weekday: 曜日（'mon', 'tue', etc.）
            current_time: 現在時刻
            language: 言語コード
            db: データベースセッション
        
        Returns:
            EscalationSchedule: 該当するスケジュール、見つからない場合はNone
        """
        # アクティブなスケジュール取得
        query = select(EscalationSchedule).where(
            EscalationSchedule.facility_id == facility_id,
            EscalationSchedule.is_active == True
        )
        result = await db.execute(query)
        schedules = result.scalars().all()
        
        for schedule in schedules:
            # 曜日チェック
            if "all" in schedule.day_of_week:
                day_match = True
            else:
                day_match = weekday in schedule.day_of_week
            
            if not day_match:
                continue
            
            # 時間帯チェック
            if schedule.time_start <= schedule.time_end:
                # 通常の時間帯（例: 09:00-18:00）
                time_match = schedule.time_start <= current_time <= schedule.time_end
            else:
                # 日を跨ぐ時間帯（例: 18:00-09:00）
                time_match = current_time >= schedule.time_start or current_time <= schedule.time_end
            
            if not time_match:
                continue
            
            # 言語チェック
            if language in schedule.languages or "all" in schedule.languages:
                return schedule
        
        return None
    
    def _detect_emergency_keywords(self, message: str) -> bool:
        """
        緊急キーワード検出（v0.2継続）
        
        Args:
            message: ゲストのメッセージ
        
        Returns:
            bool: 緊急キーワードが検出された場合はTrue
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.EMERGENCY_KEYWORDS)
    
    async def _check_multiple_turns_unresolved(
        self,
        conversation_id: int,
        db: AsyncSession
    ) -> bool:
        """
        3往復以上未解決かチェック（v0.2継続）
        
        Args:
            conversation_id: 会話ID
            db: データベースセッション
        
        Returns:
            bool: 3往復以上未解決の場合はTrue
        """
        # 会話のメッセージ数を取得
        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        # 3往復 = 6メッセージ以上（user + assistant × 3）
        return count >= 6
    
    async def create_escalation(
        self,
        facility_id: int,
        conversation_id: int,
        trigger_type: str,
        ai_confidence: float,
        escalation_mode: str = "normal",
        notification_channels: list = None,
        db: AsyncSession = None
    ) -> Escalation:
        """
        エスカレーション記録作成（v0.3詳細化）
        
        Args:
            facility_id: 施設ID
            conversation_id: 会話ID
            trigger_type: エスカレーション理由（'low_confidence', 'keyword', 'multiple_turns', 'safety_category'）
            ai_confidence: AI信頼度スコア
            escalation_mode: エスカレーションモード（'normal', 'early'）
            notification_channels: 通知チャネルリスト（デフォルト: ['email']）
            db: データベースセッション
        
        Returns:
            Escalation: 作成されたエスカレーション
        """
        if not db:
            raise ValueError("Database session is required")
        
        if notification_channels is None:
            notification_channels = ["email"]
        
        escalation = Escalation(
            facility_id=facility_id,
            conversation_id=conversation_id,
            trigger_type=trigger_type,
            ai_confidence=Decimal(str(ai_confidence)),
            escalation_mode=escalation_mode,
            notification_channels=notification_channels
        )
        
        db.add(escalation)
        await db.commit()
        await db.refresh(escalation)
        
        # 会話のis_escalatedフラグを更新
        conversation = await db.get(Conversation, conversation_id)
        if conversation:
            conversation.is_escalated = True
            await db.commit()
        
        logger.info(
            f"Escalation created: {escalation.id}",
            extra={
                "escalation_id": escalation.id,
                "facility_id": facility_id,
                "conversation_id": conversation_id,
                "trigger_type": trigger_type
            }
        )
        
        return escalation

