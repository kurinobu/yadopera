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
# 全プランで20件に統一（カテゴリ毎に5件ずつ）
INITIAL_FAQ_COUNTS: Dict[str, int] = {
    "free": 20,      # Freeプラン: 20件（日本語のみ）
    "mini": 20,      # Miniプラン: 20件（日本語+英語）
    "small": 20,     # Smallプラン: 20件（日本語+英語+中国語）
    "standard": 20,  # Standardプラン: 20件（日本語+英語+中国語+フランス語）
    "premium": 20    # Premiumプラン: 20件（全言語）
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
        初期自動登録件数（全プランで20件）
    """
    return INITIAL_FAQ_COUNTS.get(plan, 20)  # デフォルトは20件


def filter_faq_presets_by_plan(
    presets: List[Dict[str, Any]],
    plan: str
) -> List[Dict[str, Any]]:
    """
    料金プランに基づいてFAQプリセットをフィルタ（初期自動登録用）
    
    カテゴリ毎に均等に5件ずつ抽出して合計20件にする。
    
    Args:
        presets: FAQプリセットリスト
        plan: 料金プラン
    
    Returns:
        フィルタされたFAQプリセットリスト（20件、カテゴリ毎に5件ずつ）
    """
    # プランの制限を取得（言語フィルタ用）
    limits = get_plan_limits(plan)
    allowed_languages = limits["languages"]
    
    # カテゴリ毎に分類
    categories = ["basic", "facilities", "location", "trouble"]
    filtered_presets = []
    
    for category in categories:
        # カテゴリ毎にFAQを抽出
        category_presets = [p for p in presets if p["category"] == category]
        
        # 優先度順にソート（優先度が高い順）
        category_presets.sort(key=lambda x: x.get("priority", 1), reverse=True)
        
        # 各カテゴリから5件ずつ抽出
        selected_presets = category_presets[:5]
        
        # 言語フィルタ
        if allowed_languages:
            selected_presets = [
                {
                    **preset,
                    "translations": [
                        t for t in preset["translations"]
                        if t["language"] in allowed_languages
                    ]
                }
                for preset in selected_presets
            ]
            # フィルタ後も翻訳が残っているFAQのみを追加
            selected_presets = [
                preset for preset in selected_presets
                if preset["translations"]
            ]
        
        filtered_presets.extend(selected_presets)
    
    return filtered_presets

