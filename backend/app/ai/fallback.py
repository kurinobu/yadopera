"""
フォールバックメッセージ（v0.3新規）
OpenAI API障害時のフォールバック文言
"""

FALLBACK_MESSAGES = {
    "en": (
        "Sorry, the automatic support system is temporarily unavailable. "
        "Please contact the staff directly for assistance."
    ),
    "ja": (
        "現在、自動案内システムが一時的に利用できません。"
        "お手数ですがスタッフへ直接お問い合わせください。"
    ),
    "zh-TW": (
        "抱歉，自動支援系統暫時無法使用。"
        "請直接聯繫工作人員尋求協助。"
    ),
    "fr": (
        "Désolé, le système de support automatique est temporairement indisponible. "
        "Veuillez contacter directement le personnel pour obtenir de l'aide."
    ),
    "ko": (
        "죄송합니다. 자동 안내 시스템을 일시적으로 이용하실 수 없습니다. "
        "직원에게 직접 문의해 주세요."
    )
}


def get_fallback_message(language: str = "en") -> str:
    """
    フォールバックメッセージ取得（v0.3新規）
    ゲストの選択言語に応じて返却
    
    Args:
        language: 言語コード（'en', 'ja', 'zh-TW', 'fr', 'ko'）
    
    Returns:
        str: フォールバックメッセージ（該当言語がない場合は英語を返却）
    """
    return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["en"])


# プラン超過時・FAQ限定モードで該当FAQが無いときのメッセージ
FAQ_ONLY_NO_MATCH_MESSAGES = {
    "en": "No matching FAQ was found. Please contact the staff for assistance.",
    "ja": "該当するFAQが見つかりませんでした。スタッフまでお問い合わせください。",
    "zh-TW": "未找到對應的常見問題。請聯繫工作人員尋求協助。",
    "zh-CN": "未找到对应的常见问题。请联系工作人员寻求协助。",
    "fr": "Aucune FAQ correspondante trouvée. Veuillez contacter le personnel pour obtenir de l'aide.",
    "ko": "해당 FAQ를 찾을 수 없습니다. 스태프에게 문의해 주세요.",
    "es": "No se encontró ninguna FAQ coincidente. Por favor, contacte al personal para obtener ayuda.",
}


def get_faq_only_no_match_message(language: str = "en") -> str:
    """
    FAQ限定モードで該当FAQが無いときに返すメッセージ（プラン超過時挙動 Step 3）
    """
    return FAQ_ONLY_NO_MATCH_MESSAGES.get(language, FAQ_ONLY_NO_MATCH_MESSAGES["en"])


