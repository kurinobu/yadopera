"""
RAG統合型AI対話エンジン
"""

import time
import logging
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.ai.embeddings import generate_embedding
from app.ai.vector_search import search_similar_faqs
from app.ai.openai_client import OpenAIClient
from app.ai.fallback import get_fallback_message
from app.models.facility import Facility
from app.models.faq import FAQ
from app.schemas.chat import RAGEngineResponse, EscalationInfo

logger = logging.getLogger(__name__)


class RAGChatEngine:
    """
    RAG統合型AI対話エンジン（v0.3詳細化）
    """
    
    def __init__(self, db: AsyncSession):
        """
        RAGエンジン初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
        self.openai_client = OpenAIClient()
    
    async def process_message(
        self,
        message: str,
        facility_id: int,
        session_id: str,
        language: str = "en"
    ) -> RAGEngineResponse:
        """
        RAG統合型でメッセージを処理（v0.3詳細化）
        
        Args:
            message: ゲストのメッセージ
            facility_id: 施設ID
            session_id: セッションID
            language: 言語コード（デフォルト: "en"）
        
        Returns:
            RAGEngineResponse: RAGエンジンのレスポンス（中間形式）
        """
        start_time = time.time()
        
        try:
            # Step 1: 埋め込みベクトル生成
            question_embedding = await generate_embedding(message)
            if not question_embedding:
                logger.error("Failed to generate embedding for question")
                # フォールバック: 空の埋め込みで検索を続行（結果は空になる）
                question_embedding = []
            
            # Step 2: pgvector検索（Top 3 FAQ取得）
            similar_faqs = await search_similar_faqs(
                facility_id=facility_id,
                embedding=question_embedding,
                top_k=3,
                threshold=0.7,  # コサイン類似度閾値
                db=self.db
            )
            
            # Step 2.5: FAQのtranslationsを読み込む（インテントベース構造対応）
            if similar_faqs:
                faq_ids = [faq.id for faq in similar_faqs]
                faqs_with_translations_result = await self.db.execute(
                    select(FAQ)
                    .where(FAQ.id.in_(faq_ids))
                    .options(selectinload(FAQ.translations))
                )
                similar_faqs = faqs_with_translations_result.scalars().all()
            
            # Step 3: コンテキスト構築
            facility = await self._get_facility_info(facility_id)
            if not facility:
                logger.error(f"Facility not found: {facility_id}")
                # エラーレスポンスを返す（後で実装）
                raise ValueError(f"Facility not found: {facility_id}")
            
            context = self._build_context(facility, similar_faqs, message, language)
            
            # Step 4: GPT-4o-mini回答生成
            ai_response = await self.openai_client.generate_response(
                prompt=context,
                max_tokens=200,
                temperature=0.7,
                language=language
            )
            
            # Step 5: 信頼度スコア計算（後続ステップで実装）
            # TODO: confidence.pyを実装後に有効化
            # from app.ai.confidence import calculate_confidence
            # confidence = await calculate_confidence(
            #     response_text=ai_response,
            #     similar_faqs=similar_faqs,
            #     question=message,
            #     facility_id=facility_id,
            #     db=self.db
            # )
            confidence = Decimal("0.7")  # 暫定値
            
            # Step 6: エスカレーション判定（後続ステップで実装）
            # TODO: escalation_serviceを実装後に有効化
            # from app.services.escalation_service import check_escalation_needed
            # escalation_info = await check_escalation_needed(
            #     facility_id=facility_id,
            #     confidence=confidence,
            #     message=message,
            #     session_id=session_id,
            #     db=self.db
            # )
            escalation_info = EscalationInfo(
                needed=False,
                mode=None,
                trigger_type=None,
                reason=None,
                notified=None
            )  # 暫定値
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # RAGEngineResponseを返す（メッセージ保存はchat_service.pyで実施）
            return RAGEngineResponse(
                response=ai_response,
                ai_confidence=confidence,
                matched_faq_ids=[faq.id for faq in similar_faqs],
                response_time_ms=response_time_ms,
                escalation=escalation_info
            )
        
        except Exception as e:
            logger.error(
                f"Error processing message: {e}",
                exc_info=True,
                extra={
                    "facility_id": facility_id,
                    "session_id": session_id,
                    "language": language
                }
            )
            # エラー時はフォールバックレスポンスを返す
            return RAGEngineResponse(
                response=get_fallback_message(language),
                ai_confidence=Decimal("0.0"),
                matched_faq_ids=[],
                response_time_ms=int((time.time() - start_time) * 1000),
                escalation=EscalationInfo(
                    needed=True,
                    mode="normal",
                    trigger_type="error",
                    reason=f"Error processing message: {str(e)}",
                    notified=False
                )
            )
    
    async def _get_facility_info(self, facility_id: int) -> Optional[Facility]:
        """
        施設情報取得
        
        Args:
            facility_id: 施設ID
        
        Returns:
            Facility: 施設情報、見つからない場合はNone
        """
        try:
            query = select(Facility).where(Facility.id == facility_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching facility info: {e}", exc_info=True)
            return None
    
    def _build_context(
        self,
        facility: Facility,
        similar_faqs: List[FAQ],
        question: str,
        language: str = "en"
    ) -> str:
        """
        コンテキスト構築（約600トークン、インテントベース構造対応）
        
        Args:
            facility: 施設情報
            similar_faqs: 類似FAQリスト（インテント単位）
            question: ゲストの質問
            language: ゲストの言語コード（デフォルト: "en"）
        
        Returns:
            str: 構築されたコンテキスト
        """
        # 関連FAQ Top 3（約300トークン）
        # FAQから適切な言語の翻訳を取得
        faq_context_parts = []
        for faq in similar_faqs[:3]:
            # FAQのtranslationsから適切な言語の翻訳を取得
            # 言語が一致するものを優先し、なければ最初の翻訳を使用
            translation = None
            if hasattr(faq, 'translations') and faq.translations:
                # 言語が一致する翻訳を探す
                for trans in faq.translations:
                    if trans.language == language:
                        translation = trans
                        break
                # 一致する言語がない場合は最初の翻訳を使用
                if not translation:
                    translation = faq.translations[0]
            
            if translation:
                faq_context_parts.append(f"Q: {translation.question}\nA: {translation.answer}")
            else:
                # 翻訳が見つからない場合（リレーションシップが読み込まれていない可能性）
                logger.warning(f"FAQ translation not found for faq_id={faq.id}, language={language}")
                # フォールバック: 空のFAQとして扱う
                faq_context_parts.append("Q: [Translation not available]\nA: [Translation not available]")
        
        faq_context = "\n".join(faq_context_parts) if faq_context_parts else "No relevant FAQs found."
        
        # 施設基本情報（約150トークン）
        facility_info = f"""
Facility: {facility.name}
Check-in: {facility.check_in_time}
Check-out: {facility.check_out_time}
WiFi SSID: {facility.wifi_ssid or "Not available"}
House Rules: {(facility.house_rules or "")[:500]}
Local Info: {(facility.local_info or "")[:500]}
"""
        
        # システムプロンプト（約100トークン）
        system_prompt = """
You are a helpful assistant for a guesthouse.
Answer guests' questions based on the provided FAQs and facility information.
Be friendly, concise (under 200 characters), and helpful.
If you cannot answer confidently, suggest contacting staff.
"""
        
        # ゲスト質問（約50トークン）
        guest_question = f"Guest question: {question}"
        
        # コンテキスト結合
        context = f"""{system_prompt}

## Facility Information:
{facility_info}

## Relevant FAQs:
{faq_context}

## Guest's Question:
{guest_question}

## Your Response:
"""
        
        return context

