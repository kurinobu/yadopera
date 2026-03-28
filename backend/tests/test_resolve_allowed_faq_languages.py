"""resolve_allowed_faq_language_codes（C1）の単体テスト"""

import pytest

from app.core.plan_limits import (
    PREMIUM_FAQ_LANGUAGE_CODES,
    get_first_faq_language_for_plan,
    resolve_allowed_faq_language_codes,
)


def test_get_first_faq_language_for_plan():
    assert get_first_faq_language_for_plan("free") == "ja"
    assert get_first_faq_language_for_plan("mini") == "ja"
    assert get_first_faq_language_for_plan("premium") == "ja"


def test_free_plan_no_existing():
    assert resolve_allowed_faq_language_codes("free", 1, set()) == ["ja"]


def test_free_plan_with_drift_language_appended():
    out = resolve_allowed_faq_language_codes("free", 1, {"ja", "en"})
    assert out[:1] == ["ja"]
    assert "en" in out


def test_standard_plan_order():
    out = resolve_allowed_faq_language_codes("standard", 4, set())
    assert out == ["ja", "en", "zh-TW", "fr"]


def test_premium_uses_premium_code_list():
    out = resolve_allowed_faq_language_codes("premium", None, set())
    assert out == PREMIUM_FAQ_LANGUAGE_CODES


@pytest.mark.parametrize(
    "bad_plan,expected_prefix",
    [
        ("unknown", ["ja", "en", "zh-TW"]),
        ("", ["ja", "en", "zh-TW"]),
    ],
)
def test_invalid_plan_falls_back_to_small(bad_plan, expected_prefix):
    out = resolve_allowed_faq_language_codes(bad_plan, 3, set())
    assert out == expected_prefix
