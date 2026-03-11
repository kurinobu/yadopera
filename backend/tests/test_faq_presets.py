"""
FAQプリセットのプラン別フィルタテスト（多言語実装 Phase B）
plan_limits.filter_faq_presets_by_plan の動作確認
"""

import pytest

from app.data.faq_presets import FAQ_PRESETS
from app.core.plan_limits import (
    filter_faq_presets_by_plan,
    get_plan_limits,
    get_initial_faq_count,
    PLAN_FAQ_LIMITS,
    INITIAL_FAQ_COUNTS,
)


class TestFilterFaqPresetsByPlan:
    """料金プラン別FAQプリセットフィルタのテスト"""

    def test_faq_presets_has_30_items(self):
        """FAQ_PRESETSは30件あること"""
        assert len(FAQ_PRESETS) == 30

    def test_faq_presets_each_has_seven_languages(self):
        """各FAQに7言語（ja, en, zh-TW, fr, ko, zh-CN, es）が含まれること"""
        expected_languages = {"ja", "en", "zh-TW", "fr", "ko", "zh-CN", "es"}
        for preset in FAQ_PRESETS:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == expected_languages, (
                f"intent_key={preset['intent_key']}: expected {expected_languages}, got {langs}"
            )

    def test_filter_free_returns_20_presets_ja_only(self):
        """Freeプラン: 20件、日本語のみ"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "free")
        assert len(result) == 20
        for preset in result:
            langs = [t["language"] for t in preset["translations"]]
            assert langs == ["ja"], f"Free should have only ja, got {langs}"

    def test_filter_mini_returns_20_presets_ja_en(self):
        """Miniプラン: 20件、日本語＋英語"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "mini")
        assert len(result) == 20
        for preset in result:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == {"ja", "en"}, f"Mini should have ja,en only, got {langs}"

    def test_filter_small_returns_20_presets_ja_en_zh_tw(self):
        """Smallプラン: 20件、日本語＋英語＋繁体中国語"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "small")
        assert len(result) == 20
        for preset in result:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == {"ja", "en", "zh-TW"}, (
                f"Small should have ja,en,zh-TW only, got {langs}"
            )

    def test_filter_standard_returns_20_presets_ja_en_zh_tw_fr(self):
        """Standardプラン: 20件、日本語＋英語＋繁体中国語＋フランス語"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "standard")
        assert len(result) == 20
        for preset in result:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == {"ja", "en", "zh-TW", "fr"}, (
                f"Standard should have ja,en,zh-TW,fr only, got {langs}"
            )

    def test_filter_premium_returns_20_presets_all_languages(self):
        """Premiumプラン: 20件、全7言語"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "premium")
        assert len(result) == 20
        for preset in result:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == {"ja", "en", "zh-TW", "fr", "ko", "zh-CN", "es"}, (
                f"Premium should have all 7 languages, got {langs}"
            )

    def test_filter_unknown_plan_defaults_to_small(self):
        """未知のプラン名: smallとして扱われること"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "unknown_plan")
        assert len(result) == 20
        for preset in result:
            langs = {t["language"] for t in preset["translations"]}
            assert langs == {"ja", "en", "zh-TW"}

    def test_filter_preserves_priority_order(self):
        """フィルタ結果は優先度順（降順）であること"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "standard")
        priorities = [p.get("priority", 1) for p in result]
        assert priorities == sorted(priorities, reverse=True)

    def test_filter_preserves_intent_key_and_category(self):
        """フィルタ後も intent_key, category が維持されること"""
        result = filter_faq_presets_by_plan(FAQ_PRESETS, "mini")
        for preset in result:
            assert "intent_key" in preset
            assert "category" in preset
            assert "translations" in preset
            assert len(preset["translations"]) >= 1


class TestGetPlanLimits:
    """get_plan_limits のテスト（言語フィルタ動作確認の一環）"""

    def test_free_languages_ja_only(self):
        """Free: 日本語のみ"""
        limits = get_plan_limits("free")
        assert limits["languages"] == ["ja"]

    def test_mini_languages_ja_en(self):
        """Mini: 日本語＋英語"""
        limits = get_plan_limits("mini")
        assert limits["languages"] == ["ja", "en"]

    def test_small_languages_ja_en_zh_tw(self):
        """Small: 日本語＋英語＋繁体中国語"""
        limits = get_plan_limits("small")
        assert limits["languages"] == ["ja", "en", "zh-TW"]

    def test_standard_languages_ja_en_zh_tw_fr(self):
        """Standard: 日本語＋英語＋繁体中国語＋フランス語"""
        limits = get_plan_limits("standard")
        assert limits["languages"] == ["ja", "en", "zh-TW", "fr"]

    def test_premium_languages_none_unlimited(self):
        """Premium: 無制限（None）"""
        limits = get_plan_limits("premium")
        assert limits["languages"] is None

    def test_unknown_plan_defaults_to_small(self):
        """未知のプラン: smallの制限を返す"""
        limits = get_plan_limits("invalid")
        assert limits["languages"] == ["ja", "en", "zh-TW"]


class TestGetInitialFaqCount:
    """get_initial_faq_count のテスト"""

    def test_all_plans_return_20(self):
        """全プランで初期登録件数は20件"""
        for plan in ("free", "mini", "small", "standard", "premium"):
            assert get_initial_faq_count(plan) == 20

    def test_unknown_plan_returns_20(self):
        """未知のプランは20件"""
        assert get_initial_faq_count("unknown") == 20
