"""
料金プラン制限定義
各プランのFAQ登録数上限と対応言語リストを定義
"""

from typing import Optional, List, Dict, Any, Set, Iterable

# 料金プラン別のFAQ登録数上限と対応言語リスト
PLAN_FAQ_LIMITS: Dict[str, Dict[str, Any]] = {
    "free": {
        "max_faqs": 30,  # FAQ登録数上限（インテント単位）
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

# Premium / ゲスト公開情報と揃えた管理画面FAQ用の言語コード一覧（plan_limits["languages"] が None のとき）
PREMIUM_FAQ_LANGUAGE_CODES: List[str] = [
    "ja", "en", "zh-TW", "zh-CN", "fr", "ko", "es"
]

# 管理画面・LP文言の統一表示で使う言語名（日本語）
LANGUAGE_CODE_TO_JA_NAME: Dict[str, str] = {
    "ja": "日本語",
    "en": "英語",
    "zh-TW": "繁体中国語",
    "zh-CN": "簡体中国語",
    "fr": "フランス語",
    "ko": "韓国語",
    "es": "スペイン語",
    "th": "タイ語",
}

# 初期自動登録件数の定義
# 注意: これは新規登録時に自動投入されるFAQ件数であり、
# プランの上限（max_faqs）とは異なる
# 全プランで30件に統一（優先度順にソートして上位30件を抽出）
INITIAL_FAQ_COUNTS: Dict[str, int] = {
    "free": 30,      # Freeプラン: 30件（日本語のみ）
    "mini": 30,      # Miniプラン: 30件（日本語+英語）
    "small": 30,     # Smallプラン: 30件（日本語+英語+中国語）
    "standard": 30,  # Standardプラン: 30件（日本語+英語+中国語+フランス語）
    "premium": 30    # Premiumプラン: 30件（全言語）
}

# プラン超過時の挙動（管理者選択制）: docs/プラン超過時の挙動_管理者選択制_実装計画.md
OVERAGE_BEHAVIOR_CONTINUE_BILLING = "continue_billing"  # 通常継続（従量課金）
OVERAGE_BEHAVIOR_FAQ_ONLY = "faq_only"  # AI停止・FAQ限定モード
OVERAGE_BEHAVIOR_CHOICES = (OVERAGE_BEHAVIOR_CONTINUE_BILLING, OVERAGE_BEHAVIOR_FAQ_ONLY)


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


def get_plan_language_codes(subscription_plan: str) -> List[str]:
    """
    プランごとの利用可能言語コードを返す。

    - Premium（None）の場合は PREMIUM_FAQ_LANGUAGE_CODES を返す
    - 不正なプランは small 扱いにフォールバックする
    """
    raw_plan = (subscription_plan or "small").lower()
    if raw_plan not in PLAN_FAQ_LIMITS:
        raw_plan = "small"
    plan_langs = PLAN_FAQ_LIMITS[raw_plan]["languages"]
    if plan_langs is None:
        return list(PREMIUM_FAQ_LANGUAGE_CODES)
    return list(plan_langs)


def get_language_ja_name(code: str) -> str:
    """言語コードから日本語表示名を返す（未知コードはコード文字列をそのまま返す）。"""
    return LANGUAGE_CODE_TO_JA_NAME.get(code, code)


def get_first_faq_language_for_plan(subscription_plan: str) -> str:
    """
    プラン定義における FAQ 用の「第一言語」コード（新規作成時の既定に使用）。
    """
    raw = (subscription_plan or "small").lower()
    if raw not in PLAN_FAQ_LIMITS:
        raw = "small"
    langs = PLAN_FAQ_LIMITS[raw]["languages"]
    if langs is None:
        return PREMIUM_FAQ_LANGUAGE_CODES[0]
    return langs[0] if langs else "ja"


def resolve_allowed_faq_language_codes(
    subscription_plan: str,
    language_limit: Optional[int],
    existing_faq_languages: Optional[Iterable[str]] = None,
) -> List[str]:
    """
    管理画面FAQで選択可能にすべき言語コード一覧を一意に算出する。

    - プランの許容語（get_plan_limits）をベースとし、Premium は PREMIUM_FAQ_LANGUAGE_CODES を使用
    - 施設の既存FAQに含まれる言語を和集合（プラン外のコードがあれば末尾に辞書順で追加）
    - language_limit は create_faq / update_faq の検証と整合するため引数で受け取る（C2 で UI 制御に使用）

    Args:
        subscription_plan: 課金サブスクプラン（free, mini, small, ...）
        language_limit: 施設の同時利用言語数上限（None は無制限）
        existing_faq_languages: 当該施設の FAQ 翻訳に現れる言語コード

    Returns:
        プラン定義順を先頭に並べた言語コードのリスト
    """
    _ = language_limit  # C1: 集約APIの入力として保持。選択肢の絞り込みは C2 で行う。
    existing: Set[str] = set(existing_faq_languages or [])
    raw_plan = (subscription_plan or "small").lower()
    if raw_plan not in PLAN_FAQ_LIMITS:
        raw_plan = "small"
    plan_langs = PLAN_FAQ_LIMITS[raw_plan]["languages"]
    if plan_langs is None:
        ordered_pool = list(PREMIUM_FAQ_LANGUAGE_CODES)
    else:
        ordered_pool = list(plan_langs)
    pool_set = set(ordered_pool)
    extras = sorted(lang for lang in existing if lang not in pool_set)
    return ordered_pool + extras


def get_initial_faq_count(plan: str) -> int:
    """
    初期自動登録件数を取得
    
    Args:
        plan: 料金プラン
    
    Returns:
        初期自動登録件数（全プランで30件）
    """
    return INITIAL_FAQ_COUNTS.get(plan, 30)  # デフォルトは30件


def filter_faq_presets_by_plan(
    presets: List[Dict[str, Any]],
    plan: str
) -> List[Dict[str, Any]]:
    """
    料金プランに基づいてFAQプリセットをフィルタ（初期自動登録用）
    
    優先度順にソートして、上位N件を抽出する（Nはプラン別初期登録件数）。
    
    Args:
        presets: FAQプリセットリスト
        plan: 料金プラン
    
    Returns:
        フィルタされたFAQプリセットリスト（優先度順）
    """
    # プランの制限を取得（言語フィルタ用）
    limits = get_plan_limits(plan)
    allowed_languages = limits["languages"]
    
    # 優先度順にソート（優先度が高い順）
    sorted_presets = sorted(
        presets,
        key=lambda x: x.get("priority", 1),
        reverse=True
    )
    
    # 上位N件を抽出（Nは初期自動登録件数）
    count = get_initial_faq_count(plan)
    selected_presets = sorted_presets[:count]
    
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
        # フィルタ後も翻訳が残っているFAQのみを返す
        selected_presets = [
            preset for preset in selected_presets
            if preset["translations"]
        ]
    
    return selected_presets

