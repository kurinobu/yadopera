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

# 初期自動登録件数の定義
# 注意: これは新規登録時に自動投入されるFAQ件数であり、
# プランの上限（max_faqs）とは異なる
INITIAL_FAQ_COUNTS: Dict[str, int] = {
    "free": 20,      # Freeプラン: 20件
    "mini": 30,      # Miniプラン: 30件
    "small": 30,     # Smallプラン: 30件
    "standard": 30,  # Standardプラン: 30件
    "premium": 30    # Premiumプラン: 30件
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


def get_initial_faq_count(plan: str) -> int:
    """
    初期自動登録件数を取得
    
    Args:
        plan: 料金プラン
    
    Returns:
        初期自動登録件数
    """
    return INITIAL_FAQ_COUNTS.get(plan, 30)  # デフォルトは30件


def filter_faq_presets_by_plan(
    presets: List[Dict[str, Any]],
    plan: str
) -> List[Dict[str, Any]]:
    """
    料金プランに基づいてFAQプリセットをフィルタ（初期自動登録用）
    
    注意: この関数は初期自動登録時に使用されます。
    プランの上限（max_faqs）ではなく、初期自動登録件数（INITIAL_FAQ_COUNTS）に基づいてフィルタリングします。
    
    Args:
        presets: FAQプリセットリスト
        plan: 料金プラン
    
    Returns:
        フィルタされたFAQプリセットリスト
    """
    # 初期自動登録件数を取得
    initial_count = get_initial_faq_count(plan)
    
    # プランの制限を取得（言語フィルタ用）
    limits = get_plan_limits(plan)
    allowed_languages = limits["languages"]
    
    # 初期自動登録件数に基づいてフィルタ
    filtered_presets = presets[:initial_count]
    
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

