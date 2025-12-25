"""
信頼度スコア計算（v0.3改善版）
"""

import re
import logging
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.faq import FAQ
from app.models.question_pattern import QuestionPattern
from app.ai.embeddings import generate_embedding

logger = logging.getLogger(__name__)


async def calculate_confidence(
    response_text: str,
    similar_faqs: List[FAQ],
    question: str,
    facility_id: int,
    db: AsyncSession
) -> Decimal:
    """
    信頼度スコア計算（v0.3改善版）
    0.0-1.0の範囲
    
    Args:
        response_text: AI生成回答テキスト
        similar_faqs: 類似FAQリスト（similarity属性を含む）
        question: ゲストの質問
        facility_id: 施設ID
        db: データベースセッション
    
    Returns:
        Decimal: 信頼度スコア（0.0-1.0）
    """
    base_confidence = Decimal("0.7")
    
    # FAQ類似度ボーナス（v0.2継続）
    if similar_faqs:
        # 最高類似度を取得（similar_faqsはsearch_similar_faqsから返されるが、
        # similarity属性は直接含まれていないため、暫定的に0.7を仮定）
        # TODO: search_similar_faqsでsimilarityを返すように修正
        max_similarity = Decimal("0.7")  # 暫定値
        if max_similarity >= Decimal("0.8"):
            base_confidence += Decimal("0.3")  # +0.3ボーナス
        elif max_similarity >= Decimal("0.7"):
            base_confidence += Decimal("0.15")  # +0.15ボーナス
    
    # 回答長ペナルティ（v0.2継続）
    if len(response_text) < 20:
        base_confidence -= Decimal("0.2")  # -0.2ペナルティ
    
    # 不確実性ワード検出（v0.2継続）
    uncertain_phrases = [
        "i'm not sure",
        "i don't know",
        "maybe",
        "probably",
        "might be",
        "i think",
        "possibly",
        "perhaps",
        "uncertain",
        "not certain"
    ]
    
    response_lower = response_text.lower()
    if any(phrase in response_lower for phrase in uncertain_phrases):
        base_confidence -= Decimal("0.15")  # -0.15ペナルティ
    
    # v0.3新規: 質問具体性スコア（固有名詞・数値含む）
    has_proper_noun = bool(re.search(r'\b[A-Z][a-z]+\b', question))  # 固有名詞検出
    has_number = bool(re.search(r'\d+', question))  # 数値検出
    if has_proper_noun or has_number:
        base_confidence += Decimal("0.1")  # +0.1ボーナス
    
    # v0.3新規: 過去同一質問解決率（80%以上で+0.15）
    try:
        from app.ai.vector_search import search_similar_patterns
        question_embedding = await generate_embedding(question)
        
        if question_embedding:
            # question_patternsテーブルから類似パターンを検索
            similar_patterns = await search_similar_patterns(
                facility_id=facility_id,
                embedding=question_embedding,
                threshold=Decimal("0.85"),  # コサイン類似度0.85以上を同一パターンと判定
                top_k=1,  # 最も類似度の高いパターンのみ
                db=db
            )
            
            if similar_patterns:
                pattern = similar_patterns[0]
                if pattern.resolution_rate and pattern.resolution_rate >= Decimal("0.8"):
                    base_confidence += Decimal("0.15")  # +0.15ボーナス
    except Exception as e:
        # 過去解決率取得エラーは無視（信頼度計算を続行）
        logger.warning(
            f"Failed to get past resolution rate: {e}",
            extra={
                "facility_id": facility_id,
                "question": question[:50]  # 最初の50文字のみ
            }
        )
    
    # v0.3新規: 施設カスタムFAQヒット（テンプレート以外）
    if similar_faqs:
        # テンプレートFAQはcreated_byがNULL、カスタムFAQはユーザーIDが設定
        has_custom_faq = any(faq.created_by is not None for faq in similar_faqs)
        if has_custom_faq:
            base_confidence += Decimal("0.2")  # +0.2ボーナス
    
    # 0.0-1.0の範囲にクリップ
    return max(Decimal("0.0"), min(Decimal("1.0"), base_confidence))


