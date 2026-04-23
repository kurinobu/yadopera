"""
Feature flag helpers.
"""

import os


def _is_enabled(raw: str) -> bool:
    value = (raw or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def is_contact_capture_enabled() -> bool:
    """
    C-3（同意ベース連絡先取得）フラグ。
    デフォルトは無効（False）。
    """
    return _is_enabled(os.getenv("ENABLE_CONTACT_CAPTURE", "false"))

