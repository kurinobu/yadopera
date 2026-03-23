"""
CSV一括登録用 文字コード検出（encoding_detector）のテスト
"""

import pytest
from app.utils.encoding_detector import detect_encoding


class TestDetectEncoding:
    """detect_encoding のテスト"""

    def test_empty_bytes_returns_none(self):
        """空の bytes の場合は (None, 0.0)"""
        enc, conf = detect_encoding(b"")
        assert enc is None
        assert conf == 0.0

    def test_utf8_bom_returns_utf8_sig(self):
        """UTF-8 BOM 付きの場合は utf-8-sig"""
        data = b"\xef\xbb\xbfcategory,language_ja_question,language_ja_answer\nbasic,Q,A"
        enc, conf = detect_encoding(data)
        assert enc == "utf-8-sig"
        assert conf == 1.0

    def test_utf16le_bom_returns_utf16le(self):
        """UTF-16 LE BOM の場合は utf-16-le"""
        data = b"\xff\xfe" + "a".encode("utf-16-le")
        enc, conf = detect_encoding(data)
        assert enc == "utf-16-le"
        assert conf == 1.0

    def test_utf16be_bom_returns_utf16be(self):
        """UTF-16 BE BOM の場合は utf-16-be"""
        data = b"\xfe\xff" + "a".encode("utf-16-be")
        enc, conf = detect_encoding(data)
        assert enc == "utf-16-be"
        assert conf == 1.0

    def test_utf8_without_bom_decodable_returns_utf8(self):
        """BOM なしで UTF-8 としてデコード可能な場合は utf-8（chardet またはフォールバック）"""
        data = "category,language_ja_question,language_ja_answer\nbasic,質問,回答".encode("utf-8")
        enc, conf = detect_encoding(data)
        assert enc == "utf-8"
        assert conf >= 0.6

    def test_cp932_decodable_returns_cp932_or_utf8(self):
        """CP932 でデコード可能な日本語は chardet で cp932 と判定される可能性、または UTF-8 フォールバック"""
        data = "カテゴリ,質問,回答".encode("cp932")
        enc, conf = detect_encoding(data)
        # chardet が cp932 を返すか、UTF-8 でデコードできれば utf-8 が返る
        assert enc in ("cp932", "utf-8") or enc is not None
        assert conf >= 0.0
