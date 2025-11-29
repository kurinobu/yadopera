"""
ダッシュボードサービス
ダッシュボードデータ取得のビジネスロジック
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from app.models.overnight_queue import OvernightQueue
from app.models.guest_feedback import GuestFeedback
from app.models.faq import FAQ
from app.schemas.dashboard import (
    DashboardResponse,
    WeeklySummary,
    CategoryBreakdown,
    TopQuestion,
    ChatHistory,
    OvernightQueueItem,
    FeedbackStats,
    LowRatedAnswer
)
from app.core.cache import get_cache, set_cache, cache_key
import asyncio

logger = logging.getLogger(__name__)

# キャッシュTTL（秒）
DASHBOARD_CACHE_TTL = 300  # 5分（リアルタイム性を重視）


class DashboardService:
    """
    ダッシュボードサービス
    - 週次サマリー取得
    - リアルタイムチャット履歴取得
    - 夜間対応キュー取得
    - フィードバック統計取得
    """
    
    def __init__(self, db: AsyncSession):
        """
        ダッシュボードサービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
    
    async def get_dashboard_data(self, facility_id: int) -> DashboardResponse:
        """
        ダッシュボードデータ取得（キャッシュ対応、並列処理）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            DashboardResponse: ダッシュボードデータ
        """
        # キャッシュキー生成
        cache_key_str = cache_key("dashboard:data", facility_id=facility_id)
        
        # キャッシュから取得を試みる
        cached_data = await get_cache(cache_key_str)
        if cached_data is not None:
            logger.debug(f"Dashboard cache hit: {cache_key_str}")
            return DashboardResponse(**cached_data)
        
        # キャッシュミス: 並列処理でデータ取得
        logger.debug(f"Dashboard cache miss: {cache_key_str}")
        summary, recent_conversations, overnight_queue, feedback_stats = await asyncio.gather(
            self.get_weekly_summary(facility_id),
            self.get_recent_chat_history(facility_id),
            self.get_overnight_queue(facility_id),
            self.get_feedback_stats(facility_id)
        )
        
        dashboard_data = DashboardResponse(
            summary=summary,
            recent_conversations=recent_conversations,
            overnight_queue=overnight_queue,
            feedback_stats=feedback_stats
        )
        
        # キャッシュに保存
        await set_cache(cache_key_str, dashboard_data.dict(), DASHBOARD_CACHE_TTL)
        
        return dashboard_data
    
    async def get_weekly_summary(self, facility_id: int) -> WeeklySummary:
        """
        週次サマリー取得（過去7日間）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            WeeklySummary: 週次サマリー
        """
        # 期間計算（過去7日間）
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # 会話を取得
        conversations_result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.facility_id == facility_id,
                Conversation.started_at >= start_date,
                Conversation.started_at <= end_date
            )
        )
        conversations = conversations_result.scalars().all()
        conversation_ids = [c.id for c in conversations]
        
        if not conversation_ids:
            # データがない場合のデフォルト値
            return WeeklySummary(
                period={"start": start_date.isoformat(), "end": end_date.isoformat()},
                total_questions=0,
                auto_response_rate=Decimal("0.0"),
                average_response_time_ms=0,
                average_confidence=Decimal("0.0"),
                category_breakdown=CategoryBreakdown(),
                top_questions=[],
                unresolved_count=0
            )
        
        # メッセージを取得
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id.in_(conversation_ids))
            .where(Message.role == MessageRole.USER.value)
        )
        messages = messages_result.scalars().all()
        
        # 総質問数
        total_questions = len(messages)
        
        # エスカレーション数を取得
        escalations_result = await self.db.execute(
            select(Escalation)
            .where(Escalation.facility_id == facility_id)
            .where(Escalation.created_at >= start_date)
            .where(Escalation.created_at <= end_date)
        )
        escalations = escalations_result.scalars().all()
        escalation_count = len(escalations)
        
        # 自動応答率 = (総質問数 - エスカレーション数) / 総質問数
        auto_response_rate = Decimal("0.0")
        if total_questions > 0:
            auto_response_rate = Decimal(str((total_questions - escalation_count) / total_questions))
        
        # 平均レスポンス時間と平均信頼度
        ai_messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id.in_(conversation_ids))
            .where(Message.role == MessageRole.ASSISTANT.value)
            .where(Message.response_time_ms.isnot(None))
        )
        ai_messages = ai_messages_result.scalars().all()
        
        average_response_time_ms = 0
        if ai_messages:
            total_time = sum(msg.response_time_ms or 0 for msg in ai_messages)
            average_response_time_ms = total_time // len(ai_messages)
        
        average_confidence = Decimal("0.0")
        if ai_messages:
            confidences = [float(msg.ai_confidence or Decimal("0.0")) for msg in ai_messages if msg.ai_confidence]
            if confidences:
                average_confidence = Decimal(str(sum(confidences) / len(confidences)))
        
        # カテゴリ別内訳（簡易実装、FAQカテゴリから推定）
        category_breakdown = CategoryBreakdown()
        # TODO: メッセージ内容からカテゴリを推定する実装（Phase 2で改善）
        
        # TOP5質問（簡易実装）
        top_questions: List[TopQuestion] = []
        # TODO: メッセージ内容から頻出質問を抽出する実装（Phase 2で改善）
        
        # 未解決数（エスカレーション済みで未解決）
        unresolved_result = await self.db.execute(
            select(func.count(Escalation.id))
            .where(Escalation.facility_id == facility_id)
            .where(Escalation.resolved_at.is_(None))
        )
        unresolved_count = unresolved_result.scalar() or 0
        
        return WeeklySummary(
            period={"start": start_date.isoformat(), "end": end_date.isoformat()},
            total_questions=total_questions,
            auto_response_rate=auto_response_rate,
            average_response_time_ms=average_response_time_ms,
            average_confidence=average_confidence,
            category_breakdown=category_breakdown,
            top_questions=top_questions,
            unresolved_count=unresolved_count
        )
    
    async def get_recent_chat_history(self, facility_id: int, limit: int = 10) -> List[ChatHistory]:
        """
        リアルタイムチャット履歴取得（最新10件）
        
        Args:
            facility_id: 施設ID
            limit: 取得件数（デフォルト: 10）
        
        Returns:
            List[ChatHistory]: チャット履歴リスト
        """
        # 最新の会話を取得
        conversations_result = await self.db.execute(
            select(Conversation)
            .where(Conversation.facility_id == facility_id)
            .order_by(Conversation.last_activity_at.desc())
            .limit(limit)
            .options(selectinload(Conversation.messages))
        )
        conversations = conversations_result.scalars().all()
        
        chat_histories: List[ChatHistory] = []
        for conversation in conversations:
            # 最後のメッセージを取得
            if conversation.messages:
                last_message = conversation.messages[-1]
                last_message_content = last_message.content[:100]  # 100文字まで
                
                # AI信頼度を取得（最後のAI応答から）
                ai_confidence = None
                for msg in reversed(conversation.messages):
                    if msg.role == MessageRole.ASSISTANT.value and msg.ai_confidence:
                        ai_confidence = msg.ai_confidence
                        break
                
                chat_histories.append(ChatHistory(
                    session_id=conversation.session_id,
                    guest_language=conversation.guest_language,
                    last_message=last_message_content,
                    ai_confidence=ai_confidence,
                    created_at=conversation.last_activity_at
                ))
        
        return chat_histories
    
    async def get_overnight_queue(self, facility_id: int) -> List[OvernightQueueItem]:
        """
        夜間対応キュー取得
        
        Args:
            facility_id: 施設ID
        
        Returns:
            List[OvernightQueueItem]: 夜間対応キューリスト
        """
        # 未解決の夜間対応キューを取得
        queue_result = await self.db.execute(
            select(OvernightQueue)
            .where(OvernightQueue.facility_id == facility_id)
            .where(OvernightQueue.resolved_at.is_(None))
            .order_by(OvernightQueue.scheduled_notify_at.asc())
        )
        queue_items = queue_result.scalars().all()
        
        return [
            OvernightQueueItem(
                id=item.id,
                facility_id=item.facility_id,
                escalation_id=item.escalation_id,
                guest_message=item.guest_message,
                language="en",  # TODO: 会話から言語を取得
                scheduled_notify_at=item.scheduled_notify_at,
                notified_at=item.notified_at,
                resolved_at=item.resolved_at,
                resolved_by=item.resolved_by,
                created_at=item.created_at
            )
            for item in queue_items
        ]
    
    async def get_feedback_stats(self, facility_id: int) -> FeedbackStats:
        """
        フィードバック統計取得
        
        Args:
            facility_id: 施設ID
        
        Returns:
            FeedbackStats: フィードバック統計
        """
        # フィードバックを取得
        feedback_result = await self.db.execute(
            select(GuestFeedback)
            .where(GuestFeedback.facility_id == facility_id)
        )
        feedbacks = feedback_result.scalars().all()
        
        positive_count = sum(1 for f in feedbacks if f.feedback_type == "positive")
        negative_count = sum(1 for f in feedbacks if f.feedback_type == "negative")
        
        # 肯定率計算
        total_feedback = positive_count + negative_count
        positive_rate = Decimal("0.0")
        if total_feedback > 0:
            positive_rate = Decimal(str(positive_count / total_feedback))
        
        # 低評価回答（2回以上）を取得
        # メッセージIDごとに低評価数を集計
        message_negative_count: dict[int, int] = {}
        for feedback in feedbacks:
            if feedback.feedback_type == "negative":
                message_negative_count[feedback.message_id] = message_negative_count.get(feedback.message_id, 0) + 1
        
        # 2回以上低評価がついたメッセージを取得
        low_rated_message_ids = [msg_id for msg_id, count in message_negative_count.items() if count >= 2]
        
        low_rated_answers: List[LowRatedAnswer] = []
        if low_rated_message_ids:
            # メッセージを取得
            messages_result = await self.db.execute(
                select(Message)
                .where(Message.id.in_(low_rated_message_ids))
                .options(selectinload(Message.conversation))
            )
            messages = messages_result.scalars().all()
            
            for message in messages:
                # 質問と回答を取得（簡易実装）
                # 実際には会話履歴から質問と回答を抽出する必要がある
                question = "Question"  # TODO: 会話履歴から質問を抽出
                answer = message.content[:200]  # 回答は200文字まで
                
                low_rated_answers.append(LowRatedAnswer(
                    message_id=message.id,
                    question=question,
                    answer=answer,
                    negative_count=message_negative_count[message.id]
                ))
        
        return FeedbackStats(
            positive_count=positive_count,
            negative_count=negative_count,
            positive_rate=positive_rate,
            low_rated_answers=low_rated_answers
        )

