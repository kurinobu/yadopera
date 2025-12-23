"""
埋め込みベクトル生成（インテントベース構造対応）
"""

import logging
from typing import List
from app.ai.openai_client import OpenAIClient
from app.models.faq import FAQ
from app.models.faq_translation import FAQTranslation

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


async def generate_faq_embedding(faq_translation: FAQTranslation) -> List[float]:
    """
    FAQ翻訳の埋め込みベクトル生成（保存時自動実行、インテントベース構造対応）
    質問と回答を結合して埋め込み生成
    
    Args:
        faq_translation: FAQTranslationモデルインスタンス
    
    Returns:
        埋め込みベクトル（1536次元）、エラー時は空リスト
    
    Note:
        - 新しい構造では、埋め込みベクトルは翻訳ごとに生成される
        - `FAQTranslation.question`と`FAQTranslation.answer`を結合して埋め込み生成
    """
    if not faq_translation:
        logger.error("FAQTranslation object is None")
        return []
    
    if not faq_translation.question or not faq_translation.answer:
        logger.warning(
            f"FAQTranslation has empty question or answer: "
            f"translation_id={faq_translation.id if hasattr(faq_translation, 'id') else 'unknown'}, "
            f"faq_id={faq_translation.faq_id if hasattr(faq_translation, 'faq_id') else 'unknown'}, "
            f"language={faq_translation.language if hasattr(faq_translation, 'language') else 'unknown'}, "
            f"question={bool(faq_translation.question)}, answer={bool(faq_translation.answer)}"
        )
        return []
    
    try:
        # 質問と回答を結合して埋め込み生成
        combined_text = f"{faq_translation.question} {faq_translation.answer}"
        logger.debug(
            f"Generating FAQ translation embedding: "
            f"translation_id={faq_translation.id if hasattr(faq_translation, 'id') else 'unknown'}, "
            f"faq_id={faq_translation.faq_id if hasattr(faq_translation, 'faq_id') else 'unknown'}, "
            f"language={faq_translation.language if hasattr(faq_translation, 'language') else 'unknown'}, "
            f"combined_text_length={len(combined_text)}"
        )
        embedding = await generate_embedding(combined_text)
        if embedding and len(embedding) > 0:
            logger.info(
                f"FAQ translation embedding generated successfully: "
                f"translation_id={faq_translation.id if hasattr(faq_translation, 'id') else 'unknown'}, "
                f"faq_id={faq_translation.faq_id if hasattr(faq_translation, 'faq_id') else 'unknown'}, "
                f"language={faq_translation.language if hasattr(faq_translation, 'language') else 'unknown'}, "
                f"embedding_length={len(embedding)}"
            )
        else:
            logger.warning(
                f"Failed to generate FAQ translation embedding (empty result): "
                f"translation_id={faq_translation.id if hasattr(faq_translation, 'id') else 'unknown'}, "
                f"faq_id={faq_translation.faq_id if hasattr(faq_translation, 'faq_id') else 'unknown'}, "
                f"language={faq_translation.language if hasattr(faq_translation, 'language') else 'unknown'}"
            )
        return embedding
    except Exception as e:
        logger.error(
            f"Error generating FAQ translation embedding: {str(e)}",
            exc_info=True,
            extra={
                "translation_id": faq_translation.id if hasattr(faq_translation, 'id') else 'unknown',
                "faq_id": faq_translation.faq_id if hasattr(faq_translation, 'faq_id') else 'unknown',
                "language": faq_translation.language if hasattr(faq_translation, 'language') else 'unknown',
                "question": faq_translation.question[:100] if faq_translation.question else None,
                "answer": faq_translation.answer[:100] if faq_translation.answer else None,
                "error": str(e)
            }
        )
        return []

