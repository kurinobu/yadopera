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
        
        # 無視されたメッセージIDを除外
        low_rated_message_ids = [msg_id for msg_id in low_rated_message_ids if msg_id not in ignored_message_ids]
        
        if not low_rated_message_ids:
            return []
        
        # メッセージを取得（会話も一緒に取得）
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.id.in_(low_rated_message_ids))
            .options(selectinload(Message.conversation))
        )
        messages = messages_result.scalars().all()
        
        low_rated_answers: List[LowRatedAnswer] = []
        
        for message in messages:
            # 会話内のメッセージを取得（質問を取得するため）
            conversation_messages_result = await self.db.execute(
                select(Message)
                .where(Message.conversation_id == message.conversation_id)
                .order_by(Message.created_at.asc())
            )
            conversation_messages = conversation_messages_result.scalars().all()
            
            # このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
            question = None
            # メッセージのインデックスを見つける
            message_index = None
            for i, msg in enumerate(conversation_messages):
                if msg.id == message.id:
                    message_index = i
                    break
            
            if message_index is not None and message_index > 0:
                # インデックスの前にある最後のUSERロールのメッセージを取得
                for i in range(message_index - 1, -1, -1):
                    if conversation_messages[i].role == MessageRole.USER.value:
                        question = conversation_messages[i].content
                        break
            
            # 質問が見つからない場合はデフォルト値を設定
            if not question:
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

