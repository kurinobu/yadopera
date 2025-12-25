"""
夜間対応キュー管理サービス（v0.3新規）
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pytz
import json
from app.models.facility import Facility
from app.models.overnight_queue import OvernightQueue
from app.models.escalation import Escalation
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.staff_absence import is_in_staff_absence_period, get_next_notification_time
from app.core.cache import delete_cache_pattern, cache_key

logger = logging.getLogger(__name__)


class OvernightQueueService:
    """
    夜間対応キュー管理サービス（v0.3新規）
    スタッフ不在時間帯に対応（v0.3改善）
    """
    
    async def add_to_overnight_queue(
        self,
        facility_id: int,
        escalation_id: int,
        guest_message: str,
        db: AsyncSession
    ) -> OvernightQueue:
        """
        夜間対応キューに追加（v0.3新規、v0.3改善: スタッフ不在時間帯に対応）
        施設のタイムゾーン基準でスタッフ不在時間帯の終了時刻を計算
        
        Args:
            facility_id: 施設ID
            escalation_id: エスカレーションID
            guest_message: ゲストメッセージ
            db: データベースセッション
        
        Returns:
            OvernightQueue: 作成された夜間対応キュー
        """
        # 施設情報を取得
        facility = await db.get(Facility, facility_id)
        if not facility:
            raise ValueError(f"Facility not found: {facility_id}")
        
        timezone_str = facility.timezone or 'Asia/Tokyo'
        
        # タイムゾーン変換（UTC → 施設のタイムゾーン）
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        facility_tz = pytz.timezone(timezone_str)
        local_now = utc_now.astimezone(facility_tz)
        
        # スタッフ不在時間帯を取得
        staff_absence_periods: List[Dict] = []
        if facility.staff_absence_periods:
            try:
                if isinstance(facility.staff_absence_periods, str):
                    staff_absence_periods = json.loads(facility.staff_absence_periods)
                else:
                    staff_absence_periods = facility.staff_absence_periods
            except (json.JSONDecodeError, TypeError, ValueError):
                # パースエラーの場合は空リスト
                staff_absence_periods = []
        
        # 現在の曜日を取得
        current_weekday = local_now.strftime("%a").lower()  # 'mon', 'tue', etc.
        
        # 次の通知時刻を計算（スタッフ不在時間帯の終了時刻）
        scheduled_time_local = get_next_notification_time(
            current_time=local_now,
            current_weekday=current_weekday,
            staff_absence_periods=staff_absence_periods
        )
        
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
        通知予定時刻の一括通知処理（v0.3新規、v0.3改善: スタッフ不在時間帯に対応）
        MVP期間中: 手動実行ボタンまたは外部cron対応
        
        Args:
            db: データベースセッション
            facility_id: 施設ID（指定時はその施設のみ処理、None時は全施設）
        
        Returns:
            List[OvernightQueue]: 処理されたキューリスト
        """
        now = datetime.utcnow()
        
        # 通知予定時刻が現在時刻の30分前から30分後までの範囲で未通知のキューを取得
        # これにより、スタッフ不在時間帯の終了時刻が異なる場合にも対応できる
        time_window_start = now - timedelta(minutes=30)
        time_window_end = now + timedelta(minutes=30)
        
        query = select(OvernightQueue).where(
            OvernightQueue.scheduled_notify_at >= time_window_start,
            OvernightQueue.scheduled_notify_at <= time_window_end,
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
    
    async def resolve_queue_item(
        self,
        queue_id: int,
        user_id: int,
        facility_id: int,
        db: AsyncSession
    ) -> OvernightQueue:
        """
        夜間対応キューアイテムを対応済みにする
        
        Args:
            queue_id: キューID
            user_id: 解決者ID
            facility_id: 施設ID
            db: データベースセッション
        
        Returns:
            OvernightQueue: 更新された夜間対応キュー
        
        Raises:
            ValueError: キューが見つからない、または施設IDが一致しない場合
        """
        # キューを取得
        queue = await db.get(OvernightQueue, queue_id)
        if not queue:
            raise ValueError(f"Overnight queue not found: {queue_id}")
        
        # 施設IDの確認
        if queue.facility_id != facility_id:
            raise ValueError(f"Overnight queue does not belong to facility: {facility_id}")
        
        # 既に解決済みの場合は何もしない
        if queue.resolved_at is not None:
            logger.warning(
                f"Overnight queue already resolved: queue_id={queue_id}",
                extra={
                    "overnight_queue_id": queue_id,
                    "facility_id": facility_id,
                    "resolved_at": queue.resolved_at.isoformat() if queue.resolved_at else None
                }
            )
            return queue
        
        # 解決済みとしてマーク
        queue.resolved_at = datetime.utcnow()
        queue.resolved_by = user_id
        
        await db.commit()
        await db.refresh(queue)
        
        # ダッシュボードキャッシュを無効化（スタッフ不在時間帯対応キューが更新されたため）
        try:
            deleted = await delete_cache_pattern(f"dashboard:data:*facility_id={facility_id}*")
            logger.debug(
                f"Invalidated dashboard cache by pattern: dashboard:data:*facility_id={facility_id}*, deleted={deleted}"
            )
        except Exception as e:
            logger.warning(f"Failed to invalidate dashboard cache: facility_id={facility_id}, error={e}")
        
        logger.info(
            f"Resolved overnight queue: queue_id={queue_id}",
            extra={
                "overnight_queue_id": queue_id,
                "facility_id": facility_id,
                "resolved_by": user_id,
                "resolved_at": queue.resolved_at.isoformat() if queue.resolved_at else None
            }
        )
        
        return queue

