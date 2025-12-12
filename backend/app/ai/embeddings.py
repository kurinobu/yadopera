"""
埋め込みベクトル生成
"""

import logging
from typing import List
from app.ai.openai_client import OpenAIClient
from app.models.faq import FAQ

logger = logging.getLogger(__name__)


async def generate_embedding(text: str) -> List[float]:
    """
    テキストを埋め込みベクトルに変換（v0.3詳細化）
    Model: text-embedding-3-small (1536次元)
    
    Args:
        text: 埋め込み生成対象のテキスト
    
    Returns:
        埋め込みベクトル（1536次元）、エラー時は空リスト
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding generation")
        return []
    
    try:
        client = OpenAIClient()
        embedding = await client.generate_embedding(text)
        if embedding and len(embedding) > 0:
            logger.debug(f"Embedding generated successfully: text_length={len(text)}, embedding_length={len(embedding)}")
            return embedding
        else:
            logger.warning(f"Empty embedding returned: text_length={len(text)}")
            return []
    except Exception as e:
        logger.error(
            f"Error generating embedding: {str(e)}",
            exc_info=True,
            extra={
                "text_length": len(text) if text else 0,
                "text_preview": text[:100] if text else None,
                "error": str(e)
            }
        )
        return []


async def generate_faq_embedding(faq: FAQ) -> List[float]:
    """
    FAQの埋め込みベクトル生成（保存時自動実行、v0.3詳細化）
    質問と回答を結合して埋め込み生成
    
    Args:
        faq: FAQモデルインスタンス
    
    Returns:
        埋め込みベクトル（1536次元）、エラー時は空リスト
    """
    if not faq:
        logger.error("FAQ object is None")
        return []
    
    if not faq.question or not faq.answer:
        logger.warning(
            f"FAQ has empty question or answer: faq_id={faq.id if hasattr(faq, 'id') else 'unknown'}, question={bool(faq.question)}, answer={bool(faq.answer)}"
        )
        return []
    
    try:
        # 質問と回答を結合して埋め込み生成
        combined_text = f"{faq.question} {faq.answer}"
        logger.debug(
            f"Generating FAQ embedding: faq_id={faq.id if hasattr(faq, 'id') else 'unknown'}, combined_text_length={len(combined_text)}"
        )
        embedding = await generate_embedding(combined_text)
        if embedding and len(embedding) > 0:
            logger.info(f"FAQ embedding generated successfully: faq_id={faq.id if hasattr(faq, 'id') else 'unknown'}, embedding_length={len(embedding)}")
        else:
            logger.warning(f"Failed to generate FAQ embedding (empty result): faq_id={faq.id if hasattr(faq, 'id') else 'unknown'}")
        return embedding
    except Exception as e:
        logger.error(
            f"Error generating FAQ embedding: {str(e)}",
            exc_info=True,
            extra={
                "faq_id": faq.id if hasattr(faq, 'id') else 'unknown',
                "question": faq.question[:100] if faq.question else None,
                "answer": faq.answer[:100] if faq.answer else None,
                "error": str(e)
            }
        )
        return []

