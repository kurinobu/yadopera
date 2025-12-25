"""
FAQ提案サービス
FAQ自動学習のビジネスロジック
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.models.faq_suggestion import FAQSuggestion, FAQSuggestionStatus
from app.models.faq import FAQ, FAQCategory
from app.models.message import Message, MessageRole
from app.models.guest_feedback import GuestFeedback
from app.models.escalation import Escalation
from app.models.processed_feedback import ProcessedFeedback
from app.schemas.faq_suggestion import FAQSuggestionResponse, ApproveSuggestionRequest
from app.schemas.faq import FAQRequest, FAQTranslationRequest
from app.ai.openai_client import OpenAIClient
from app.services.faq_service import FAQService

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    テキストの言語を検出（簡易版）
    - 日本語文字（ひらがな、カタカナ、漢字）が含まれていれば "ja"
    - そうでなければ "en"
    
    Args:
        text: 検出対象のテキスト
    
    Returns:
        str: 言語コード（"ja" または "en"）
    """
    import re
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    if japanese_pattern.search(text):
        return "ja"
    return "en"


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
        # メッセージを取得（conversationを事前にロード）
        query = select(Message).options(joinedload(Message.conversation)).where(Message.id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise ValueError(f"Message not found: message_id={message_id}")
        
        if message.conversation.facility_id != facility_id:
            raise ValueError(f"Message does not belong to facility: message_id={message_id}, facility_id={facility_id}")
        
        # USERロールのメッセージに対してFAQ提案を生成しようとした場合、エラーを発生させる
        if message.role == MessageRole.USER.value:
            logger.error(
                f"Attempted to generate FAQ suggestion for USER role message: "
                f"message_id={message_id}, facility_id={facility_id}, "
                f"conversation_id={message.conversation_id}, "
                f"content={message.content[:100] if message.content else 'None'}..."
            )
            # データ不整合の可能性をログに記録
            logger.error(
                f"Data inconsistency detected: message_id={message_id} is USER role but was included in negative feedbacks. "
                f"This should not happen as feedback_service.py filters for ASSISTANT role messages only."
            )
            raise ValueError(
                f"FAQ suggestion cannot be generated for USER role messages. "
                f"Please specify an ASSISTANT role message (message_id={message_id} is USER role). "
                f"USER role messages are user questions, not AI responses that need improvement. "
                f"If you see this error, it indicates a data inconsistency issue."
            )
        
        # 既存の提案を確認（最新の1件を取得）
        existing_result = await self.db.execute(
            select(FAQSuggestion).where(
                FAQSuggestion.source_message_id == message_id,
                FAQSuggestion.status == FAQSuggestionStatus.PENDING.value
            ).order_by(FAQSuggestion.created_at.desc()).limit(1)
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
        # メッセージがASSISTANTの場合は、同じ会話のUSERメッセージを取得
        if message.role == MessageRole.ASSISTANT.value:
            # 同じ会話の全メッセージを時系列順で取得（created_atとidでソートして順序を確実にする）
            conversation_messages_result = await self.db.execute(
                select(Message)
                .where(Message.conversation_id == message.conversation_id)
                .order_by(Message.created_at.asc(), Message.id.asc())
            )
            conversation_messages = conversation_messages_result.scalars().all()
            
            # このメッセージ（AI応答）の前にあるユーザーメッセージ（質問）を取得
            def pick_question_before(index: int) -> str | None:
                """
                直前以前のUSERメッセージから「質問らしい」ものを優先的に選ぶ。
                疑問符を含むものを優先し、それがなければ直近のUSERロールを返す。
                """
                logger.debug(
                    f"pick_question_before: index={index}, total_messages={len(conversation_messages)}, "
                    f"message_id={message_id}, conversation_id={message.conversation_id}"
                )
                
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
                        logger.debug(
                            f"Found question with question mark: message_id={msg.id}, content={content[:50]}..."
                        )
                        return content
                
                # 疑問符がない場合は、直近のUSERロールを返す
                for i in range(index - 1, -1, -1):
                    msg = conversation_messages[i]
                    if msg.role == MessageRole.USER.value:
                        content = (msg.content or "").strip()
                        if content:
                            logger.debug(
                                f"Found question without question mark: message_id={msg.id}, content={content[:50]}..."
                            )
                            return content
                
                logger.warning(
                    f"No USER message found before assistant message: message_id={message_id}, "
                    f"conversation_id={message.conversation_id}, index={index}"
                )
                return None

            # メッセージのインデックスを見つける
            message_index = None
            for i, msg in enumerate(conversation_messages):
                if msg.id == message.id:
                    message_index = i
                    break

            if message_index is None:
                logger.error(
                    f"Message not found in conversation: message_id={message_id}, conversation_id={message.conversation_id}, "
                    f"total_messages={len(conversation_messages)}"
                )
                raise ValueError(f"Message not found in conversation: message_id={message_id}")

            if message_index == 0:
                logger.error(
                    f"Assistant message is the first message in conversation: message_id={message_id}, "
                    f"conversation_id={message.conversation_id}"
                )
                raise ValueError(
                    f"Assistant message is the first message in conversation: message_id={message_id}. "
                    f"Please ensure there is a USER message before this ASSISTANT message."
                )

            question = pick_question_before(message_index)

            if not question:
                # USERメッセージが見つからない場合、エラー（回答文を質問文として使用しない）
                logger.error(
                    f"User message not found for assistant message: message_id={message_id}, "
                    f"conversation_id={message.conversation_id}, message_index={message_index}, "
                    f"total_messages={len(conversation_messages)}, "
                    f"message_content={message.content[:100] if message.content else 'None'}..."
                )
                # 会話履歴の詳細をログに記録
                for i, msg in enumerate(conversation_messages[:message_index + 1]):
                    logger.error(
                        f"  Message[{i}]: id={msg.id}, role={msg.role}, "
                        f"content={msg.content[:50] if msg.content else 'None'}..."
                    )
                raise ValueError(
                    f"User message not found for assistant message: message_id={message_id}. "
                    f"Please ensure there is a USER message before this ASSISTANT message. "
                    f"Conversation has {len(conversation_messages)} messages."
                )
            
            existing_answer = message.content  # 既存の回答（改善対象）
        else:
            # USERメッセージの場合
            question = message.content
            existing_answer = None  # 新規FAQ提案
        
        # 会話の言語を取得
        conversation_language = message.conversation.guest_language or "en"
        
        # 質問文の言語を検出
        question_language = detect_language(question)
        
        # 言語の優先順位: 質問文の言語 > 会話の言語設定
        # 質問文が日本語の場合は日本語、そうでなければ会話の言語設定を使用
        language = question_language if question_language == "ja" else conversation_language
        
        # GPT-4o miniで回答文テンプレートとカテゴリを生成
        if existing_answer:
            # ゲストフィードバック連動の場合：既存の回答を改善
            prompt = f"""You are an AI assistant helping a guesthouse improve FAQ entries.

Guest question: {question}
Current answer (needs improvement): {existing_answer}

Please generate:
1. An improved answer template (2-3 sentences, professional and friendly, addressing the guest's concern better)
2. A category from: basic, facilities, location, trouble

Format your response as:
ANSWER: [your improved answer template]
CATEGORY: [category]

Language: {language}"""
        else:
            # 未解決質問の場合：新規FAQ提案
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
            if existing_answer:
                # ゲストフィードバック連動の場合：既存の回答を少し改善したテンプレート
                suggested_answer = f"This is an improved answer template. Original: {existing_answer[:100]}... Please customize this answer."
            else:
                # 未解決質問の場合：新規FAQ提案
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
        logger.info(
            f"Approving FAQ suggestion: suggestion_id={suggestion_id}, facility_id={facility_id}, user_id={user_id}",
            extra={
                "suggestion_id": suggestion_id,
                "facility_id": facility_id,
                "user_id": user_id
            }
        )
        
        try:
            # 提案を取得
            logger.info(f"Fetching FAQ suggestion: suggestion_id={suggestion_id}")
            suggestion = await self.db.get(FAQSuggestion, suggestion_id)
            if not suggestion:
                logger.error(
                    f"FAQ suggestion not found: suggestion_id={suggestion_id}, facility_id={facility_id}",
                    extra={
                        "suggestion_id": suggestion_id,
                        "facility_id": facility_id,
                        "user_id": user_id
                    }
                )
                raise ValueError(
                    f"FAQ suggestion not found: suggestion_id={suggestion_id}. "
                    f"Please refresh the page and try again."
                )
            
            logger.info(
                f"FAQ suggestion found: suggestion_id={suggestion_id}, status={suggestion.status}, facility_id={suggestion.facility_id}",
                extra={
                    "suggestion_id": suggestion_id,
                    "status": suggestion.status,
                    "facility_id": suggestion.facility_id
                }
            )
            
            if suggestion.facility_id != facility_id:
                logger.error(
                    f"FAQ suggestion facility mismatch: suggestion_id={suggestion_id}, suggestion.facility_id={suggestion.facility_id}, facility_id={facility_id}",
                    extra={
                        "suggestion_id": suggestion_id,
                        "suggestion_facility_id": suggestion.facility_id,
                        "facility_id": facility_id
                    }
                )
                raise ValueError(f"FAQ suggestion does not belong to facility: suggestion_id={suggestion_id}, facility_id={facility_id}")
            
            if suggestion.status != FAQSuggestionStatus.PENDING.value:
                logger.error(
                    f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}",
                    extra={
                        "suggestion_id": suggestion_id,
                        "status": suggestion.status
                    }
                )
                raise ValueError(f"FAQ suggestion is not pending: suggestion_id={suggestion_id}, status={suggestion.status}")
            
            # FAQ作成リクエストを準備（編集可能）
            # priorityがNoneの場合はデフォルト値1を使用（念のため）
            priority = request.priority if request.priority is not None else 1
            
            logger.info(
                f"Creating FAQ request: suggestion_id={suggestion_id}",
                extra={
                    "suggestion_id": suggestion_id,
                    "request_category": request.category,
                    "suggestion_category": suggestion.suggested_category,
                    "request_priority": request.priority,
                    "final_priority": priority
                }
            )
            
            # 必須フィールドのバリデーション
            category = request.category or suggestion.suggested_category
            question = request.question or suggestion.suggested_question
            answer = request.answer or suggestion.suggested_answer
            
            if not category:
                raise ValueError(f"Category is required: suggestion_id={suggestion_id}")
            if not question:
                raise ValueError(f"Question is required: suggestion_id={suggestion_id}")
            if not answer:
                raise ValueError(f"Answer is required: suggestion_id={suggestion_id}")
            
            # FAQRequestを新しい構造（インテントベース）に修正
            # translationsリストに1つの翻訳を含める
            faq_request = FAQRequest(
                category=category,
                intent_key=None,  # 自動生成される
                translations=[
                    FAQTranslationRequest(
                        language=suggestion.language,
                        question=question,
                        answer=answer
                    )
                ],
                priority=priority,
                is_active=True
            )
            # ログメッセージ用に最初の翻訳を取得
            first_translation = faq_request.translations[0] if faq_request.translations else None
            logger.info(
                f"FAQ request created: category={faq_request.category}, language={first_translation.language if first_translation else 'unknown'}, priority={faq_request.priority}, question_length={len(first_translation.question) if first_translation else 0}, answer_length={len(first_translation.answer) if first_translation else 0}, translations_count={len(faq_request.translations)}",
                extra={
                    "category": faq_request.category,
                    "language": first_translation.language if first_translation else None,
                    "priority": faq_request.priority,
                    "question_length": len(first_translation.question) if first_translation else 0,
                    "answer_length": len(first_translation.answer) if first_translation else 0,
                    "translations_count": len(faq_request.translations)
                }
            )
            
            # FAQ作成
            logger.info(
                f"Creating FAQ: facility_id={facility_id}, user_id={user_id}",
                extra={
                    "facility_id": facility_id,
                    "user_id": user_id
                }
            )
            try:
                faq = await self.faq_service.create_faq(
                    facility_id=facility_id,
                    request=faq_request,
                    user_id=user_id
                )
                logger.info(
                    f"FAQ created successfully: faq_id={faq.id}",
                    extra={
                        "faq_id": faq.id,
                        "facility_id": facility_id
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error creating FAQ: {str(e)}",
                    exc_info=True,
                    extra={
                        "suggestion_id": suggestion_id,
                        "facility_id": facility_id,
                        "user_id": user_id,
                        "error": str(e)
                    }
                )
                raise
            
            # エスカレーションを解決済みにする
            try:
                # メッセージを取得（conversationを事前にロード）
                message_query = select(Message).options(joinedload(Message.conversation)).where(Message.id == suggestion.source_message_id)
                message_result = await self.db.execute(message_query)
                message = message_result.scalar_one_or_none()
                
                if message and message.conversation_id:
                    # 対応するエスカレーションを取得（未解決のもの）
                    escalation_query = select(Escalation).where(
                        Escalation.conversation_id == message.conversation_id,
                        Escalation.facility_id == facility_id,
                        Escalation.resolved_at.is_(None)
                    ).order_by(Escalation.created_at.desc()).limit(1)
                    
                    escalation_result = await self.db.execute(escalation_query)
                    escalation = escalation_result.scalar_one_or_none()
                    
                    if escalation:
                        # エスカレーションを解決済みにする
                        escalation.resolved_at = datetime.utcnow()
                        escalation.resolved_by = user_id
                        escalation.resolution_notes = f"FAQ created from suggestion {suggestion_id}"
                        await self.db.flush()
                        
                        logger.info(
                            f"Escalation resolved: escalation_id={escalation.id}, suggestion_id={suggestion_id}",
                            extra={
                                "escalation_id": escalation.id,
                                "suggestion_id": suggestion_id,
                                "faq_id": faq.id
                            }
                        )
                    else:
                        logger.warning(
                            f"No unresolved escalation found for conversation_id={message.conversation_id}, suggestion_id={suggestion_id}",
                            extra={
                                "conversation_id": message.conversation_id,
                                "suggestion_id": suggestion_id
                            }
                        )
                else:
                    logger.warning(
                        f"Message not found or conversation_id is None: source_message_id={suggestion.source_message_id}, suggestion_id={suggestion_id}",
                        extra={
                            "source_message_id": suggestion.source_message_id,
                            "suggestion_id": suggestion_id
                        }
                    )
            except Exception as e:
                # エスカレーション解決の失敗はFAQ作成を妨げない（ログのみ記録）
                logger.error(
                    f"Error resolving escalation: {str(e)}",
                    exc_info=True,
                    extra={
                        "suggestion_id": suggestion_id,
                        "source_message_id": suggestion.source_message_id,
                        "error": str(e)
                    }
                )
            
            # 提案を更新
            logger.info(
                f"Updating FAQ suggestion: suggestion_id={suggestion_id}, faq_id={faq.id}",
                extra={
                    "suggestion_id": suggestion_id,
                    "faq_id": faq.id
                }
            )
            suggestion.status = FAQSuggestionStatus.APPROVED.value
            suggestion.reviewed_at = datetime.utcnow()
            suggestion.reviewed_by = user_id
            suggestion.created_faq_id = faq.id
            
            # FAQ承認により処理済みとなった低評価回答を記録
            try:
                # 既に処理済みとして記録されているか確認
                processed_result = await self.db.execute(
                    select(ProcessedFeedback).where(
                        ProcessedFeedback.message_id == suggestion.source_message_id,
                        ProcessedFeedback.facility_id == facility_id
                    )
                )
                existing_processed = processed_result.scalar_one_or_none()
                
                if not existing_processed:
                    # 処理済みとして記録
                    processed_feedback = ProcessedFeedback(
                        message_id=suggestion.source_message_id,
                        facility_id=facility_id,
                        faq_suggestion_id=suggestion_id,
                        processed_by=user_id
                    )
                    self.db.add(processed_feedback)
                    logger.info(
                        f"Processed feedback recorded after FAQ approval: message_id={suggestion.source_message_id}, "
                        f"suggestion_id={suggestion_id}, faq_id={faq.id}",
                        extra={
                            "message_id": suggestion.source_message_id,
                            "suggestion_id": suggestion_id,
                            "faq_id": faq.id,
                            "facility_id": facility_id
                        }
                    )
                else:
                    logger.debug(
                        f"Feedback already processed: message_id={suggestion.source_message_id}, "
                        f"suggestion_id={suggestion_id}",
                        extra={
                            "message_id": suggestion.source_message_id,
                            "suggestion_id": suggestion_id
                        }
                    )
            except Exception as e:
                # 処理済み記録の失敗はFAQ作成を妨げない（ログのみ記録）
                logger.error(
                    f"Error recording processed feedback after FAQ approval: {str(e)}",
                    exc_info=True,
                    extra={
                        "suggestion_id": suggestion_id,
                        "source_message_id": suggestion.source_message_id,
                        "error": str(e)
                    }
                )
            
            await self.db.commit()
            await self.db.refresh(suggestion)
            
            logger.info(
                f"FAQ suggestion approved successfully: suggestion_id={suggestion_id}, faq_id={faq.id}",
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
        except ValueError as e:
            logger.error(
                f"ValueError in approve_suggestion: {str(e)}",
                extra={
                    "suggestion_id": suggestion_id,
                    "facility_id": facility_id,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in approve_suggestion: {str(e)}",
                exc_info=True,
                extra={
                    "suggestion_id": suggestion_id,
                    "facility_id": facility_id,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise
    
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

