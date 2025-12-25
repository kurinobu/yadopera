"""
フィードバックサービス
低評価回答リスト取得のビジネスロジック
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.guest_feedback import GuestFeedback
from app.models.ignored_feedback import IgnoredFeedback
from app.models.processed_feedback import ProcessedFeedback
from app.models.message import Message, MessageRole
from app.models.conversation import Conversation
from app.schemas.dashboard import LowRatedAnswer

logger = logging.getLogger(__name__)


class FeedbackService:
    """
    フィードバックサービス
    - 低評価回答リスト取得
    """
    
    def __init__(self, db: AsyncSession):
        """
        フィードバックサービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
    
    async def get_negative_feedbacks(
        self,
        facility_id: int
    ) -> List[LowRatedAnswer]:
        """
        低評価回答リスト取得（2回以上低評価がついた回答）
        
        Args:
            facility_id: 施設ID
        
        Returns:
            List[LowRatedAnswer]: 低評価回答リスト
        """
        # フィードバックを取得
        feedback_result = await self.db.execute(
            select(GuestFeedback)
            .where(
                GuestFeedback.facility_id == facility_id,
                GuestFeedback.feedback_type == "negative"
            )
        )
        feedbacks = feedback_result.scalars().all()
        
        # メッセージIDごとに低評価数を集計
        message_negative_count: dict[int, int] = {}
        for feedback in feedbacks:
            message_negative_count[feedback.message_id] = message_negative_count.get(feedback.message_id, 0) + 1
        
        # 2回以上低評価がついたメッセージIDを取得
        low_rated_message_ids = [msg_id for msg_id, count in message_negative_count.items() if count >= 2]
        
        if not low_rated_message_ids:
            return []
        
        # 無視されたメッセージIDを取得
        ignored_result = await self.db.execute(
            select(IgnoredFeedback.message_id).where(
                IgnoredFeedback.facility_id == facility_id,
                IgnoredFeedback.message_id.in_(low_rated_message_ids)
            )
        )
        ignored_message_ids = set(ignored_result.scalars().all())
        
        # 処理済みのメッセージIDを取得（FAQ承認により処理済みとなった低評価回答）
        processed_result = await self.db.execute(
            select(ProcessedFeedback.message_id).where(
                ProcessedFeedback.facility_id == facility_id,
                ProcessedFeedback.message_id.in_(low_rated_message_ids)
            )
        )
        processed_message_ids = set(processed_result.scalars().all())
        
        # 無視されたメッセージIDと処理済みのメッセージIDを除外
        excluded_message_ids = ignored_message_ids | processed_message_ids
        low_rated_message_ids = [msg_id for msg_id in low_rated_message_ids if msg_id not in excluded_message_ids]
        
        if not low_rated_message_ids:
            return []
        
        # メッセージを取得（会話も一緒に取得）
        # ASSISTANTロールのメッセージのみを取得（データ整合性を確保）
        messages_result = await self.db.execute(
            select(Message)
            .where(
                Message.id.in_(low_rated_message_ids),
                Message.role == MessageRole.ASSISTANT.value
            )
            .options(selectinload(Message.conversation))
        )
        messages = messages_result.scalars().all()
        
        # ログを追加して、取得されたメッセージのroleを確認
        logger.info(
            f"Retrieved messages for negative feedbacks: facility_id={facility_id}, "
            f"low_rated_message_ids={low_rated_message_ids}, "
            f"retrieved_count={len(messages)}"
        )
        for msg in messages:
            logger.debug(
                f"Message in negative feedbacks: message_id={msg.id}, role={msg.role}, "
                f"content={msg.content[:50] if msg.content else 'None'}..."
            )
        
        # ASSISTANTロールのメッセージが取得できなかった場合の警告
        if len(messages) < len(low_rated_message_ids):
            missing_ids = set(low_rated_message_ids) - {msg.id for msg in messages}
            # フィルタリングされたメッセージの詳細を確認
            missing_messages_result = await self.db.execute(
                select(Message)
                .where(Message.id.in_(list(missing_ids)))
            )
            missing_messages = missing_messages_result.scalars().all()
            for missing_msg in missing_messages:
                logger.warning(
                    f"Message filtered out (not ASSISTANT role): message_id={missing_msg.id}, "
                    f"role={missing_msg.role}, facility_id={facility_id}"
                )
            logger.warning(
                f"Some message IDs were filtered out (not ASSISTANT role): "
                f"facility_id={facility_id}, missing_ids={missing_ids}, "
                f"filtered_count={len(missing_ids)}, retrieved_count={len(messages)}"
            )
        
        low_rated_answers: List[LowRatedAnswer] = []
        
        for message in messages:
            # 会話内のメッセージを取得（質問を取得するため）
            # faq_suggestion_service.pyと同じロジックで順序を確実にする
            conversation_messages_result = await self.db.execute(
                select(Message)
                .where(Message.conversation_id == message.conversation_id)
                .order_by(Message.created_at.asc(), Message.id.asc())
            )
            conversation_messages = conversation_messages_result.scalars().all()
            
            # このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
            # faq_suggestion_service.pyのpick_question_before関数と同じロジック
            def pick_question_before(index: int) -> str | None:
                """
                直前以前のUSERメッセージから「質問らしい」ものを優先的に選ぶ。
                疑問符を含むものを優先し、それがなければ直近のUSERロールを返す。
                """
                # 疑問符を含むUSERメッセージを優先的に探す
                for i in range(index - 1, -1, -1):
                    msg = conversation_messages[i]
                    if msg.role != MessageRole.USER.value:
                        continue
                    content = (msg.content or "").strip()
                    if not content:
                        continue
                    # 疑問符を含むものを優先
                    if "?" in content or content.endswith("？"):
                        return content
                
                # 疑問符がない場合は、直近のUSERロールを返す
                for i in range(index - 1, -1, -1):
                    msg = conversation_messages[i]
                    if msg.role == MessageRole.USER.value:
                        content = (msg.content or "").strip()
                        if content:
                            return content
                
                return None
            
            # メッセージのインデックスを見つける
            message_index = None
            for i, msg in enumerate(conversation_messages):
                if msg.id == message.id:
                    message_index = i
                    break
            
            if message_index is None:
                logger.warning(
                    f"Message not found in conversation: message_id={message.id}, "
                    f"conversation_id={message.conversation_id}"
                )
                continue
            
            if message_index == 0:
                logger.warning(
                    f"Assistant message is the first message in conversation: message_id={message.id}, "
                    f"conversation_id={message.conversation_id}"
                )
                question = "質問が見つかりませんでした"
            else:
                question = pick_question_before(message_index)
                if not question:
                    logger.warning(
                        f"User message not found for assistant message: message_id={message.id}, "
                        f"conversation_id={message.conversation_id}, message_index={message_index}"
                    )
                    question = "質問が見つかりませんでした"
            
            # 回答はメッセージの内容（200文字まで）
            answer = message.content[:200] if len(message.content) > 200 else message.content
            
            low_rated_answers.append(LowRatedAnswer(
                message_id=message.id,
                question=question,
                answer=answer,
                negative_count=message_negative_count[message.id]
            ))
        
        logger.info(
            f"Low-rated answers retrieved: facility_id={facility_id}, count={len(low_rated_answers)}",
            extra={
                "facility_id": facility_id,
                "count": len(low_rated_answers)
            }
        )
        
        return low_rated_answers
    
    async def ignore_negative_feedback(
        self,
        message_id: int,
        facility_id: int,
        user_id: int
    ) -> None:
        """
        低評価回答を無視
        
        Args:
            message_id: メッセージID
            facility_id: 施設ID
            user_id: 無視したユーザーID
        
        Raises:
            ValueError: メッセージが見つからない場合、または既に無視されている場合
        """
        # メッセージを取得
        message = await self.db.get(Message, message_id)
        if not message:
            raise ValueError(f"Message not found: message_id={message_id}")
        
        # 会話を取得して施設IDを確認
        conversation = await self.db.get(Conversation, message.conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: conversation_id={message.conversation_id}")
        
        if conversation.facility_id != facility_id:
            raise ValueError(f"Message does not belong to facility: message_id={message_id}, facility_id={facility_id}")
        
        # 既に無視されているか確認
        existing_result = await self.db.execute(
            select(IgnoredFeedback).where(
                IgnoredFeedback.message_id == message_id,
                IgnoredFeedback.facility_id == facility_id
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Negative feedback already ignored: message_id={message_id}")
        
        # 無視状態を記録
        ignored_feedback = IgnoredFeedback(
            message_id=message_id,
            facility_id=facility_id,
            ignored_by=user_id
        )
        self.db.add(ignored_feedback)
        await self.db.commit()
        
        logger.info(
            f"Negative feedback ignored: message_id={message_id}, facility_id={facility_id}, user_id={user_id}",
            extra={
                "message_id": message_id,
                "facility_id": facility_id,
                "user_id": user_id
            }
        )

