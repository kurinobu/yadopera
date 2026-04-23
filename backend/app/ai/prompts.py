"""
RAG統合型プロンプトテンプレート
"""

from typing import List
from app.models.facility import Facility
from app.models.faq import FAQ


def format_facility_information_block(facility: Facility) -> str:
    """
    RAG 用の施設情報ブロック。
    wifi_password は公開 REST には載せないが、サーバー内チャット文脈では施設が提供した公式情報として含める。
    """
    pw_raw = getattr(facility, "wifi_password", None)
    if pw_raw is not None and str(pw_raw).strip():
        wifi_password_value = str(pw_raw).strip()
    else:
        wifi_password_value = "Not set"
    return f"""
Facility: {facility.name}
Check-in: {facility.check_in_time}
Check-out: {facility.check_out_time}
WiFi SSID: {facility.wifi_ssid or "Not available"}
WiFi password (official guest information from the property): {wifi_password_value}
House Rules: {(facility.house_rules or "")[:500]}
Local Info: {(facility.local_info or "")[:500]}
Prohibited Items: {(getattr(facility, "prohibited_items", "") or "")[:500]}
"""


RAG_SYSTEM_PROMPT = """
You are a helpful assistant for {facility_name}, a guesthouse.

## Your role:
- Answer guests' questions based on the provided FAQs and facility information.
- Be friendly, concise (under 200 characters), and helpful.
- WiFi SSID and WiFi password in Facility Information are official guest-facing details from the property. When guests ask about WiFi, state them exactly when set; do not refuse on generic security grounds when they appear there. If WiFi password is "Not set", do not invent one—suggest asking staff at the property.
- Only if the answer is not supported by Facility Information or Relevant FAQs (and you would need to guess), suggest contacting staff.

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
    facility_info = format_facility_information_block(facility)
    
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

