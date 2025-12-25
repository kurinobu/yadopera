"""
pgvector検索実装（インテントベース構造対応）
"""

import logging
from typing import List
from decimal import Decimal
from sqlalchemy import select, func, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from pgvector.sqlalchemy import Vector
from app.models.faq import FAQ
from app.models.faq_translation import FAQTranslation
from app.models.question_pattern import QuestionPattern

logger = logging.getLogger(__name__)


async def search_similar_faqs(
    facility_id: int,
    embedding: List[float],
    top_k: int = 3,
    threshold: float = 0.7,
    db: AsyncSession = None
) -> List[FAQ]:
    """
    pgvectorで類似FAQ検索（エラーハンドリング付き、インテントベース構造対応）
    コサイン類似度を使用
    
    Args:
        facility_id: 施設ID
        embedding: 埋め込みベクトル（1536次元）
        top_k: 取得する最大件数（デフォルト: 3）
        threshold: 類似度閾値（0.0-1.0、デフォルト: 0.7）
        db: データベースセッション
    
    Returns:
        類似FAQリスト（閾値以上の類似度のもののみ、インテント単位で重複排除）、エラー時は空リスト
    
    Note:
        - `faq_translations`テーブルから検索
        - 同じ`faq_id`の`FAQTranslation`をグループ化して返す（インテント単位で1件）
    """
    if not db:
        logger.error("Database session is required")
        return []
    
    if not embedding:
        logger.warning("Empty embedding provided")
        return []
    
    try:
        # ベクトルをvector型に変換
        # pgvectorのcosine_distance関数は、2つのvector型の引数を必要とする
        # Pythonのリストをcast関数でvector型に変換
        embedding_vector = cast(embedding, Vector(1536))
        
        # コサイン類似度で検索（1 - コサイン距離 = 類似度）
        # faq_translationsテーブルから検索（埋め込みベクトルは翻訳ごとに保存されている）
        # FAQとFAQTranslationをJOINして、FAQ.is_activeもチェック
        query = select(
            FAQTranslation,
            FAQ,
            (1 - func.cosine_distance(FAQTranslation.embedding, embedding_vector)).label('similarity')
        ).join(
            FAQ, FAQTranslation.faq_id == FAQ.id
        ).where(
            FAQ.facility_id == facility_id,
            FAQ.is_active == True,
            FAQTranslation.embedding.isnot(None)  # 埋め込みベクトルが存在するもののみ
        ).order_by(
            func.cosine_distance(FAQTranslation.embedding, embedding_vector).asc()
        ).limit(top_k * 5)  # 同じfaq_idの重複を考慮して多めに取得
        
        result = await db.execute(query)
        results = result.all()
        
        # 閾値以上の類似度のFAQTranslationを取得し、同じfaq_idのものをグループ化
        # 同じfaq_idの場合は、最も高い類似度のものを使用
        faq_similarities = {}  # {faq_id: (faq, max_similarity)}
        
        for faq_translation, faq, similarity in results:
            if similarity >= threshold:
                faq_id = faq.id
                # 既に同じfaq_idが存在する場合は、より高い類似度のものを保持
                if faq_id not in faq_similarities or similarity > faq_similarities[faq_id][1]:
                    faq_similarities[faq_id] = (faq, similarity)
        
        # FAQリストを作成（類似度の降順でソート）
        similar_faqs = [
            faq for faq, _ in sorted(
                faq_similarities.values(),
                key=lambda x: x[1],
                reverse=True
            )
        ][:top_k]  # top_k件まで返す
        
        logger.debug(
            f"Vector search completed: {len(similar_faqs)}/{len(faq_similarities)} unique FAQs above threshold (from {len(results)} translation results)",
            extra={
                "facility_id": facility_id,
                "top_k": top_k,
                "threshold": threshold,
                "found_count": len(similar_faqs),
                "unique_faq_count": len(faq_similarities),
                "total_translation_results": len(results)
            }
        )
        
        return similar_faqs
    
    except SQLAlchemyError as e:
        # データベースエラー
        logger.error(
            "pgvector search error",
            extra={
                "error_type": "database_error",
                "error_message": str(e),
                "facility_id": facility_id
            },
            exc_info=True
        )
        # エラー時は空リスト返却（検索結果なしとして処理続行）
        return []
    
    except Exception as e:
        # 予期しないエラー
        logger.critical(
            "Unexpected error in vector search",
            extra={
                "error_type": "unexpected_error",
                "error_message": str(e),
                "facility_id": facility_id
            },
            exc_info=True
        )
        return []


async def search_similar_patterns(
    facility_id: int,
    embedding: List[float],
    threshold: Decimal = Decimal("0.85"),
    top_k: int = 1,
    db: AsyncSession = None
) -> List[QuestionPattern]:
    """
    pgvectorで類似質問パターン検索（エラーハンドリング付き、v0.3詳細化）
    コサイン類似度を使用（信頼度スコア計算用）
    
    Args:
        facility_id: 施設ID
        embedding: 埋め込みベクトル（1536次元）
        threshold: 類似度閾値（0.0-1.0、デフォルト: 0.85）
        top_k: 取得する最大件数（デフォルト: 1）
        db: データベースセッション
    
    Returns:
        類似質問パターンリスト（閾値以上の類似度のもののみ）、エラー時は空リスト
    """
    if not db:
        logger.error("Database session is required")
        return []
    
    if not embedding:
        logger.warning("Empty embedding provided")
        return []
    
    try:
        # ベクトルをvector型に変換
        # pgvectorのcosine_distance関数は、2つのvector型の引数を必要とする
        # Pythonのリストをcast関数でvector型に変換
        embedding_vector = cast(embedding, Vector(1536))
        
        # コサイン類似度で検索（1 - コサイン距離 = 類似度）
        query = select(
            QuestionPattern,
            (1 - func.cosine_distance(QuestionPattern.pattern_embedding, embedding_vector)).label('similarity')
        ).where(
            QuestionPattern.facility_id == facility_id
        ).order_by(
            func.cosine_distance(QuestionPattern.pattern_embedding, embedding_vector).asc()
        ).limit(top_k)
        
        result = await db.execute(query)
        results = result.all()
        
        # 閾値以上の類似度のパターンのみ返す
        similar_patterns = []
        for pattern, similarity in results:
            if similarity >= float(threshold):
                similar_patterns.append(pattern)
        
        logger.debug(
            f"Pattern search completed: {len(similar_patterns)}/{len(results)} patterns above threshold",
            extra={
                "facility_id": facility_id,
                "top_k": top_k,
                "threshold": float(threshold),
                "found_count": len(similar_patterns),
                "total_results": len(results)
            }
        )
        
        return similar_patterns
    
    except SQLAlchemyError as e:
        # データベースエラー
        logger.error(
            "pgvector pattern search error",
            extra={
                "error_type": "database_error",
                "error_message": str(e),
                "facility_id": facility_id
            },
            exc_info=True
        )
        # エラー時は空リスト返却（検索結果なしとして処理続行）
        return []
    
    except Exception as e:
        # 予期しないエラー
        logger.critical(
            "Unexpected error in pattern search",
            extra={
                "error_type": "unexpected_error",
                "error_message": str(e),
                "facility_id": facility_id
            },
            exc_info=True
        )
        return []

