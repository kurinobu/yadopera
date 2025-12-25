"""
FAQ提案サービス
FAQ自動学習のビジネスロジック
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.models.faq_suggestion import FAQSuggestion, FAQSuggestionStatus
from app.models.faq import FAQ, FAQCategory
from app.models.message import Message, MessageRole
from app.models.guest_feedback import GuestFeedback
from app.schemas.faq_suggestion import FAQSuggestionResponse, ApproveSuggestionRequest
from app.schemas.faq import FAQRequest
from app.ai.openai_client import OpenAIClient
from app.services.faq_service import FAQService

logger = logging.getLogger(__name__)


class FAQSuggestionService:
    """
    FAQ提案サービス
    - FAQ提案一覧取得
    - FAQ提案生成（GPT-4o mini）
    - 提案承認（FAQ作成）
    - 提案却下
    """
    
    def __init__(self, db: AsyncSession):
        """
        FAQ提案サービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
        self.openai_client = OpenAIClient()
        self.faq_service = FAQService(db)
    
    async def get_suggestions(
        self,
        facility_id: int,
        status: Optional[str] = None
    ) -> List[FAQSuggestionResponse]:
        """
        FAQ提案一覧取得
        
        Args:
            facility_id: 施設ID
            status: ステータスフィルタ（オプション）
        
        Returns:
            List[FAQSuggestionResponse]: FAQ提案リスト
        """
        query = select(FAQSuggestion).where(FAQSuggestion.facility_id == facility_id)
        
        if status:
            query = query.where(FAQSuggestion.status == status)
        
        query = query.order_by(FAQSuggestion.created_at.desc())
        
        result = await self.db.execute(query)
        suggestions = result.scalars().all()
        
        return [
            FAQSuggestionResponse(
                id=suggestion.id,
                facility_id=suggestion.facility_id,
                source_message_id=suggestion.source_message_id,
                suggested_question=suggestion.suggested_question,
                suggested_answer=suggestion.suggested_answer,
                suggested_category=suggestion.suggested_category,
                language=suggestion.language,
                status=suggestion.status,
                reviewed_at=suggestion.reviewed_at,
                reviewed_by=suggestion.reviewed_by,
                created_faq_id=suggestion.created_faq_id,
                created_at=suggestion.created_at
            )
            for suggestion in suggestions
        ]
    
    async def generate_suggestion(
        self,
        facility_id: int,
        message_id: int
    ) -> FAQSuggestionResponse:
        """
        FAQ提案生成（GPT-4o mini）
        - 質問文自動入力
        - 回答文テンプレート自動生成
        - カテゴリ自動推定
        
        Args:
            facility_id: 施設ID
            message_id: メッセージID（低評価回答または未解決質問）
        
        Returns:
            FAQSuggestionResponse: 生成されたFAQ提案
        
        Raises:
            ValueError: メッセージが見つからない場合
        """
        # メッセージを取得
        message = await self.db.get(Message, message_id)
        if not message:
            raise ValueError(f"Message not found: message_id={message_id}")
        
        if message.conversation.facility_id != facility_id:
            raise ValueError(f"Message does not belong to facility: message_id={message_id}, facility_id={facility_id}")
        
        # 既存の提案を確認
        existing_result = await self.db.execute(
            select(FAQSuggestion).where(
                FAQSuggestion.source_message_id == message_id,
                FAQSuggestion.status == FAQSuggestionStatus.PENDING.value
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            # 既存の提案を返却
            return FAQSuggestionResponse(
                id=existing.id,
                facility_id=existing.facility_id,
                source_message_id=existing.source_message_id,
                suggested_question=existing.suggested_question,
                suggested_answer=existing.suggested_answer,
                suggested_category=existing.suggested_category,
                language=existing.language,
                status=existing.status,
                reviewed_at=existing.reviewed_at,
                reviewed_by=existing.reviewed_by,
                created_faq_id=existing.created_faq_id,
                created_at=existing.created_at
            )
        
        # 質問文を取得（ユーザーメッセージから）
        question = message.content
        
        # 会話の言語を取得
        language = message.conversation.guest_language or "en"
        
        # GPT-4o miniで回答文テンプレートとカテゴリを生成
        prompt = f"""You are an AI assistant helping a guesthouse create FAQ entries.

Guest question: {question}

Please generate:
1. A clear, helpful answer template (2-3 sentences, professional and friendly)
2. A category from: basic, facilities, location, trouble

Format your response as:
ANSWER: [your answer template]
CATEGORY: [category]

Language: {language}"""

        try:
            response_text = await self.openai_client.generate_response(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7,
                language=language
            )
            
            # レスポンスをパース
            suggested_answer = "This is a suggested answer. Please customize it."
            suggested_category = "basic"
            
            if "ANSWER:" in response_text and "CATEGORY:" in response_text:
                parts = response_text.split("CATEGORY:")
                if len(parts) == 2:
                    answer_part = parts[0].replace("ANSWER:", "").strip()
                    category_part = parts[1].strip().lower()
                    
                    if answer_part:
                        suggested_answer = answer_part
                    
                    if category_part in [cat.value for cat in FAQCategory]:
                        suggested_category = category_part
            elif "ANSWER:" in response_text:
                suggested_answer = response_text.split("ANSWER:")[1].strip()
            
            logger.info(f"FAQ suggestion generated: message_id={message_id}, category={suggested_category}")
        
        except Exception as e:
            logger.error(f"Error generating FAQ suggestion: {str(e)}")
            # フォールバック: デフォルト値を使用
            suggested_answer = f"This is a suggested answer template for: {question}. Please customize this answer."
            suggested_category = "basic"
        
        # FAQ提案を作成
        suggestion = FAQSuggestion(
            facility_id=facility_id,
            source_message_id=message_id,
            suggested_question=question,
            suggested_answer=suggested_answer,
            suggested_category=suggested_category,
            language=language,
            status=FAQSuggestionStatus.PENDING.value
        )
        
        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        logger.info(
            f"FAQ suggestion created: suggestion_id={suggestion.id}, message_id={message_id}",
            extra={
                "suggestion_id": suggestion.id,
                "message_id": message_id,
                "facility_id": facility_id
            }
        )
        
        return FAQSuggestionResponse(
            id=suggestion.id,
            facility_id=suggestion.facility_id,
            source_message_id=suggestion.source_message_id,
            suggested_question=suggestion.suggested_question,
            suggested_answer=suggestion.suggested_answer,
            suggested_category=suggestion.suggested_category,
            language=suggestion.language,
            status=suggestion.status,
            reviewed_at=suggestion.reviewed_at,
            reviewed_by=suggestion.reviewed_by,
            created_faq_id=suggestion.created_faq_id,
            created_at=suggestion.created_at
        )
    
    async def approve_suggestion(
        self,
        suggestion_id: int,
        facility_id: int,
        request: ApproveSuggestionRequest,
        user_id: int
    ) -> FAQSuggestionResponse:
        """
        提案承認（FAQ作成）
        
        Args:
            suggestion_id: 提案ID
            facility_id: 施設ID
            request: 承認リクエスト（編集可能）
            user_id: 承認者ID
        
        Returns:
            FAQSuggestionResponse: 更新されたFAQ提案
        
        Raises:
            ValueError: 提案が見つからない場合
        """
        # 提案を取得
        suggestion = await self.db.get(FAQSuggestion, suggestion_id)
        if not suggestion:
            raise ValueError(f"FAQ suggestion not found: suggestion_id={suggestion_id}")
        
        if suggestion.facility_id != facility_id:
            raise ValueError(f"FAQ suggestion does not belong to facility: suggestion_id={suggestion_id}, facility_id={facility_id}")
        
        if suggestion.status != FAQSuggestionStatus.PENDING.value:
            raise ValueError(f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}")
        
        # FAQ作成リクエストを準備（編集可能）
        faq_request = FAQRequest(
            category=request.category or suggestion.suggested_category,
            language=suggestion.language,
            question=request.question or suggestion.suggested_question,
            answer=request.answer or suggestion.suggested_answer,
            priority=request.priority,
            is_active=True
        )
        
        # FAQ作成
        faq = await self.faq_service.create_faq(
            facility_id=facility_id,
            request=faq_request,
            user_id=user_id
        )
        
        # 提案を更新
        suggestion.status = FAQSuggestionStatus.APPROVED.value
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.reviewed_by = user_id
        suggestion.created_faq_id = faq.id
        
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        logger.info(
            f"FAQ suggestion approved: suggestion_id={suggestion_id}, faq_id={faq.id}",
            extra={
                "suggestion_id": suggestion_id,
                "faq_id": faq.id,
                "facility_id": facility_id
            }
        )
        
        return FAQSuggestionResponse(
            id=suggestion.id,
            facility_id=suggestion.facility_id,
            source_message_id=suggestion.source_message_id,
            suggested_question=suggestion.suggested_question,
            suggested_answer=suggestion.suggested_answer,
            suggested_category=suggestion.suggested_category,
            language=suggestion.language,
            status=suggestion.status,
            reviewed_at=suggestion.reviewed_at,
            reviewed_by=suggestion.reviewed_by,
            created_faq_id=suggestion.created_faq_id,
            created_at=suggestion.created_at
        )
    
    async def reject_suggestion(
        self,
        suggestion_id: int,
        facility_id: int,
        user_id: int
    ) -> FAQSuggestionResponse:
        """
        提案却下
        
        Args:
            suggestion_id: 提案ID
            facility_id: 施設ID
            user_id: 却下者ID
        
        Returns:
            FAQSuggestionResponse: 更新されたFAQ提案
        
        Raises:
            ValueError: 提案が見つからない場合
        """
        # 提案を取得
        suggestion = await self.db.get(FAQSuggestion, suggestion_id)
        if not suggestion:
            raise ValueError(f"FAQ suggestion not found: suggestion_id={suggestion_id}")
        
        if suggestion.facility_id != facility_id:
            raise ValueError(f"FAQ suggestion does not belong to facility: suggestion_id={suggestion_id}, facility_id={facility_id}")
        
        if suggestion.status != FAQSuggestionStatus.PENDING.value:
            raise ValueError(f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}")
        
        # 提案を却下
        suggestion.status = FAQSuggestionStatus.REJECTED.value
        suggestion.reviewed_at = datetime.utcnow()
        suggestion.reviewed_by = user_id
        
        await self.db.commit()
        await self.db.refresh(suggestion)
        
        logger.info(
            f"FAQ suggestion rejected: suggestion_id={suggestion_id}",
            extra={
                "suggestion_id": suggestion_id,
                "facility_id": facility_id
            }
        )
        
        return FAQSuggestionResponse(
            id=suggestion.id,
            facility_id=suggestion.facility_id,
            source_message_id=suggestion.source_message_id,
            suggested_question=suggestion.suggested_question,
            suggested_answer=suggestion.suggested_answer,
            suggested_category=suggestion.suggested_category,
            language=suggestion.language,
            status=suggestion.status,
            reviewed_at=suggestion.reviewed_at,
            reviewed_by=suggestion.reviewed_by,
            created_faq_id=suggestion.created_faq_id,
            created_at=suggestion.created_at
        )

