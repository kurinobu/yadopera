"""
FAQサービス
FAQ管理のビジネスロジック（インテントベース構造）
"""

import logging
import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.faq import FAQ, FAQCategory
from app.models.faq_translation import FAQTranslation
from app.models.user import User
from app.schemas.faq import FAQRequest, FAQUpdateRequest, FAQResponse, FAQTranslationResponse
from app.ai.embeddings import generate_embedding
from app.core.cache import get_cache, set_cache, delete_cache_pattern, cache_key

logger = logging.getLogger(__name__)

# キャッシュTTL（秒）
FAQ_CACHE_TTL = 3600  # 1時間


def normalize_question(question: str) -> str:
    """
    質問文を正規化してintent_keyを生成するためのキーを作成
    
    Args:
        question: 質問文
    
    Returns:
        正規化された質問文（小文字、記号除去、空白正規化）
    """
    if not question:
        return ""
    
    # 小文字に変換
    normalized = question.lower()
    
    # 記号を除去（ハイフン、アンダースコアは保持）
    normalized = re.sub(r'[^\w\s\-_]', '', normalized)
    
    # 複数の空白を1つに
    normalized = re.sub(r'\s+', '_', normalized)
    
    # 前後の空白を削除
    normalized = normalized.strip('_')
    
    # 長さを制限（100文字以内）
    if len(normalized) > 100:
        normalized = normalized[:100]
    
    return normalized


def generate_intent_key(category: str, question: str) -> str:
    """
    インテントキーを生成
    
    Args:
        category: カテゴリ（basic, facilities, location, trouble）
        question: 質問文
    
    Returns:
        インテントキー（例: basic_checkout_time）
    """
    normalized_question = normalize_question(question)
    
    # カテゴリと正規化された質問文を結合
    intent_key = f"{category}_{normalized_question}"
    
    # 長さを制限（100文字以内）
    if len(intent_key) > 100:
        intent_key = intent_key[:100]
    
    return intent_key


