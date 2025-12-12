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
    )
}


def get_fallback_message(language: str = "en") -> str:
    """
    フォールバックメッセージ取得（v0.3新規）
    ゲストの選択言語に応じて返却
    
    Args:
        language: 言語コード（'en', 'ja', 'zh-TW', 'fr'）
    
    Returns:
        str: フォールバックメッセージ（該当言語がない場合は英語を返却）
    """
    return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["en"])


