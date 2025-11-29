"""
FAQサービス
FAQ管理のビジネスロジック
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.faq import FAQ, FAQCategory
from app.models.user import User
from app.schemas.faq import FAQRequest, FAQUpdateRequest, FAQResponse
from app.ai.embeddings import generate_faq_embedding

logger = logging.getLogger(__name__)


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
        FAQ一覧取得
        
        Args:
            facility_id: 施設ID
            category: カテゴリフィルタ（オプション）
            is_active: 有効/無効フィルタ（オプション）
        
        Returns:
            List[FAQResponse]: FAQリスト
        """
        query = select(FAQ).where(FAQ.facility_id == facility_id)
        
        if category:
            query = query.where(FAQ.category == category)
        
        if is_active is not None:
            query = query.where(FAQ.is_active == is_active)
        
        query = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc())
        
        result = await self.db.execute(query)
        faqs = result.scalars().all()
        
        return [
            FAQResponse(
                id=faq.id,
                facility_id=faq.facility_id,
                category=faq.category,
                language=faq.language,
                question=faq.question,
                answer=faq.answer,
                priority=faq.priority,
                is_active=faq.is_active,
                created_by=faq.created_by,
                created_at=faq.created_at,
                updated_at=faq.updated_at
            )
            for faq in faqs
        ]
    
    async def create_faq(
        self,
        facility_id: int,
        request: FAQRequest,
        user_id: int
    ) -> FAQResponse:
        """
        FAQ作成（埋め込みベクトル自動生成）
        
        Args:
            facility_id: 施設ID
            request: FAQ作成リクエスト
            user_id: 作成者ID
        
        Returns:
            FAQResponse: 作成されたFAQ
        """
        # カテゴリバリデーション
        if request.category not in [cat.value for cat in FAQCategory]:
            raise ValueError(f"Invalid category: {request.category}")
        
        # FAQ作成
        faq = FAQ(
            facility_id=facility_id,
            category=request.category,
            language=request.language,
            question=request.question,
            answer=request.answer,
            priority=request.priority,
            is_active=request.is_active if request.is_active is not None else True,
            created_by=user_id
        )
        
        self.db.add(faq)
        await self.db.flush()
        
        # 埋め込みベクトル生成
        try:
            embedding = await generate_faq_embedding(faq)
            if embedding:
                faq.embedding = embedding
                await self.db.flush()
                logger.info(f"FAQ embedding generated: faq_id={faq.id}")
            else:
                logger.warning(f"Failed to generate FAQ embedding: faq_id={faq.id}")
        except Exception as e:
            logger.error(f"Error generating FAQ embedding: {str(e)}")
            # 埋め込み生成失敗でもFAQは保存（後で再生成可能）
        
        await self.db.commit()
        await self.db.refresh(faq)
        
        logger.info(
            f"FAQ created: faq_id={faq.id}, facility_id={facility_id}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id,
                "category": faq.category
            }
        )
        
        return FAQResponse(
            id=faq.id,
            facility_id=faq.facility_id,
            category=faq.category,
            language=faq.language,
            question=faq.question,
            answer=faq.answer,
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
        FAQ更新（埋め込みベクトル自動再生成）
        
        Args:
            faq_id: FAQ ID
            facility_id: 施設ID
            request: FAQ更新リクエスト（オプショナルフィールド）
            user_id: 更新者ID
        
        Returns:
            FAQResponse: 更新されたFAQ
        
        Raises:
            ValueError: FAQが見つからない場合
        """
        # FAQ取得
        faq = await self.db.get(FAQ, faq_id)
        if not faq:
            raise ValueError(f"FAQ not found: faq_id={faq_id}")
        
        if faq.facility_id != facility_id:
            raise ValueError(f"FAQ does not belong to facility: faq_id={faq_id}, facility_id={facility_id}")
        
        # 更新フィールドを適用（Noneの場合は更新しない）
        need_embedding_update = False
        
        if request.category is not None:
            # カテゴリバリデーション
            if request.category not in [cat.value for cat in FAQCategory]:
                raise ValueError(f"Invalid category: {request.category}")
            faq.category = request.category
            need_embedding_update = True
        
        if request.language is not None:
            faq.language = request.language
            need_embedding_update = True
        
        if request.question is not None:
            faq.question = request.question
            need_embedding_update = True
        
        if request.answer is not None:
            faq.answer = request.answer
            need_embedding_update = True
        
        if request.priority is not None:
            faq.priority = request.priority
        
        if request.is_active is not None:
            faq.is_active = request.is_active
        
        await self.db.flush()
        
        # 埋め込みベクトル再生成（質問または回答が変更された場合）
        if need_embedding_update:
            try:
                embedding = await generate_faq_embedding(faq)
                if embedding:
                    faq.embedding = embedding
                    await self.db.flush()
                    logger.info(f"FAQ embedding regenerated: faq_id={faq.id}")
                else:
                    logger.warning(f"Failed to regenerate FAQ embedding: faq_id={faq.id}")
            except Exception as e:
                logger.error(f"Error regenerating FAQ embedding: {str(e)}")
                # 埋め込み生成失敗でもFAQは更新（後で再生成可能）
        
        await self.db.commit()
        await self.db.refresh(faq)
        
        logger.info(
            f"FAQ updated: faq_id={faq.id}, facility_id={facility_id}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id,
                "category": faq.category
            }
        )
        
        return FAQResponse(
            id=faq.id,
            facility_id=faq.facility_id,
            category=faq.category,
            language=faq.language,
            question=faq.question,
            answer=faq.answer,
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
        
        await self.db.delete(faq)
        await self.db.commit()
        
        logger.info(
            f"FAQ deleted: faq_id={faq.id}, facility_id={facility_id}",
            extra={
                "faq_id": faq.id,
                "facility_id": facility_id
            }
        )

