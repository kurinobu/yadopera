"""
埋め込みベクトル生成
"""

from typing import List
from app.ai.openai_client import OpenAIClient
from app.models.faq import FAQ


async def generate_embedding(text: str) -> List[float]:
    """
    テキストを埋め込みベクトルに変換（v0.3詳細化）
    Model: text-embedding-3-small (1536次元)
    
    Args:
        text: 埋め込み生成対象のテキスト
    
    Returns:
        埋め込みベクトル（1536次元）、エラー時は空リスト
    """
    client = OpenAIClient()
    return await client.generate_embedding(text)


async def generate_faq_embedding(faq: FAQ) -> List[float]:
    """
    FAQの埋め込みベクトル生成（保存時自動実行、v0.3詳細化）
    質問と回答を結合して埋め込み生成
    
    Args:
        faq: FAQモデルインスタンス
    
    Returns:
        埋め込みベクトル（1536次元）、エラー時は空リスト
    """
    # 質問と回答を結合して埋め込み生成
    combined_text = f"{faq.question} {faq.answer}"
    return await generate_embedding(combined_text)

