"""
事業者向けFAQサービス
FAQの取得・検索・管理機能を提供
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from app.models.operator_help import OperatorFaq, OperatorFaqTranslation
from app.redis_client import redis_client
import json
import logging

logger = logging.getLogger(__name__)


class OperatorFaqService:
    """事業者向けFAQサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_ttl = 300  # 5分
    
    async def get_faqs(
        self,
        language: str = 'ja',
        category: Optional[str] = None,
        is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """
        FAQ一覧取得（キャッシュ対応）
        
        Args:
            language: 言語コード (ja, en)
            category: カテゴリフィルタ (optional)
            is_active: 有効フラグ
        
        Returns:
            FAQ辞書のリスト
        """
        # キャッシュキー生成
        cache_key = f"operator_faqs:{language}:{category or 'all'}:{is_active}"
        
        # キャッシュチェック
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"FAQ cache hit: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        # データベースクエリ
        query = (
            select(OperatorFaq)
            .options(selectinload(OperatorFaq.translations))
            .where(OperatorFaq.is_active == is_active)
            .order_by(OperatorFaq.display_order, OperatorFaq.id)
        )
        
        if category:
            query = query.where(OperatorFaq.category == category)
        
        result = await self.db.execute(query)
        faqs = result.scalars().all()
        
        # レスポンス構築
        faq_list = []
        for faq in faqs:
            # 指定言語の翻訳を取得
            translation = next(
                (t for t in faq.translations if t.language == language),
                None
            )
            
            if translation:
                faq_list.append({
                    'id': faq.id,
                    'category': faq.category,
                    'intent_key': faq.intent_key,
                    'question': translation.question,
                    'answer': translation.answer,
                    'keywords': translation.keywords,
                    'related_url': translation.related_url,
                    'display_order': faq.display_order
                })
        
        # キャッシュに保存
        try:
            await redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(faq_list, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
        
        logger.info(f"FAQs fetched: {len(faq_list)} items (language={language}, category={category})")
        return faq_list
    
    async def search_faqs(
        self,
        query: str,
        language: str = 'ja',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        FAQ検索（全文検索）
        
        Args:
            query: 検索クエリ
            language: 言語コード
            limit: 取得件数上限
        
        Returns:
            検索結果FAQ辞書のリスト
        """
        if not query or len(query) < 2:
            return []
        
        # LIKE検索（PostgreSQL全文検索は今後実装）
        search_pattern = f"%{query}%"
        
        stmt = (
            select(OperatorFaqTranslation)
            .join(OperatorFaq)
            .where(
                OperatorFaq.is_active == True,
                OperatorFaqTranslation.language == language,
                or_(
                    OperatorFaqTranslation.question.ilike(search_pattern),
                    OperatorFaqTranslation.answer.ilike(search_pattern),
                    OperatorFaqTranslation.keywords.ilike(search_pattern)
                )
            )
            .options(selectinload(OperatorFaqTranslation.faq))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        translations = result.scalars().all()
        
        # レスポンス構築
        results = []
        for trans in translations:
            results.append({
                'id': trans.faq.id,
                'category': trans.faq.category,
                'question': trans.question,
                'answer': trans.answer,
                'keywords': trans.keywords,
                'related_url': trans.related_url,
                'display_order': trans.faq.display_order,
                'relevance_score': self._calculate_relevance(query, trans)
            })
        
        # 関連度順にソート
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"FAQ search: query='{query}', results={len(results)}")
        return results
    
    def _calculate_relevance(self, query: str, translation: OperatorFaqTranslation) -> float:
        """
        簡易的な関連度スコア計算
        
        Args:
            query: 検索クエリ
            translation: FAQ翻訳オブジェクト
        
        Returns:
            関連度スコア (0.0-1.0)
        """
        score = 0.0
        query_lower = query.lower()
        
        # 質問文に完全一致
        if query_lower in translation.question.lower():
            score += 1.0
        
        # 回答文に完全一致
        if query_lower in translation.answer.lower():
            score += 0.5
        
        # キーワードに部分一致
        if translation.keywords and query_lower in translation.keywords.lower():
            score += 0.7
        
        return min(score, 1.0)
    
    async def get_categories(self, language: str = 'ja') -> List[Dict[str, Any]]:
        """
        カテゴリ一覧取得（FAQ件数付き）
        
        Args:
            language: 言語コード
        
        Returns:
            カテゴリ辞書のリスト
        """
        cache_key = f"operator_faq_categories:{language}"
        
        # キャッシュチェック
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        # カテゴリ別件数集計
        stmt = (
            select(
                OperatorFaq.category,
                func.count(OperatorFaq.id).label('count')
            )
            .where(OperatorFaq.is_active == True)
            .group_by(OperatorFaq.category)
            .order_by(OperatorFaq.category)
        )
        
        result = await self.db.execute(stmt)
        categories = [
            {'category': row.category, 'count': row.count}
            for row in result.all()
        ]
        
        # キャッシュに保存
        try:
            await redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(categories)
            )
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
        
        return categories