class FAQService:
    """
    FAQサービス
    - FAQ一覧取得
    - FAQ作成（埋め込みベクトル自動生成）
    - FAQ更新（埋め込みベクトル自動再生成）
    - FAQ削除
    """
    
    def __init__(self, db: AsyncSession):
        """
        FAQサービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
    
    async def get_faqs(
        self,
        facility_id: int,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[FAQResponse]:
        """
        FAQ一覧取得（キャッシュ対応、インテントベース構造）
        
        Args:
            facility_id: 施設ID
            category: カテゴリフィルタ（オプション）
            is_active: 有効/無効フィルタ（オプション）
        
        Returns:
            List[FAQResponse]: FAQリスト（translationsを含む）
        """
        # キャッシュキー生成
        cache_key_str = cache_key(
            "faq:list",
            facility_id=facility_id,
            category=category,
            is_active=is_active
        )
        
        # キャッシュから取得を試みる
        cached_faqs = await get_cache(cache_key_str)
        if cached_faqs is not None:
            logger.debug(f"FAQ cache hit: {cache_key_str}")
            return [FAQResponse(**faq_dict) for faq_dict in cached_faqs]
        
        # キャッシュミス: データベースから取得
        logger.debug(f"FAQ cache miss: {cache_key_str}")
        query = select(FAQ).where(FAQ.facility_id == facility_id)
        
        if category:
            query = query.where(FAQ.category == category)
        
        if is_active is not None:
            query = query.where(FAQ.is_active == is_active)
        
        # 関連するFAQTranslationを取得（selectinloadを使用）
        query = query.options(selectinload(FAQ.translations))
        query = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc())
        
        result = await self.db.execute(query)
        faqs = result.scalars().all()
        
        # FAQResponseを作成（translationsを含む）
        faq_responses = []
        for faq in faqs:
            # FAQTranslationをFAQTranslationResponseに変換
            translations = [
                FAQTranslationResponse(
                    id=trans.id,
                    faq_id=trans.faq_id,
                    language=trans.language,
                    question=trans.question,
                    answer=trans.answer,
                    created_at=trans.created_at,
                    updated_at=trans.updated_at
                )
                for trans in faq.translations
            ]
            
            faq_responses.append(
                FAQResponse(
                    id=faq.id,
                    facility_id=faq.facility_id,
                    category=faq.category,
                    intent_key=faq.intent_key,
                    translations=translations,
                    priority=faq.priority,
                    is_active=faq.is_active,
                    created_by=faq.created_by,
                    created_at=faq.created_at,
                    updated_at=faq.updated_at
                )
            )
        
        # キャッシュに保存（辞書形式で保存）
        faq_dicts = [faq.model_dump() for faq in faq_responses]
        await set_cache(cache_key_str, faq_dicts, FAQ_CACHE_TTL)
        
        return faq_responses
    
    async def create_faq(
        self,
        facility_id: int,
        request: FAQRequest,
        user_id: int
    ) -> FAQResponse:
        """
        FAQ作成（埋め込みベクトル自動生成、インテントベース構造）
        
        Args:
            facility_id: 施設ID
            request: FAQ作成リクエスト（translationsを含む）
            user_id: 作成者ID
        
        Returns:
            FAQResponse: 作成されたFAQ（translationsを含む）
        """
        # カテゴリバリデーション
        if request.category not in [cat.value for cat in FAQCategory]:
            raise ValueError(f"Invalid category: {request.category}")
        
        # intent_keyを生成（指定されていない場合）
        if request.intent_key:
            intent_key = request.intent_key
        else:
            # 最初の翻訳の質問文を使用してintent_keyを生成
            if not request.translations or len(request.translations) == 0:
                raise ValueError("At least one translation is required")
            first_translation = request.translations[0]
            intent_key = generate_intent_key(request.category, first_translation.question)
        
        # 重複チェック: 同じfacility_id、同じintent_keyのFAQが既に存在するか確認
        existing_faq_result = await self.db.execute(
            select(FAQ).where(
                FAQ.facility_id == facility_id,
                FAQ.intent_key == intent_key
            )
        )
        existing_faq = existing_faq_result.scalar_one_or_none()
        if existing_faq:
            logger.warning(
                f"Duplicate FAQ detected: facility_id={facility_id}, intent_key={intent_key}, "
                f"existing_faq_id={existing_faq.id}"
            )
            raise ValueError(
                f"FAQ with the same intent_key already exists: faq_id={existing_faq.id}, intent_key={intent_key}. "
                f"Please edit the existing FAQ instead of creating a duplicate."
            )
        
        # priorityがNoneの場合はデフォルト値1を使用（念のため）
        priority = request.priority if request.priority is not None else 1
        
        logger.info(
            f"Creating FAQ: facility_id={facility_id}, category={request.category}, intent_key={intent_key}, priority={priority}",
            extra={
                "facility_id": facility_id,
                "category": request.category,
                "intent_key": intent_key,
                "priority": priority,
                "translations_count": len(request.translations)
            }
        )
        
        # FAQ作成
        faq = FAQ(
            facility_id=facility_id,
            category=request.category,
            intent_key=intent_key,
            priority=priority,
            is_active=request.is_active if request.is_active is not None else True,
            created_by=user_id
        )
        
        self.db.add(faq)
        await self.db.flush()
        
        # FAQTranslationを作成（各翻訳に対して）
        translations = []
        for trans_request in request.translations:
            # 埋め込みベクトル生成
            embedding = None
            try:
                combined_text = f"{trans_request.question} {trans_request.answer}"
                logger.debug(f"Generating FAQ translation embedding: language={trans_request.language}, text_length={len(combined_text)}")
                embedding = await generate_embedding(combined_text)
                if embedding:
                    logger.debug(f"FAQ translation embedding generated: language={trans_request.language}, embedding_length={len(embedding)}")
                else:
                    logger.warning(f"Failed to generate FAQ translation embedding (empty result): language={trans_request.language}")
            except Exception as e:
                logger.error(
                    f"Error generating FAQ translation embedding: {str(e)}",
                    exc_info=True,
                    extra={
                        "language": trans_request.language,
                        "question": trans_request.question[:100] if trans_request.question else None,
                        "answer": trans_request.answer[:100] if trans_request.answer else None,
                        "error": str(e)
                    }
                )
                # 埋め込み生成失敗でも翻訳は保存（後で再生成可能）
            
            # FAQTranslation作成
            faq_translation = FAQTranslation(
                faq_id=faq.id,
                language=trans_request.language,
                question=trans_request.question,
                answer=trans_request.answer,
                embedding=embedding
            )
            self.db.add(faq_translation)
            translations.append(faq_translation)
        
        await self.db.flush()
        await self.db.commit()
        
        # リレーションシップを読み込むためにリフレッシュ
        await self.db.refresh(faq)
        # translationsも明示的にリフレッシュ
        for trans in translations:
            await self.db.refresh(trans)
        
        # キャッシュを無効化（ワイルドカードを使用して、すべてのパラメータ組み合わせを無効化）
        try:
            deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
            if deleted_count > 0:
                logger.info(f"FAQ cache deleted: {deleted_count} keys deleted after FAQ creation (faq_id={faq.id}, facility_id={facility_id})")
            else:
                logger.debug(f"FAQ cache deletion: no keys found to delete (faq_id={faq.id}, facility_id={facility_id})")
        except Exception as e:
            logger.error(f"Failed to delete FAQ cache after creation: faq_id={faq.id}, facility_id={facility_id}, error={str(e)}", exc_info=True)
            # エラーが発生しても処理は続行（キャッシュは次回のリクエストで更新される）
        
        logger.info(
            f"FAQ created: faq_id={faq.id}, facility_id={facility_id}, translations_count={len(translations)}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id,
                "category": faq.category,
                "intent_key": faq.intent_key,
                "translations_count": len(translations)
            }
        )
        
        # FAQResponseを作成（translationsを含む）
        translation_responses = [
            FAQTranslationResponse(
                id=trans.id,
                faq_id=trans.faq_id,
                language=trans.language,
                question=trans.question,
                answer=trans.answer,
                created_at=trans.created_at,
                updated_at=trans.updated_at
            )
            for trans in translations
        ]
        
        return FAQResponse(
            id=faq.id,
            facility_id=faq.facility_id,
            category=faq.category,
            intent_key=faq.intent_key,
            translations=translation_responses,
            priority=faq.priority,
            is_active=faq.is_active,
            created_by=faq.created_by,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )
    
    async def update_faq(
        self,
        faq_id: int,
        facility_id: int,
        request: FAQUpdateRequest,
        user_id: int
    ) -> FAQResponse:
        """
        FAQ更新（埋め込みベクトル自動再生成、インテントベース構造）
        
        Args:
            faq_id: FAQ ID
            facility_id: 施設ID
            request: FAQ更新リクエスト（オプショナルフィールド）
            user_id: 更新者ID
        
        Returns:
            FAQResponse: 更新されたFAQ（translationsを含む）
        
        Raises:
            ValueError: FAQが見つからない場合
        """
        # FAQ取得（translationsも含む）
        faq = await self.db.get(FAQ, faq_id)
        if not faq:
            raise ValueError(f"FAQ not found: faq_id={faq_id}")
        
        if faq.facility_id != facility_id:
            raise ValueError(f"FAQ does not belong to facility: faq_id={faq_id}, facility_id={facility_id}")
        
        # 関連するFAQTranslationを取得
        translations_result = await self.db.execute(
            select(FAQTranslation).where(FAQTranslation.faq_id == faq_id)
        )
        existing_translations = {trans.language: trans for trans in translations_result.scalars().all()}
        
        # 更新フィールドを適用（Noneの場合は更新しない）
        if request.category is not None:
            # カテゴリバリデーション
            if request.category not in [cat.value for cat in FAQCategory]:
                raise ValueError(f"Invalid category: {request.category}")
            faq.category = request.category
        
        if request.intent_key is not None:
            # intent_keyの重複チェック（自分自身を除く）
            existing_faq_result = await self.db.execute(
                select(FAQ).where(
                    FAQ.facility_id == facility_id,
                    FAQ.intent_key == request.intent_key,
                    FAQ.id != faq_id
                )
            )
            existing_faq = existing_faq_result.scalar_one_or_none()
            if existing_faq:
                raise ValueError(
                    f"FAQ with the same intent_key already exists: faq_id={existing_faq.id}, intent_key={request.intent_key}"
                )
            faq.intent_key = request.intent_key
        
        if request.priority is not None:
            faq.priority = request.priority
        
        if request.is_active is not None:
            faq.is_active = request.is_active
        
        # translationsの更新または作成
        if request.translations is not None:
            for trans_request in request.translations:
                if trans_request.language in existing_translations:
                    # 既存の翻訳を更新
                    existing_trans = existing_translations[trans_request.language]
                    existing_trans.question = trans_request.question
                    existing_trans.answer = trans_request.answer
                    
                    # 埋め込みベクトル再生成
                    try:
                        combined_text = f"{trans_request.question} {trans_request.answer}"
                        embedding = await generate_embedding(combined_text)
                        if embedding:
                            existing_trans.embedding = embedding
                            logger.debug(f"FAQ translation embedding regenerated: faq_id={faq_id}, language={trans_request.language}")
                        else:
                            logger.warning(f"Failed to regenerate FAQ translation embedding: faq_id={faq_id}, language={trans_request.language}")
                    except Exception as e:
                        logger.error(f"Error regenerating FAQ translation embedding: {str(e)}")
                        # 埋め込み生成失敗でも翻訳は更新（後で再生成可能）
                else:
                    # 新しい翻訳を作成
                    # 埋め込みベクトル生成
                    embedding = None
                    try:
                        combined_text = f"{trans_request.question} {trans_request.answer}"
                        embedding = await generate_embedding(combined_text)
                        if embedding:
                            logger.debug(f"FAQ translation embedding generated: faq_id={faq_id}, language={trans_request.language}")
                        else:
                            logger.warning(f"Failed to generate FAQ translation embedding: faq_id={faq_id}, language={trans_request.language}")
                    except Exception as e:
                        logger.error(f"Error generating FAQ translation embedding: {str(e)}")
                        # 埋め込み生成失敗でも翻訳は作成（後で再生成可能）
                    
                    new_translation = FAQTranslation(
                        faq_id=faq_id,
                        language=trans_request.language,
                        question=trans_request.question,
                        answer=trans_request.answer,
                        embedding=embedding
                    )
                    self.db.add(new_translation)
                    existing_translations[trans_request.language] = new_translation
        
        await self.db.flush()
        await self.db.commit()
        
        # リレーションシップを読み込むためにリフレッシュ
        await self.db.refresh(faq)
        # translationsも再取得
        translations_result = await self.db.execute(
            select(FAQTranslation).where(FAQTranslation.faq_id == faq_id)
        )
        translations = translations_result.scalars().all()
        
        # キャッシュを無効化（ワイルドカードを使用して、すべてのパラメータ組み合わせを無効化）
        try:
            deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
            if deleted_count > 0:
                logger.info(f"FAQ cache deleted: {deleted_count} keys deleted after FAQ update (faq_id={faq.id}, facility_id={facility_id})")
            else:
                logger.debug(f"FAQ cache deletion: no keys found to delete (faq_id={faq.id}, facility_id={facility_id})")
        except Exception as e:
            logger.error(f"Failed to delete FAQ cache after update: faq_id={faq.id}, facility_id={facility_id}, error={str(e)}", exc_info=True)
            # エラーが発生しても処理は続行（キャッシュは次回のリクエストで更新される）
        
        logger.info(
            f"FAQ updated: faq_id={faq.id}, facility_id={facility_id}, translations_count={len(translations)}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id,
                "category": faq.category,
                "intent_key": faq.intent_key,
                "translations_count": len(translations)
            }
        )
        
        # FAQResponseを作成（translationsを含む）
        translation_responses = [
            FAQTranslationResponse(
                id=trans.id,
                faq_id=trans.faq_id,
                language=trans.language,
                question=trans.question,
                answer=trans.answer,
                created_at=trans.created_at,
                updated_at=trans.updated_at
            )
            for trans in translations
        ]
        
        return FAQResponse(
            id=faq.id,
            facility_id=faq.facility_id,
            category=faq.category,
            intent_key=faq.intent_key,
            translations=translation_responses,
            priority=faq.priority,
            is_active=faq.is_active,
            created_by=faq.created_by,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )
    
    async def delete_faq(
        self,
        faq_id: int,
        facility_id: int
    ) -> None:
        """
        FAQ削除
        
        Args:
            faq_id: FAQ ID
            facility_id: 施設ID
        
        Raises:
            ValueError: FAQが見つからない場合
        """
        # FAQ取得
        faq = await self.db.get(FAQ, faq_id)
        if not faq:
            raise ValueError(f"FAQ not found: faq_id={faq_id}")
        
        if faq.facility_id != facility_id:
            raise ValueError(f"FAQ does not belong to facility: faq_id={faq_id}, facility_id={facility_id}")
        
        # キャッシュを先に無効化（削除前に無効化することで、古いデータが残らないようにする）
        try:
            deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
            if deleted_count > 0:
                logger.debug(f"FAQ cache deleted before deletion: {deleted_count} keys deleted (faq_id={faq.id}, facility_id={facility_id})")
        except Exception as e:
            logger.warning(f"Failed to delete FAQ cache before deletion: faq_id={faq.id}, facility_id={facility_id}, error={str(e)}", exc_info=True)
            # エラーが発生しても処理は続行
        
        # FAQを削除
        await self.db.delete(faq)
        await self.db.commit()
        
        # 念のため、再度キャッシュを無効化
        try:
            deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
            if deleted_count > 0:
                logger.info(f"FAQ cache deleted after deletion: {deleted_count} keys deleted (faq_id={faq.id}, facility_id={facility_id})")
            else:
                logger.debug(f"FAQ cache deletion after deletion: no keys found to delete (faq_id={faq.id}, facility_id={facility_id})")
        except Exception as e:
            logger.error(f"Failed to delete FAQ cache after deletion: faq_id={faq.id}, facility_id={facility_id}, error={str(e)}", exc_info=True)
            # エラーが発生しても処理は続行（キャッシュは次回のリクエストで更新される）
        
        logger.info(
            f"FAQ deleted: faq_id={faq.id}, facility_id={facility_id}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id
            }
        )

