"""
RAG統合型プロンプトテンプレート
"""

from typing import List
from app.models.facility import Facility
from app.models.faq import FAQ


RAG_SYSTEM_PROMPT = """
You are a helpful assistant for {facility_name}, a guesthouse.

## Your role:
- Answer guests' questions based on the provided FAQs and facility information.
- Be friendly, concise (under 200 characters), and helpful.
- If you cannot answer confidently, suggest contacting staff.

## Facility Information:
{facility_info}

## Relevant FAQs (from vector search):
{faqs}

## Guest's question:
{question}

## Your Response (in English, under 200 characters):
"""


def build_rag_prompt(
    facility: Facility,
    similar_faqs: List[FAQ],
    question: str
) -> str:
    """
    RAG統合型プロンプト生成（v0.3詳細化）
    コンテキスト構築（約600トークン）
    - 関連FAQ Top 3: 約300トークン
    - 施設基本情報: 約150トークン
    - システムプロンプト: 約100トークン
    - ゲスト質問: 約50トークン
    
    Args:
        facility: 施設情報
        similar_faqs: 類似FAQリスト
        question: ゲストの質問
    
    Returns:
        str: 構築されたプロンプト
    """
    # 施設基本情報（約150トークン）
    facility_info = f"""
- Name: {facility.name}
- Check-in: {facility.check_in_time}
- Check-out: {facility.check_out_time}
- WiFi SSID: {facility.wifi_ssid or "Not available"}
- House Rules: {(facility.house_rules or "")[:500]}
- Local Info: {(facility.local_info or "")[:500]}
- Prohibited Items: {(getattr(facility, "prohibited_items", "") or "")[:500]}
"""
    
    # 関連FAQ Top 3（約300トークン）
    faq_text = "\n".join([
        f"Q: {faq.question}\nA: {faq.answer}"
        for faq in similar_faqs[:3]
    ]) if similar_faqs else "No relevant FAQs found."
    
    return RAG_SYSTEM_PROMPT.format(
        facility_name=facility.name,
        facility_info=facility_info,
        faqs=faq_text,
        question=question
    )

