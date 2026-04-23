"""
チャットサービス（v0.3新規）
チャットメッセージ処理のビジネスロジック
"""

import logging
import json
import re
import time
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
import pytz

from app.models.conversation import Conversation
from app.models.escalation import Escalation
from app.models.message import Message, MessageRole
from app.models.facility import Facility
from app.models.faq import FAQ
from app.models.guest_feedback import GuestFeedback
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    MessageResponse,
    FeedbackResponse,
    RAGEngineResponse,
    EscalationInfo,
)
from app.ai.engine import RAGChatEngine
from app.ai.embeddings import generate_embedding
from app.ai.vector_search import search_similar_faqs
from app.ai.fallback import get_faq_only_no_match_message
from app.services.escalation_service import EscalationService
from app.services.escalation_notification_service import send_staff_escalation_notification
from app.services.escalation_absence_routing import queue_escalation_if_staff_absence
from app.services.overnight_queue_service import OvernightQueueService
from app.services.stripe_service import is_stripe_configured, report_usage_to_meter
from app.core.plan_limits import get_plan_limits
from app.core.feature_flags import is_contact_capture_enabled

logger = logging.getLogger(__name__)
CONTACT_CONSENT_PREFIX = "__contact_consent__:"


class ChatService:
    """
    チャットサービス（v0.3新規）
    - セッション管理
    - RAG統合型AI対話エンジン呼び出し
    - エスカレーション処理
    - 夜間対応キュー処理
    - メッセージ保存
    """
    
    def __init__(self, db: AsyncSession):
        """
        チャットサービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
        self.rag_engine = RAGChatEngine(db)
        self.escalation_service = EscalationService()
        self.overnight_queue_service = OvernightQueueService()
    
    async def process_chat_message(
        self,
        request: ChatRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> ChatResponse:
        """
        チャットメッセージ処理（v0.3新規）
        - セッション管理
        - RAG統合型AI対話エンジン呼び出し
        - エスカレーション処理
        - 夜間対応キュー処理
        - メッセージ保存
        
        Args:
            request: チャットリクエスト
            user_agent: ユーザーエージェント（オプション）
            ip_address: IPアドレス（オプション）
        
        Returns:
            ChatResponse: チャットレスポンス
        """
        # Step 2: request.language が施設のAI回答可能言語に含まれるか検証（計画書 Step 2）
        facility_result = await self.db.execute(
            select(Facility).where(Facility.id == request.facility_id)
        )
        facility = facility_result.scalar_one_or_none()
        if not facility:
            raise ValueError("Facility not found")
        plan_type = facility.plan_type or "Free"
        plan_limits = get_plan_limits(plan_type.lower())
        available_languages = plan_limits.get("languages", ["ja"])
        if plan_type == "Premium" or available_languages is None:
            available_languages = ["ja", "en", "zh-TW", "zh-CN", "fr", "ko", "es"]
        if request.language not in available_languages:
            raise ValueError(
                f"選択可能な言語は {', '.join(available_languages)} のみです。"
            )

        # セッション管理: 会話の取得または新規作成
        conversation = await self._get_or_create_conversation(
            facility_id=request.facility_id,
            session_id=request.session_id,
            language=request.language,
            location=request.location,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # ユーザーメッセージを保存
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=request.message
        )
        self.db.add(user_message)
        await self.db.flush()

        use_faq_only = await self._should_use_faq_only_path(facility)
        wifi_shortcut_response = self._build_wifi_shortcut_response(
            facility=facility,
            message=request.message,
            language=request.language,
        )
        # WiFi 関連は施設設定を正本として確定応答する。
        # FAQ や一般知識優先での誤案内を防ぐため、RAG より先にここで返す。
        if wifi_shortcut_response:
            if not use_faq_only:
                await self._report_usage_to_stripe_if_needed(facility)
            ai_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=wifi_shortcut_response.response,
                ai_confidence=wifi_shortcut_response.ai_confidence,
                matched_faq_ids=wifi_shortcut_response.matched_faq_ids,
                response_time_ms=wifi_shortcut_response.response_time_ms,
            )
            self.db.add(ai_message)
            await self.db.flush()
            conversation.last_activity_at = datetime.now(timezone.utc)
            conversation.total_messages += 2
            await self.db.commit()
            await self.db.refresh(ai_message)
            return ChatResponse(
                message=MessageResponse(
                    id=ai_message.id,
                    role=ai_message.role,
                    content=ai_message.content,
                    ai_confidence=ai_message.ai_confidence,
                    matched_faq_ids=ai_message.matched_faq_ids,
                    response_time_ms=ai_message.response_time_ms,
                    created_at=ai_message.created_at
                ),
                session_id=conversation.session_id,
                ai_confidence=wifi_shortcut_response.ai_confidence,
                is_escalated=False,
                escalation_id=None,
                escalation=wifi_shortcut_response.escalation
            )

        # プラン超過時・FAQ限定モード: 超過かつ overage_behavior==faq_only のときは RAG を呼ばず FAQ 検索のみ、Stripe 報告なし
        if use_faq_only:
            rag_response = await self._build_faq_only_response(
                request.message, request.facility_id, request.language
            )
            ai_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=rag_response.response,
                ai_confidence=rag_response.ai_confidence,
                matched_faq_ids=rag_response.matched_faq_ids,
                response_time_ms=rag_response.response_time_ms
            )
            self.db.add(ai_message)
            await self.db.flush()
            if rag_response.matched_faq_ids:
                from app.models.faq_view_log import FAQViewLog
                for faq_id in rag_response.matched_faq_ids:
                    faq_view_log = FAQViewLog(
                        faq_id=faq_id,
                        facility_id=conversation.facility_id,
                        conversation_id=conversation.id,
                        message_id=ai_message.id,
                        guest_language=conversation.guest_language
                    )
                    self.db.add(faq_view_log)
            conversation.last_activity_at = datetime.now(timezone.utc)
            conversation.total_messages += 2
            await self.db.commit()
            await self.db.refresh(ai_message)
            message_response = MessageResponse(
                id=ai_message.id,
                role=ai_message.role,
                content=ai_message.content,
                ai_confidence=ai_message.ai_confidence,
                matched_faq_ids=ai_message.matched_faq_ids,
                response_time_ms=ai_message.response_time_ms,
                created_at=ai_message.created_at
            )
            logger.info(
                "Chat message processed (FAQ-only overage path): conversation_id=%s, message_id=%s",
                conversation.id, ai_message.id,
                extra={"conversation_id": conversation.id, "message_id": ai_message.id, "facility_id": request.facility_id}
            )
            return ChatResponse(
                message=message_response,
                session_id=conversation.session_id,
                ai_confidence=rag_response.ai_confidence,
                is_escalated=False,
                escalation_id=None,
                escalation=rag_response.escalation
            )

        # Phase E: 従量課金メーターへ使用量を報告（Mini: 全件、Small/Standard/Premium: 超過分のみ）
        await self._report_usage_to_stripe_if_needed(facility)

        # RAG統合型AI対話エンジンでメッセージ処理
        rag_response = await self.rag_engine.process_message(
            message=request.message,
            facility_id=request.facility_id,
            session_id=conversation.session_id,
            language=request.language
        )
        
        # AI応答メッセージを保存
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=rag_response.response,
            ai_confidence=rag_response.ai_confidence,
            matched_faq_ids=rag_response.matched_faq_ids,
            response_time_ms=rag_response.response_time_ms
        )
        self.db.add(ai_message)
        await self.db.flush()
        
        # FAQ閲覧ログ記録（非同期）
        if rag_response.matched_faq_ids:
            from app.models.faq_view_log import FAQViewLog
            for faq_id in rag_response.matched_faq_ids:
                faq_view_log = FAQViewLog(
                    faq_id=faq_id,
                    facility_id=conversation.facility_id,
                    conversation_id=conversation.id,
                    message_id=ai_message.id,
                    guest_language=conversation.guest_language
                )
                self.db.add(faq_view_log)
            await self.db.commit()
        
        # エスカレーション処理
        escalation_id = None
        if rag_response.escalation.needed:
            # エスカレーション記録作成
            escalation = await self.escalation_service.create_escalation(
                facility_id=request.facility_id,
                conversation_id=conversation.id,
                trigger_type=rag_response.escalation.trigger_type or "low_confidence",
                ai_confidence=float(rag_response.ai_confidence or Decimal("0.0")),
                escalation_mode=rag_response.escalation.mode or "normal",
                notification_channels=["email"],  # デフォルトはemail
                db=self.db
            )
            escalation_id = escalation.id
            queued_for_overnight = await queue_escalation_if_staff_absence(
                self.db,
                facility_id=request.facility_id,
                escalation_id=escalation.id,
                conversation_id=conversation.id,
                guest_message=request.message,
                guest_language_for_auto_reply=request.language,
                overnight_queue_service=self.overnight_queue_service,
            )
            if not queued_for_overnight:
                await send_staff_escalation_notification(self.db, escalation.id)
        
        # 会話の最終活動時刻を更新
        conversation.last_activity_at = datetime.now(timezone.utc)
        conversation.total_messages += 2  # ユーザーメッセージ + AI応答
        
        await self.db.commit()
        await self.db.refresh(ai_message)
        
        # MessageResponseオブジェクトを作成
        message_response = MessageResponse(
            id=ai_message.id,
            role=ai_message.role,
            content=ai_message.content,
            ai_confidence=ai_message.ai_confidence,
            matched_faq_ids=ai_message.matched_faq_ids,
            response_time_ms=ai_message.response_time_ms,
            created_at=ai_message.created_at
        )
        
        # 新しいChatResponseオブジェクトを作成
        new_chat_response = ChatResponse(
            message=message_response,
            session_id=conversation.session_id,
            ai_confidence=rag_response.ai_confidence,
            is_escalated=rag_response.escalation.needed,
            escalation_id=escalation_id,
            escalation=rag_response.escalation
        )
        
        logger.info(
            f"Chat message processed: conversation_id={conversation.id}, message_id={ai_message.id}",
            extra={
                "conversation_id": conversation.id,
                "message_id": ai_message.id,
                "facility_id": request.facility_id,
                "session_id": conversation.session_id,
                "escalation_needed": rag_response.escalation.needed
            }
        )
        
        return new_chat_response

    def _normalize_message_for_intent(self, message: str) -> str:
        text = (message or "").strip().lower()
        text = text.replace("　", " ")
        text = text.replace("wi-fi", "wifi")
        text = re.sub(r"\s+", " ", text)
        return text

    def _is_wifi_related_message(self, message: str) -> bool:
        text = self._normalize_message_for_intent(message)
        if not text:
            return False
        wifi_keywords = [
            "wifi", "wi fi", "ワイファイ", "無線", "internet", "internet connection",
            "ssid", "パスワード", "password", "接続", "つなが", "繋が", "使い方",
            "how to connect", "how do i connect", "network",
        ]
        return any(k in text for k in wifi_keywords)

    def _build_wifi_shortcut_response(
        self,
        facility: Facility,
        message: str,
        language: str
    ) -> Optional[RAGEngineResponse]:
        if not self._is_wifi_related_message(message):
            return None

        ssid = (getattr(facility, "wifi_ssid", None) or "").strip()
        password = (getattr(facility, "wifi_password", None) or "").strip()
        if language == "ja":
            if ssid and password:
                text = (
                    f"WiFiのSSIDは「{ssid}」、パスワードは「{password}」です。"
                    "接続先でSSIDを選び、パスワードを入力してください。"
                )
            elif ssid and not password:
                text = (
                    f"WiFiのSSIDは「{ssid}」です。パスワードは施設で未設定のため、"
                    "フロントまたはスタッフにご確認ください。"
                )
            else:
                text = "WiFi情報が未設定です。フロントまたはスタッフにご確認ください。"
        else:
            if ssid and password:
                text = (
                    f"The WiFi SSID is \"{ssid}\" and the password is \"{password}\". "
                    "Please select the SSID and enter the password to connect."
                )
            elif ssid and not password:
                text = (
                    f"The WiFi SSID is \"{ssid}\". The password is not set in the facility settings, "
                    "so please ask the staff at the property."
                )
            else:
                text = "WiFi information is not configured. Please ask the staff at the property."

        return RAGEngineResponse(
            response=text,
            ai_confidence=Decimal("0.95"),
            matched_faq_ids=[],
            response_time_ms=1,
            escalation=EscalationInfo(
                needed=False,
                mode=None,
                trigger_type=None,
                reason=None,
                notified=None,
            ),
        )

    async def _report_usage_to_stripe_if_needed(self, facility: Facility) -> None:
        """
        Phase E: 従量課金メーターへ使用量を報告する。
        Mini は全質問で 1 件報告。Small/Standard/Premium は請求期間内の質問数がプラン上限を超えた分のみ報告。
        Stripe 未設定・Free プラン・stripe_customer_id なしの場合は何もしない。
        """
        if not facility or not getattr(facility, "stripe_customer_id", None) or not facility.stripe_customer_id:
            return
        if not is_stripe_configured():
            return
        plan_type = facility.plan_type or "Free"
        if plan_type == "Free":
            return
        try:
            if plan_type == "Mini":
                report_usage_to_meter(facility.stripe_customer_id, value=1)
                return
            if plan_type not in ("Small", "Standard", "Premium"):
                return
            # 請求期間内の質問数（今回のメッセージを含む）を集計
            from app.utils.billing_period import calculate_billing_period
            jst = pytz.timezone("Asia/Tokyo")
            now_jst = datetime.now(jst)
            plan_started_at = facility.plan_started_at
            if not plan_started_at:
                return
            if plan_started_at.tzinfo is None:
                plan_started_at = pytz.UTC.localize(plan_started_at).astimezone(jst)
            else:
                plan_started_at = plan_started_at.astimezone(jst)
            billing_start_jst, billing_end_jst = calculate_billing_period(plan_started_at, now_jst)
            billing_start_utc = billing_start_jst.astimezone(pytz.UTC)
            billing_end_utc = billing_end_jst.astimezone(pytz.UTC)
            count_result = await self.db.execute(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility.id,
                    Message.role == MessageRole.USER.value,
                    Message.created_at >= billing_start_utc,
                    Message.created_at <= billing_end_utc,
                )
            )
            current_count = count_result.scalar() or 0
            plan_limit = facility.monthly_question_limit
            plan_limits = {"Small": 200, "Standard": 500, "Premium": 1000}
            expected = plan_limits.get(plan_type, 200)
            if plan_limit is None or plan_limit != expected:
                plan_limit = expected
            if current_count > plan_limit:
                report_usage_to_meter(facility.stripe_customer_id, value=1)
        except Exception as e:
            logger.warning(
                "Phase E: Stripe usage report skipped for facility_id=%s: %s",
                facility.id,
                e,
                exc_info=False,
            )

    async def _should_use_faq_only_path(self, facility: Facility) -> bool:
        """
        プラン超過時・FAQ限定モードかどうか判定する。
        請求期間内の質問数がプラン上限を超えており、かつ overage_behavior==faq_only のとき True。
        Mini は上限なしのため常に False。
        """
        plan_type = facility.plan_type or "Free"
        if plan_type == "Mini":
            return False
        plan_limits = {"Free": 30, "Small": 200, "Standard": 500, "Premium": 1000}
        plan_limit = facility.monthly_question_limit
        expected = plan_limits.get(plan_type, 30)
        if plan_limit is None or plan_limit != expected:
            plan_limit = expected
        if getattr(facility, "overage_behavior", "continue_billing") != "faq_only":
            return False
        try:
            from app.utils.billing_period import calculate_billing_period
            jst = pytz.timezone("Asia/Tokyo")
            now_jst = datetime.now(jst)
            plan_started_at = facility.plan_started_at
            if not plan_started_at:
                return False
            if plan_started_at.tzinfo is None:
                plan_started_at = pytz.UTC.localize(plan_started_at).astimezone(jst)
            else:
                plan_started_at = plan_started_at.astimezone(jst)
            billing_start_jst, billing_end_jst = calculate_billing_period(plan_started_at, now_jst)
            billing_start_utc = billing_start_jst.astimezone(pytz.UTC)
            billing_end_utc = billing_end_jst.astimezone(pytz.UTC)
            count_result = await self.db.execute(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility.id,
                    Message.role == MessageRole.USER.value,
                    Message.created_at >= billing_start_utc,
                    Message.created_at <= billing_end_utc,
                )
            )
            current_count = count_result.scalar() or 0
            return current_count > plan_limit
        except Exception as e:
            logger.warning("_should_use_faq_only_path failed for facility_id=%s: %s", facility.id, e)
            return False

    async def _build_faq_only_response(
        self, message: str, facility_id: int, language: str
    ) -> RAGEngineResponse:
        """
        プラン超過・FAQ限定モード用: 埋め込み＋FAQ検索のみで応答を組み立てる。OpenAI は呼ばない。
        """
        start_time = time.time()
        question_embedding = await generate_embedding(message)
        if not question_embedding:
            question_embedding = []
        similar_faqs = await search_similar_faqs(
            facility_id=facility_id,
            embedding=question_embedding,
            top_k=1,
            threshold=0.7,
            db=self.db
        )
        response_text: str
        matched_faq_ids: List[int] = []
        if similar_faqs:
            best_faq = similar_faqs[0]
            faq_with_trans_result = await self.db.execute(
                select(FAQ)
                .where(FAQ.id == best_faq.id)
                .options(selectinload(FAQ.translations))
            )
            faq_with_trans = faq_with_trans_result.scalar_one_or_none()
            if faq_with_trans and getattr(faq_with_trans, "translations", None):
                translation = None
                for t in faq_with_trans.translations:
                    if t.language == language:
                        translation = t
                        break
                if not translation:
                    translation = faq_with_trans.translations[0]
                if translation:
                    response_text = translation.answer
                    matched_faq_ids = [best_faq.id]
                else:
                    response_text = get_faq_only_no_match_message(language)
            else:
                response_text = get_faq_only_no_match_message(language)
        else:
            response_text = get_faq_only_no_match_message(language)
        response_time_ms = int((time.time() - start_time) * 1000)
        return RAGEngineResponse(
            response=response_text,
            ai_confidence=Decimal("0.7"),
            matched_faq_ids=matched_faq_ids,
            response_time_ms=response_time_ms,
            escalation=EscalationInfo(needed=False, mode=None, trigger_type=None, reason=None, notified=None),
        )

    async def _get_or_create_conversation(
        self,
        facility_id: int,
        session_id: Optional[str],
        language: str,
        location: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Conversation:
        """
        会話の取得または新規作成
        
        Args:
            facility_id: 施設ID
            session_id: セッションID（Noneの場合は新規生成）
            language: 言語コード
            location: QRコード設置場所（オプション）
            user_agent: ユーザーエージェント（オプション）
            ip_address: IPアドレス（オプション）
        
        Returns:
            Conversation: 会話オブジェクト
        """
        # セッションIDが指定されていない場合は新規生成
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 既存の会話を検索
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.facility_id == facility_id,
                Conversation.session_id == session_id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if conversation:
            # セッション有効期限をチェック（防止策1: started_atベースの固定有効期限）
            from app.utils.session import is_session_valid
            is_valid = await is_session_valid(session_id, self.db)
            
            if not is_valid:
                # セッションが無効な場合は、既存の会話を無視して新規セッションを作成
                logger.info(f"Session expired, creating new session: old_session_id={session_id}, facility_id={facility_id}")
                conversation = None  # 既存の会話を無視
                # 既存のセッションIDが無効な場合は、新しいセッションIDを生成
                session_id = str(uuid.uuid4())
                logger.info(f"Generating new session_id for expired session: new_session_id={session_id}")
            else:
                # 既存の会話を更新
                conversation.last_activity_at = datetime.now(timezone.utc)
                if location:
                    conversation.location = location
                logger.debug(f"Existing conversation found: conversation_id={conversation.id}, session_id={session_id}")
        
        if not conversation:
            # 新規会話を作成（既存の会話が存在しない、またはセッションが無効な場合）
            try:
                conversation = Conversation(
                    facility_id=facility_id,
                    session_id=session_id,
                    guest_language=language,
                    location=location,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    started_at=datetime.now(timezone.utc),
                    last_activity_at=datetime.now(timezone.utc)
                )
                self.db.add(conversation)
                await self.db.flush()
                logger.info(f"New conversation created: conversation_id={conversation.id}, session_id={session_id}")
            except IntegrityError as e:
                # セッションIDの重複エラーが発生した場合（並行処理による競合）
                # 既存の会話を再取得する
                await self.db.rollback()
                logger.warning(f"Session ID duplicate detected, retrieving existing conversation: session_id={session_id}, error={e}")
                
                # 既存の会話を再取得
                result = await self.db.execute(
                    select(Conversation).where(
                        Conversation.facility_id == facility_id,
                        Conversation.session_id == session_id
                    )
                )
                conversation = result.scalar_one_or_none()
                
                if conversation:
                    # 既存の会話を更新
                    conversation.last_activity_at = datetime.now(timezone.utc)
                    if location:
                        conversation.location = location
                    logger.info(f"Existing conversation retrieved after duplicate error: conversation_id={conversation.id}, session_id={session_id}")
                else:
                    # 既存の会話が見つからない場合は、新しいセッションIDを生成して再試行
                    logger.error(f"Existing conversation not found after duplicate error, generating new session_id: old_session_id={session_id}")
                    session_id = str(uuid.uuid4())
                    conversation = Conversation(
                        facility_id=facility_id,
                        session_id=session_id,
                        guest_language=language,
                        location=location,
                        user_agent=user_agent,
                        ip_address=ip_address,
                        started_at=datetime.now(timezone.utc),
                        last_activity_at=datetime.now(timezone.utc)
                    )
                    self.db.add(conversation)
                    await self.db.flush()
                    logger.info(f"New conversation created with new session_id: conversation_id={conversation.id}, session_id={session_id}")
        
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation_history(
        self,
        session_id: str,
        facility_id: Optional[int] = None
    ) -> Optional[ChatHistoryResponse]:
        """
        会話履歴取得（v0.3新規）
        
        Args:
            session_id: セッションID
            facility_id: 施設ID（オプション、指定時はその施設の会話のみ）
        
        Returns:
            ChatHistoryResponse: 会話履歴、見つからない場合はNone
        
        Note:
            - ゲスト側（facility_idがNone）: セッション有効期限チェックを実行（24時間以内）
            - 管理画面側（facility_idが指定されている）: セッション有効期限チェックをスキップ（月次統計のため過去の会話も表示可能）
        """
        # セッション有効期限をチェック（ゲスト側のみ）
        # 管理画面からのアクセス（facility_idが指定されている場合）はスキップ
        # 理由: 管理画面では月次統計のため過去の会話（今月のデータ）も表示する必要がある
        if facility_id is None:
            from app.utils.session import is_session_valid
            is_valid = await is_session_valid(session_id, self.db)
            
            if not is_valid:
                logger.warning(f"Session expired: session_id={session_id}")
                return None
        
        # 会話を検索
        query = select(Conversation).where(Conversation.session_id == session_id)
        if facility_id:
            query = query.where(Conversation.facility_id == facility_id)
        
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            logger.warning(f"Conversation not found: session_id={session_id}")
            return None
        
        # メッセージを取得
        messages_result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
        )
        messages = messages_result.scalars().all()
        
        # メッセージレスポンスに変換
        message_responses = [
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                ai_confidence=msg.ai_confidence,
                matched_faq_ids=msg.matched_faq_ids,
                response_time_ms=msg.response_time_ms,
                created_at=msg.created_at
            )
            for msg in messages
            if not self._is_contact_consent_message(msg)
        ]

        unresolved_escalation_id: Optional[int] = None
        contactability_status: Optional[str] = None
        if facility_id is not None:
            open_esc = await self.db.execute(
                select(Escalation.id)
                .where(
                    Escalation.conversation_id == conversation.id,
                    Escalation.resolved_at.is_(None),
                )
                .order_by(Escalation.created_at.desc())
                .limit(1)
            )
            unresolved_escalation_id = open_esc.scalar_one_or_none()
            contactability_status = self._get_contactability_status(messages)
        
        return ChatHistoryResponse(
            session_id=conversation.session_id,
            facility_id=conversation.facility_id,
            language=conversation.guest_language,
            location=conversation.location,
            started_at=conversation.started_at,
            last_activity_at=conversation.last_activity_at,
            messages=message_responses,
            unresolved_escalation_id=unresolved_escalation_id,
            contactability_status=contactability_status,
        )

    async def create_staff_reply(
        self,
        *,
        session_id: str,
        facility_id: int,
        content: str,
    ) -> Message:
        """
        管理者手動返信（role=staff）を保存する。
        """
        body = (content or "").strip()
        if not body:
            raise ValueError("Reply content is required")

        result = await self.db.execute(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.facility_id == facility_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ValueError(f"Conversation not found: session_id={session_id}")

        open_esc = await self.db.execute(
            select(Escalation.id).where(
                Escalation.conversation_id == conversation.id,
                Escalation.facility_id == facility_id,
                Escalation.resolved_at.is_(None),
            ).limit(1)
        )
        if open_esc.scalar_one_or_none() is None:
            raise ValueError("No unresolved escalation found for this conversation")

        staff_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.STAFF.value,
            content=body,
        )
        self.db.add(staff_message)
        conversation.last_activity_at = datetime.now(timezone.utc)
        conversation.total_messages += 1
        await self.db.commit()
        await self.db.refresh(staff_message)
        return staff_message

    def _get_contactability_status(self, messages: List[Message]) -> str:
        """
        C-1: 連絡可能状態の最小定義。
        C-3有効時は会話メッセージ内の同意メタ情報から判定する。
        """
        if is_contact_capture_enabled():
            for msg in messages:
                if not self._is_contact_consent_message(msg):
                    continue
                payload = self._parse_contact_consent(msg.content)
                if payload and payload.get("consent") is True and payload.get("email"):
                    return "contactable"
        return "no_contact"

    async def capture_contact_consent(
        self,
        *,
        facility_id: int,
        session_id: str,
        email: str,
        guest_name: Optional[str],
        consent: bool,
    ) -> str:
        """
        C-3: 連絡先提供同意を保存（feature flag ON時のみ）。
        既存スキーマを変更せず messages(role=system) にメタ情報として記録する。
        """
        if not is_contact_capture_enabled():
            raise ValueError("Contact capture feature is disabled")

        result = await self.db.execute(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.facility_id == facility_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ValueError(f"Conversation not found: session_id={session_id}")

        payload = {
            "email": (email or "").strip(),
            "guest_name": (guest_name or "").strip() or None,
            "consent": bool(consent),
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        marker = Message(
            conversation_id=conversation.id,
            role=MessageRole.SYSTEM.value,
            content=f"{CONTACT_CONSENT_PREFIX}{json.dumps(payload, ensure_ascii=False)}",
        )
        self.db.add(marker)
        conversation.last_activity_at = datetime.now(timezone.utc)
        await self.db.commit()
        return "contactable" if payload["consent"] and payload["email"] else "no_contact"

    @staticmethod
    def _is_contact_consent_message(message: Message) -> bool:
        return (
            message.role == MessageRole.SYSTEM.value
            and isinstance(message.content, str)
            and message.content.startswith(CONTACT_CONSENT_PREFIX)
        )

    @staticmethod
    def _parse_contact_consent(content: str) -> Optional[dict]:
        if not isinstance(content, str) or not content.startswith(CONTACT_CONSENT_PREFIX):
            return None
        raw = content[len(CONTACT_CONSENT_PREFIX):]
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    
    async def save_feedback(
        self,
        message_id: int,
        feedback_type: str
    ) -> FeedbackResponse:
        """
        ゲストフィードバック保存（v0.3新規）
        
        Args:
            message_id: メッセージID
            feedback_type: フィードバックタイプ（positive/negative）
        
        Returns:
            FeedbackResponse: フィードバックレスポンス
        
        Raises:
            ValueError: バリデーションエラー
        """
        # バリデーション
        if feedback_type not in ["positive", "negative"]:
            raise ValueError(f"Invalid feedback_type: {feedback_type}. Must be 'positive' or 'negative'")
        
        # メッセージを取得
        message = await self.db.get(Message, message_id)
        if not message:
            raise ValueError(f"Message not found: message_id={message_id}")
        
        # 会話を取得して施設IDを取得
        conversation = await self.db.get(Conversation, message.conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: conversation_id={message.conversation_id}")
        
        # フィードバックを保存
        feedback = GuestFeedback(
            message_id=message_id,
            facility_id=conversation.facility_id,
            feedback_type=feedback_type
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        
        logger.info(
            f"Feedback saved: feedback_id={feedback.id}, message_id={message_id}, type={feedback_type}",
            extra={
                "feedback_id": feedback.id,
                "message_id": message_id,
                "facility_id": conversation.facility_id,
                "feedback_type": feedback_type
            }
        )
        
        return FeedbackResponse(
            id=feedback.id,
            message_id=feedback.message_id,
            feedback_type=feedback.feedback_type,
            created_at=feedback.created_at
        )

