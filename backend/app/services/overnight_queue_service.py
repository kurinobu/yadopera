"""
夜間対応キュー管理サービス（v0.3新規）
"""

import logging
from typing import List, Optional
from datetime import datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pytz
from app.models.facility import Facility
from app.models.overnight_queue import OvernightQueue
from app.models.escalation import Escalation
from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)


class OvernightQueueService:
    """
    夜間対応キュー管理サービス（v0.3新規）
    """
    
    NIGHT_START = time(22, 0)  # 22:00
    NIGHT_END = time(8, 0)     # 8:00
    
    async def add_to_overnight_queue(
        self,
        facility_id: int,
        escalation_id: int,
        guest_message: str,
        db: AsyncSession
    ) -> OvernightQueue:
        """
        夜間対応キューに追加（v0.3新規）
        施設のタイムゾーン基準で翌朝8:00を計算
        
        Args:
            facility_id: 施設ID
            escalation_id: エスカレーションID
            guest_message: ゲストメッセージ
            db: データベースセッション
        
        Returns:
            OvernightQueue: 作成された夜間対応キュー
        """
        # 施設のタイムゾーンを取得
        facility = await db.get(Facility, facility_id)
        if not facility:
            raise ValueError(f"Facility not found: {facility_id}")
        
        timezone_str = facility.timezone or 'Asia/Tokyo'
        
        # タイムゾーン変換（UTC → 施設のタイムゾーン）
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        facility_tz = pytz.timezone(timezone_str)
        local_now = utc_now.astimezone(facility_tz)
        
        # 翌朝8:00を計算（施設のタイムゾーン基準）
        if local_now.hour >= 22 or local_now.hour < 8:
            # 夜間時間帯
            if local_now.hour < 8:
                # 0:00-8:00 → 当日8:00
                scheduled_time_local = local_now.replace(hour=8, minute=0, second=0, microsecond=0)
            else:
                # 22:00-23:59 → 翌日8:00
                scheduled_time_local = (local_now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            # 日中時間帯（通常は呼ばないが念のため）
            scheduled_time_local = local_now.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # UTCに変換して保存
        scheduled_time = scheduled_time_local.astimezone(pytz.UTC).replace(tzinfo=None)
        
        overnight_queue = OvernightQueue(
            facility_id=facility_id,
            escalation_id=escalation_id,
            guest_message=guest_message,
            scheduled_notify_at=scheduled_time
        )
        
        db.add(overnight_queue)
        await db.commit()
        await db.refresh(overnight_queue)
        
        logger.info(
            f"Added to overnight queue: {overnight_queue.id}",
            extra={
                "overnight_queue_id": overnight_queue.id,
                "facility_id": facility_id,
                "escalation_id": escalation_id,
                "scheduled_notify_at": scheduled_time.isoformat()
            }
        )
        
        return overnight_queue
    
    async def send_overnight_auto_reply(
        self,
        conversation_id: int,
        language: str = "en",
        db: AsyncSession = None
    ) -> None:
        """
        夜間自動返信メッセージ送信（v0.3新規）
        英語/日本語対応、緊急時119/110案内
        
        Args:
            conversation_id: 会話ID
            language: 言語コード（デフォルト: "en"）
            db: データベースセッション
        """
        if not db:
            raise ValueError("Database session is required")
        
        if language == 'en':
            message = (
                "Thank you for your message. Our staff will respond "
                "by 9:00 AM tomorrow morning. For life-threatening "
                "emergencies, please call 119 (ambulance/fire) or "
                "110 (police)."
            )
        else:  # 日本語
            message = (
                "お問い合わせありがとうございます。明朝9時までに"
                "スタッフよりご連絡いたします。緊急の場合は"
                "119（救急・消防）または110（警察）へお電話ください。"
            )
        
        # メッセージを会話に追加
        system_message = Message(
            conversation_id=conversation_id,
            role="system",
            content=message
        )
        
        db.add(system_message)
        await db.commit()
        
        logger.info(
            f"Sent overnight auto reply to conversation: {conversation_id}",
            extra={
                "conversation_id": conversation_id,
                "language": language
            }
        )
    
    async def process_scheduled_notifications(
        self,
        db: AsyncSession,
        facility_id: Optional[int] = None
    ) -> List[OvernightQueue]:
        """
        翌朝8:00の一括通知処理（v0.3新規）
        MVP期間中: 手動実行ボタンまたは外部cron対応
        
        Args:
            db: データベースセッション
            facility_id: 施設ID（指定時はその施設のみ処理、None時は全施設）
        
        Returns:
            List[OvernightQueue]: 処理されたキューリスト
        """
        now = datetime.utcnow()
        
        # 8:00-8:30の範囲で未通知のキューを取得
        query = select(OvernightQueue).where(
            OvernightQueue.scheduled_notify_at >= now.replace(hour=8, minute=0, second=0, microsecond=0),
            OvernightQueue.scheduled_notify_at < now.replace(hour=8, minute=30, second=0, microsecond=0),
            OvernightQueue.notified_at.is_(None)
        )
        
        if facility_id:
            query = query.where(OvernightQueue.facility_id == facility_id)
        
        result = await db.execute(query)
        queues_list = result.scalars().all()
        
        processed_count = 0
        for queue in queues_list:
            try:
                # スタッフへ通知送信（Phase 2で実装）
                # TODO: send_escalation_notification()を実装後に有効化
                # escalation = await db.get(Escalation, queue.escalation_id)
                # await send_escalation_notification(
                #     facility_id=queue.facility_id,
                #     escalation=escalation
                # )
                
                queue.notified_at = now
                await db.commit()
                processed_count += 1
                
                logger.info(
                    f"Processed overnight queue notification: {queue.id}",
                    extra={
                        "overnight_queue_id": queue.id,
                        "facility_id": queue.facility_id,
                        "escalation_id": queue.escalation_id
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error processing overnight queue: {queue.id}",
                    exc_info=True,
                    extra={
                        "overnight_queue_id": queue.id,
                        "error": str(e)
                    }
                )
                await db.rollback()
        
        logger.info(
            f"Processed {processed_count}/{len(queues_list)} overnight queue notifications",
            extra={
                "processed_count": processed_count,
                "total_count": len(queues_list),
                "facility_id": facility_id
            }
        )
        
        return queues_list
    
    async def get_overnight_queue(
        self,
        facility_id: int,
        db: AsyncSession,
        include_resolved: bool = False
    ) -> List[OvernightQueue]:
        """
        夜間対応キュー取得
        
        Args:
            facility_id: 施設ID
            db: データベースセッション
            include_resolved: 解決済みを含めるか（デフォルト: False）
        
        Returns:
            List[OvernightQueue]: 夜間対応キューリスト
        """
        query = select(OvernightQueue).where(
            OvernightQueue.facility_id == facility_id
        )
        
        if not include_resolved:
            query = query.where(OvernightQueue.resolved_at.is_(None))
        
        query = query.order_by(OvernightQueue.scheduled_notify_at.asc())
        
        result = await db.execute(query)
        queues = result.scalars().all()
        
        return queues

