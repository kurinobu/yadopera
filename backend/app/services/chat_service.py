"""
チャットサービス（v0.3新規）
チャットメッセージ処理のビジネスロジック
"""

import logging
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import pytz

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.facility import Facility
from app.models.guest_feedback import GuestFeedback
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse, MessageResponse, FeedbackResponse
from app.ai.engine import RAGChatEngine
from app.services.escalation_service import EscalationService
from app.services.overnight_queue_service import OvernightQueueService

logger = logging.getLogger(__name__)


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
            
            # 夜間対応キュー処理（スタッフ不在時間帯の場合）
            facility = await self.db.get(Facility, request.facility_id)
            if facility:
                timezone_str = facility.timezone or 'Asia/Tokyo'
                utc_now = datetime.now(timezone.utc)
                facility_tz = pytz.timezone(timezone_str)
                local_now = utc_now.astimezone(facility_tz)
                
                # スタッフ不在時間帯を取得
                staff_absence_periods = []
                if facility.staff_absence_periods:
                    try:
                        import json
                        if isinstance(facility.staff_absence_periods, str):
                            staff_absence_periods = json.loads(facility.staff_absence_periods)
                        else:
                            staff_absence_periods = facility.staff_absence_periods
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # パースエラーの場合は空リスト
                        staff_absence_periods = []
                
                # 現在の曜日を取得
                current_weekday = local_now.strftime("%a").lower()  # 'mon', 'tue', etc.
                
                # スタッフ不在時間帯の判定
                from app.utils.staff_absence import is_in_staff_absence_period
                if is_in_staff_absence_period(
                    current_time=local_now,
                    current_weekday=current_weekday,
                    staff_absence_periods=staff_absence_periods
                ):
                    # 夜間対応キューに追加
                    await self.overnight_queue_service.add_to_overnight_queue(
                        facility_id=request.facility_id,
                        escalation_id=escalation.id,
                        guest_message=request.message,
                        db=self.db
                    )
                    
                    # 夜間自動返信メッセージ送信
                    await self.overnight_queue_service.send_overnight_auto_reply(
                        conversation_id=conversation.id,
                        language=request.language,
                        db=self.db
                    )
        
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
        ]
        
        return ChatHistoryResponse(
            session_id=conversation.session_id,
            facility_id=conversation.facility_id,
            language=conversation.guest_language,
            location=conversation.location,
            started_at=conversation.started_at,
            last_activity_at=conversation.last_activity_at,
            messages=message_responses
        )
    
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

