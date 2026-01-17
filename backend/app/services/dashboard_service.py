"""
ダッシュボードサービス
ダッシュボードデータ取得のビジネスロジック
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from app.models.overnight_queue import OvernightQueue
from app.models.guest_feedback import GuestFeedback
from app.models.faq import FAQ
from app.models.facility import Facility
from app.schemas.dashboard import (
    DashboardResponse,
    WeeklySummary,
    CategoryBreakdown,
    TopQuestion,
    ChatHistory,
    OvernightQueueItem,
    FeedbackStats,
    LowRatedAnswer,
    MonthlyUsageResponse,
    AiAutomationResponse,
    EscalationsSummaryResponse,
    UnresolvedEscalation
)
from app.core.cache import get_cache, set_cache, cache_key
from app.services.feedback_service import FeedbackService
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
        summary, recent_conversations, overnight_queue, feedback_stats, monthly_usage, ai_automation, escalations_summary, unresolved_escalations = await asyncio.gather(
            self.get_weekly_summary(facility_id),
            self.get_recent_chat_history(facility_id),
            self.get_overnight_queue(facility_id),
            self.get_feedback_stats(facility_id),
            self.get_monthly_usage(facility_id),
            self.get_ai_automation(facility_id),
            self.get_escalations_summary(facility_id),
            self.get_unresolved_escalations(facility_id)
        )
        
        dashboard_data = DashboardResponse(
            summary=summary,
            recent_conversations=recent_conversations,
            overnight_queue=overnight_queue,
            feedback_stats=feedback_stats,
            monthly_usage=monthly_usage,
            ai_automation=ai_automation,
            escalations_summary=escalations_summary,
            unresolved_escalations=unresolved_escalations
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
        
        # カテゴリ別内訳（matched_faq_idsからFAQカテゴリを集計）
        category_breakdown = CategoryBreakdown()
        
        # 過去7日間のAI応答メッセージを取得（matched_faq_idsがNULLでないもの）
        ai_messages_with_faqs_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id.in_(conversation_ids))
            .where(Message.role == MessageRole.ASSISTANT.value)
            .where(Message.matched_faq_ids.isnot(None))
        )
        ai_messages_with_faqs = ai_messages_with_faqs_result.scalars().all()
        
        # matched_faq_idsからFAQ IDを収集（重複を排除、空配列を除外）
        faq_ids = set()
        for msg in ai_messages_with_faqs:
            if msg.matched_faq_ids and len(msg.matched_faq_ids) > 0:
                faq_ids.update(msg.matched_faq_ids)
        
        # FAQを取得してカテゴリを集計
        # 注意: FAQ.idでカウントしているため、インテント単位で1件としてカウントされる（言語に関係なく）
        if faq_ids:
            faqs_result = await self.db.execute(
                select(FAQ)
                .where(FAQ.id.in_(list(faq_ids)))
                .where(FAQ.facility_id == facility_id)
                .where(FAQ.is_active == True)
            )
            faqs = faqs_result.scalars().all()
            
            # カテゴリ別に集計（各メッセージの最初のマッチしたFAQのカテゴリをカウント）
            # FAQ.idでカウントしているため、インテント単位で1件としてカウントされる
            category_counts = {"basic": 0, "facilities": 0, "location": 0, "trouble": 0}
            faq_category_map = {faq.id: faq.category for faq in faqs}
            
            for msg in ai_messages_with_faqs:
                if msg.matched_faq_ids and len(msg.matched_faq_ids) > 0:
                    # 最初のマッチしたFAQのカテゴリをカウント
                    first_faq_id = msg.matched_faq_ids[0]
                    if first_faq_id in faq_category_map:
                        category = faq_category_map[first_faq_id]
                        if category in category_counts:
                            category_counts[category] += 1
            
            category_breakdown = CategoryBreakdown(
                basic=category_counts["basic"],
                facilities=category_counts["facilities"],
                location=category_counts["location"],
                trouble=category_counts["trouble"]
            )
        
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
        # feedback_serviceを使用して重複を排除（統一 > 特殊・独自）
        feedback_service = FeedbackService(self.db)
        low_rated_answers = await feedback_service.get_negative_feedbacks(facility_id)
        
        return FeedbackStats(
            positive_count=positive_count,
            negative_count=negative_count,
            positive_rate=positive_rate,
            low_rated_answers=low_rated_answers
        )
    
    async def get_monthly_usage(self, facility_id: int) -> Optional[MonthlyUsageResponse]:
        """
        今月の質問数/プラン上限を取得（請求期間ベース）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            MonthlyUsageResponse: 月次利用状況（エラー時はNone）
        """
        try:
            # 施設情報を取得
            facility_result = await self.db.execute(
                select(Facility).where(Facility.id == facility_id)
            )
            facility = facility_result.scalar_one_or_none()
            if not facility:
                logger.warning(f"Facility not found: {facility_id}")
                return None  # ValueErrorではなくNoneを返す
            
            # JSTタイムゾーン取得
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)
            
            # plan_started_atを取得（timezone-awareに変換）
            plan_started_at = facility.plan_started_at
            if plan_started_at.tzinfo is None:
                # naive datetimeの場合はUTCとして扱い、JSTに変換
                plan_started_at = pytz.UTC.localize(plan_started_at).astimezone(jst)
            else:
                # timezone-awareの場合はJSTに変換
                plan_started_at = plan_started_at.astimezone(jst)
            
            # 請求期間を計算
            from app.utils.billing_period import calculate_billing_period
            billing_start_jst, billing_end_jst = calculate_billing_period(plan_started_at, now_jst)
            
            # UTCに変換
            billing_start_utc = billing_start_jst.astimezone(pytz.UTC)
            billing_end_utc = billing_end_jst.astimezone(pytz.UTC)
            
            # 請求期間の質問数を集計
            questions_result = await self.db.execute(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Message.role == MessageRole.USER.value,
                    Message.created_at >= billing_start_utc,
                    Message.created_at <= billing_end_utc
                )
            )
            current_billing_period_questions = questions_result.scalar() or 0
            
            # プラン情報を取得
            plan_type = facility.plan_type or 'Free'
            plan_limit = facility.monthly_question_limit
            
            # プラン種別に応じた正しいデフォルト値を定義
            plan_limits = {
                'Free': 30,
                'Mini': None,  # 無制限
                'Small': 200,
                'Standard': 500,
                'Premium': 1000
            }
            
            # プラン種別に応じた正しいデフォルト値を強制適用
            # plan_limitがNoneの場合、またはプラン種別に応じた正しい値と一致しない場合に適用
            expected_limit = plan_limits.get(plan_type, 30)
            if plan_limit is None or plan_limit != expected_limit:
                plan_limit = expected_limit
            
            # 使用率、残り質問数、超過質問数を計算
            usage_percentage = None
            remaining_questions = None
            overage_questions = 0
            status = "normal"
            
            if plan_type == 'Mini':
                # Miniプラン: 上限なし（従量課金のみ）
                overage_questions = current_billing_period_questions
                status = "normal"
            elif plan_limit is not None:
                # 上限があるプラン
                # Freeプランの場合は30件超過でfaq_only
                if plan_type == 'Free' and current_billing_period_questions > 30:
                    overage_questions = current_billing_period_questions - 30
                    usage_percentage = 100.0
                    remaining_questions = 0
                    status = "faq_only"
                elif current_billing_period_questions > plan_limit:
                    overage_questions = current_billing_period_questions - plan_limit
                    usage_percentage = 100.0
                    remaining_questions = 0
                    status = "overage"
                else:
                    usage_percentage = (current_billing_period_questions / plan_limit * 100) if plan_limit > 0 else 0.0
                    remaining_questions = plan_limit - current_billing_period_questions
                    
                    # ステータス判定
                    if usage_percentage >= 91:
                        status = "warning"
                    else:
                        status = "normal"
            else:
                # plan_limitがNULLの場合（通常は発生しないが念のため）
                status = "normal"
            
            return MonthlyUsageResponse(
                current_month_questions=current_billing_period_questions,
                plan_type=plan_type,
                plan_limit=plan_limit,
                usage_percentage=usage_percentage,
                remaining_questions=remaining_questions,
                overage_questions=overage_questions,
                status=status
            )
        
        except Exception as e:
            logger.error(
                f"Error getting monthly usage for facility {facility_id}: {e}",
                exc_info=True
            )
            return None  # エラー時はNoneを返す
    
    async def get_ai_automation(self, facility_id: int) -> Optional[AiAutomationResponse]:
        """
        AI自動応答数・自動化率を取得（請求期間ベース）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            AiAutomationResponse: AI自動応答統計（エラー時はNone）
        """
        try:
            # 施設情報を取得
            facility_result = await self.db.execute(
                select(Facility).where(Facility.id == facility_id)
            )
            facility = facility_result.scalar_one_or_none()
            if not facility:
                logger.warning(f"Facility not found: {facility_id}")
                return None
            
            # JSTタイムゾーン取得
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)
            
            # plan_started_atを取得（timezone-awareに変換）
            plan_started_at = facility.plan_started_at
            if plan_started_at.tzinfo is None:
                # naive datetimeの場合はUTCとして扱い、JSTに変換
                plan_started_at = pytz.UTC.localize(plan_started_at).astimezone(jst)
            else:
                # timezone-awareの場合はJSTに変換
                plan_started_at = plan_started_at.astimezone(jst)
            
            # 請求期間を計算
            from app.utils.billing_period import calculate_billing_period
            billing_start_jst, billing_end_jst = calculate_billing_period(plan_started_at, now_jst)
            
            # UTCに変換
            billing_start_utc = billing_start_jst.astimezone(pytz.UTC)
            billing_end_utc = billing_end_jst.astimezone(pytz.UTC)
            
            # 請求期間の総質問数
            total_questions_result = await self.db.execute(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Message.role == MessageRole.USER.value,
                    Message.created_at >= billing_start_utc,
                    Message.created_at <= billing_end_utc
                )
            )
            total_questions = total_questions_result.scalar() or 0
            
            # エスカレーションされた会話IDを取得
            escalated_conversation_ids_result = await self.db.execute(
                select(Escalation.conversation_id)
                .join(Conversation, Escalation.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Escalation.created_at >= billing_start_utc,
                    Escalation.created_at <= billing_end_utc
                )
            )
            escalated_conversation_ids = [row[0] for row in escalated_conversation_ids_result.all()]
            
            # エスカレーションされなかった会話IDを取得
            all_conversations_result = await self.db.execute(
                select(Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Conversation.started_at >= billing_start_utc,
                    Conversation.started_at <= billing_end_utc
                )
            )
            all_conversation_ids = [row[0] for row in all_conversations_result.all()]
            
            if escalated_conversation_ids:
                non_escalated_conversation_ids = [cid for cid in all_conversation_ids if cid not in escalated_conversation_ids]
            else:
                # エスカレーションがなければすべての会話が対象
                non_escalated_conversation_ids = all_conversation_ids
            
            # AI自動応答数 = エスカレーションされなかった会話のAI自動応答メッセージ数
            ai_responses = 0
            if non_escalated_conversation_ids:
                ai_responses_result = await self.db.execute(
                    select(func.count(Message.id))
                    .where(
                        Message.conversation_id.in_(non_escalated_conversation_ids),
                        Message.role == MessageRole.ASSISTANT.value,
                        Message.created_at >= billing_start_utc,
                        Message.created_at <= billing_end_utc
                    )
                )
                ai_responses = ai_responses_result.scalar() or 0
            
            # 自動化率計算
            automation_rate = 0.0
            if total_questions > 0:
                automation_rate = (ai_responses / total_questions * 100) if total_questions > 0 else 0.0
            
            return AiAutomationResponse(
                ai_responses=ai_responses,
                total_questions=total_questions,
                automation_rate=round(automation_rate, 1)
            )
        
        except Exception as e:
            logger.error(
                f"Error getting AI automation for facility {facility_id}: {e}",
                exc_info=True
            )
            return None  # エラー時はNoneを返す
    
    async def get_escalations_summary(self, facility_id: int) -> Optional[EscalationsSummaryResponse]:
        """
        エスカレーション統計を取得（請求期間ベース）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            EscalationsSummaryResponse: エスカレーション統計（エラー時はNone）
        """
        try:
            # 施設情報を取得
            facility_result = await self.db.execute(
                select(Facility).where(Facility.id == facility_id)
            )
            facility = facility_result.scalar_one_or_none()
            if not facility:
                logger.warning(f"Facility not found: {facility_id}")
                return None
            
            # JSTタイムゾーン取得
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)
            
            # plan_started_atを取得（timezone-awareに変換）
            plan_started_at = facility.plan_started_at
            if plan_started_at.tzinfo is None:
                # naive datetimeの場合はUTCとして扱い、JSTに変換
                plan_started_at = pytz.UTC.localize(plan_started_at).astimezone(jst)
            else:
                # timezone-awareの場合はJSTに変換
                plan_started_at = plan_started_at.astimezone(jst)
            
            # 請求期間を計算
            from app.utils.billing_period import calculate_billing_period
            billing_start_jst, billing_end_jst = calculate_billing_period(plan_started_at, now_jst)
            
            # UTCに変換
            billing_start_utc = billing_start_jst.astimezone(pytz.UTC)
            billing_end_utc = billing_end_jst.astimezone(pytz.UTC)
            
            # 請求期間のエスカレーション数を集計
            escalations_result = await self.db.execute(
                select(Escalation)
                .join(Conversation, Escalation.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Escalation.created_at >= billing_start_utc,
                    Escalation.created_at <= billing_end_utc
                )
            )
            escalations = escalations_result.scalars().all()
            
            total = len(escalations)
            unresolved = sum(1 for e in escalations if e.resolved_at is None)
            resolved = total - unresolved
            
            return EscalationsSummaryResponse(
                total=total,
                unresolved=unresolved,
                resolved=resolved
            )
        
        except Exception as e:
            logger.error(
                f"Error getting escalations summary for facility {facility_id}: {e}",
                exc_info=True
            )
            return None  # エラー時はNoneを返す
    
    async def get_unresolved_escalations(self, facility_id: int, limit: int = 10) -> List[UnresolvedEscalation]:
        """
        未解決エスカレーションを取得（最新10件）
        
        Args:
            facility_id: 施設ID
            limit: 取得件数（デフォルト: 10）
        
        Returns:
            List[UnresolvedEscalation]: 未解決エスカレーションリスト
        """
        try:
            # 未解決エスカレーションを取得
            escalations_result = await self.db.execute(
                select(Escalation)
                .join(Conversation, Escalation.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility_id,
                    Escalation.resolved_at.is_(None)
                )
                .order_by(Escalation.created_at.desc())
                .limit(limit)
                .options(selectinload(Escalation.conversation).selectinload(Conversation.messages))
            )
            escalations = escalations_result.scalars().all()
            
            unresolved_list: List[UnresolvedEscalation] = []
            for escalation in escalations:
                # ゲストメッセージを取得（最初のユーザーメッセージ）
                message = ""
                if escalation.conversation and escalation.conversation.messages:
                    user_messages = [m for m in escalation.conversation.messages if m.role == MessageRole.USER.value]
                    if user_messages:
                        message = user_messages[0].content[:200]  # 200文字まで
                
                # session_idを取得（安全に）
                session_id = ""
                if escalation.conversation and escalation.conversation.session_id:
                    session_id = escalation.conversation.session_id
                else:
                    # conversationが存在しない、またはsession_idがNoneの場合は空文字列
                    logger.warning(
                        f"Conversation or session_id not found for escalation {escalation.id} "
                        f"(conversation_id={escalation.conversation_id})"
                    )
                    session_id = ""
                
                unresolved_list.append(UnresolvedEscalation(
                    id=escalation.id,
                    conversation_id=escalation.conversation_id,
                    session_id=session_id,
                    created_at=escalation.created_at,
                    message=message
                ))
            
            return unresolved_list
        
        except Exception as e:
            logger.error(
                f"Error getting unresolved escalations for facility {facility_id}: {e}",
                exc_info=True
            )
            return []  # エラー時は空のリストを返す

