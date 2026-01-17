"""
エラーメッセージ定義（多言語対応）
"""

from typing import Dict, Optional

# エラーメッセージ（英語・日本語）
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "VALIDATION_ERROR": {
        "en": "Validation failed. Please check your input.",
        "ja": "入力内容に誤りがあります。入力内容を確認してください。"
    },
    "UNAUTHORIZED": {
        "en": "Authentication required. Please log in.",
        "ja": "認証が必要です。ログインしてください。"
    },
    "FORBIDDEN": {
        "en": "You do not have permission to perform this action.",
        "ja": "この操作を実行する権限がありません。"
    },
    "NOT_FOUND": {
        "en": "Resource not found.",
        "ja": "リソースが見つかりません。"
    },
    "DATABASE_ERROR": {
        "en": "Database error occurred. Please try again later.",
        "ja": "データベースエラーが発生しました。しばらく時間をおいてから再度お試しください。"
    },
    "SERVICE_UNAVAILABLE": {
        "en": "Service is temporarily unavailable. Please try again later.",
        "ja": "サービスが一時的に利用できません。しばらく時間をおいてから再度お試しください。"
    },
    "AI_ERROR": {
        "en": "AI processing error occurred. Please try again later.",
        "ja": "AI処理でエラーが発生しました。しばらく時間をおいてから再度お試しください。"
    },
    "VECTOR_SEARCH_ERROR": {
        "en": "Vector search failed. Please try again.",
        "ja": "ベクトル検索に失敗しました。再度お試しください。"
    },
    "ESCALATION_ERROR": {
        "en": "Escalation processing error occurred.",
        "ja": "エスカレーション処理でエラーが発生しました。"
    },
    "INTERNAL_ERROR": {
        "en": "An unexpected error occurred. Please try again later.",
        "ja": "予期しないエラーが発生しました。しばらく時間をおいてから再度お試しください。"
    },
    "NETWORK_ERROR": {
        "en": "Network error occurred. Please check your connection.",
        "ja": "ネットワークエラーが発生しました。接続を確認してください。"
    },
    "TIMEOUT_ERROR": {
        "en": "Request timeout. Please try again.",
        "ja": "リクエストがタイムアウトしました。再度お試しください。"
    },
    "RATE_LIMIT": {
        "en": "Too many requests. Please try again later.",
        "ja": "リクエストが多すぎます。しばらく時間をおいてから再度お試しください。"
    },
    "LANGUAGE_LIMIT_EXCEEDED": {
        "en": "Language limit reached ({language_limit} languages). Please use existing languages or upgrade your plan.",
        "ja": "プランの言語数制限に達しています（{language_limit}言語）。既存の言語を使用するか、プランをアップグレードしてください。"
    }
}


def get_error_message(code: str, language: str = "en") -> str:
    """
    エラーメッセージを取得（多言語対応）
    
    Args:
        code: エラーコード
        language: 言語コード（"en" または "ja"）
    
    Returns:
        エラーメッセージ
    """
    if code in ERROR_MESSAGES:
        return ERROR_MESSAGES[code].get(language, ERROR_MESSAGES[code]["en"])
    return ERROR_MESSAGES["INTERNAL_ERROR"].get(language, ERROR_MESSAGES["INTERNAL_ERROR"]["en"])


