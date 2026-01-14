"""
料金プラン制限定義
各プランのFAQ登録数上限と対応言語リストを定義
"""

from typing import Optional, List, Dict, Any

# 料金プラン別のFAQ登録数上限と対応言語リスト
PLAN_FAQ_LIMITS: Dict[str, Dict[str, Any]] = {
    "free": {
        "max_faqs": 20,  # FAQ登録数上限（インテント単位）
        "languages": ["ja"]  # 対応言語リスト（日本語のみ）
    },
    "mini": {
        "max_faqs": 30,
        "languages": ["ja", "en"]  # 日本語＋英語
    },
    "small": {
        "max_faqs": 50,
        "languages": ["ja", "en", "zh-TW"]  # 日本語＋英語＋中国語（繁体字）
    },
    "standard": {
        "max_faqs": 100,
        "languages": ["ja", "en", "zh-TW", "fr"]  # 日本語＋英語＋中国語＋フランス語
    },
    "premium": {
        "max_faqs": None,  # 無制限
        "languages": None  # 無制限（全言語対応）
    }
}


def get_plan_limits(plan: str) -> Dict[str, Any]:
    """
    料金プランの制限を取得
    
    Args:
        plan: 料金プラン（"free", "mini", "small", "standard", "premium"）
    
    Returns:
        プラン制限（max_faqs, languages）
    """
    if plan not in PLAN_FAQ_LIMITS:
        # デフォルトはsmallプラン
        plan = "small"
    
    return PLAN_FAQ_LIMITS[plan]


def filter_faq_presets_by_plan(
    presets: List[Dict[str, Any]],
    plan: str
) -> List[Dict[str, Any]]:
    """
    料金プランに基づいてFAQプリセットをフィルタ
    
    Args:
        presets: FAQプリセットリスト
        plan: 料金プラン
    
    Returns:
        フィルタされたFAQプリセットリスト
    """
    limits = get_plan_limits(plan)
    max_faqs = limits["max_faqs"]
    allowed_languages = limits["languages"]
    
    # FAQ件数制限
    filtered_presets = presets[:max_faqs] if max_faqs else presets
    
    # 言語フィルタ
    if allowed_languages:
        filtered_presets = [
            {
                **preset,
                "translations": [
                    t for t in preset["translations"]
                    if t["language"] in allowed_languages
                ]
            }
            for preset in filtered_presets
        ]
        # フィルタ後も翻訳が残っているFAQのみを返す
        filtered_presets = [
            preset for preset in filtered_presets
            if preset["translations"]
        ]
    
    return filtered_presets

