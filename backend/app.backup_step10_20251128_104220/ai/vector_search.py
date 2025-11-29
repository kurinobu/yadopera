"""
pgvector検索実装
"""

import logging
from typing import List
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from pgvector.sqlalchemy import Vector
from app.models.faq import FAQ
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
    pgvectorで類似FAQ検索（エラーハンドリング付き、v0.3詳細化）
    コサイン類似度を使用
    
    Args:
        facility_id: 施設ID
        embedding: 埋め込みベクトル（1536次元）
        top_k: 取得する最大件数（デフォルト: 3）
        threshold: 類似度閾値（0.0-1.0、デフォルト: 0.7）
        db: データベースセッション
    
    Returns:
        類似FAQリスト（閾値以上の類似度のもののみ）、エラー時は空リスト
    """
    if not db:
        logger.error("Database session is required")
        return []
    
    if not embedding:
        logger.warning("Empty embedding provided")
        return []
    
    try:
        # ベクトルをPostgreSQL形式に変換
        # pgvectorでは、Pythonのリストを直接使用できるが、
        # SQLAlchemyのfunc.cosine_distanceを使用する場合は文字列形式が必要
        embedding_vector = f"[{','.join(map(str, embedding))}]"
        
        # コサイン類似度で検索（1 - コサイン距離 = 類似度）
        # pgvectorのcosine_distance関数を使用
        query = select(
            FAQ,
            (1 - func.cosine_distance(FAQ.embedding, embedding_vector)).label('similarity')
        ).where(
            FAQ.facility_id == facility_id,
            FAQ.is_active == True,
            FAQ.embedding.isnot(None)  # 埋め込みベクトルが存在するもののみ
        ).order_by(
            func.cosine_distance(FAQ.embedding, embedding_vector).asc()
        ).limit(top_k)
        
        result = await db.execute(query)
        results = result.all()
        
        # 閾値以上の類似度のFAQのみ返す
        similar_faqs = []
        for faq, similarity in results:
            if similarity >= threshold:
                similar_faqs.append(faq)
        
        logger.debug(
            f"Vector search completed: {len(similar_faqs)}/{len(results)} FAQs above threshold",
            extra={
                "facility_id": facility_id,
                "top_k": top_k,
                "threshold": threshold,
                "found_count": len(similar_faqs),
                "total_results": len(results)
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
        # ベクトルをPostgreSQL形式に変換
        embedding_vector = f"[{','.join(map(str, embedding))}]"
        
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

