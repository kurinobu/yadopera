"""
Feature flag tests.
"""

from app.core.feature_flags import is_contact_capture_enabled


def test_contact_capture_flag_default_off(monkeypatch):
    monkeypatch.delenv("ENABLE_CONTACT_CAPTURE", raising=False)
    assert is_contact_capture_enabled() is False


def test_contact_capture_flag_true_values(monkeypatch):
    for raw in ("1", "true", "TRUE", "yes", "on"):
        monkeypatch.setenv("ENABLE_CONTACT_CAPTURE", raw)
        assert is_contact_capture_enabled() is True


def test_contact_capture_flag_false_values(monkeypatch):
    for raw in ("0", "false", "off", "no", ""):
        monkeypatch.setenv("ENABLE_CONTACT_CAPTURE", raw)
        assert is_contact_capture_enabled() is False

