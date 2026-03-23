"""
CSV一括登録用パーサー（csv_parser）のテスト
"""

import pytest
from app.services.csv_parser import (
    CSVParseError,
    parse_faq_csv,
    extract_languages_from_rows,
)


class TestParseFaqCsv:
    """parse_faq_csv のテスト"""

    def test_empty_bytes_raises(self):
        """空の bytes の場合は CSVParseError"""
        with pytest.raises(CSVParseError) as exc_info:
            parse_faq_csv(b"")
        assert "空です" in str(exc_info.value)

    def test_missing_required_columns_raises(self):
        """必須カラム欠落の場合は CSVParseError"""
        csv_bytes = b"category,language_ja_question\nbasic,Q"
        with pytest.raises(CSVParseError) as exc_info:
            parse_faq_csv(csv_bytes)
        assert "language_ja_answer" in str(exc_info.value)

    def test_invalid_category_raises(self):
        """不正なカテゴリの場合は CSVParseError（行番号付き）"""
        csv_bytes = (
            b"category,language_ja_question,language_ja_answer\n"
            b"invalid_category,Question?,Answer."
        )
        with pytest.raises(CSVParseError) as exc_info:
            parse_faq_csv(csv_bytes)
        assert "行 2" in str(exc_info.value) or "カテゴリ" in str(exc_info.value)
        assert "invalid_category" in str(exc_info.value)

    def test_valid_minimal_returns_rows(self):
        """必須3カラムのみの正常系 CSV は辞書リストを返す"""
        csv_bytes = (
            "category,language_ja_question,language_ja_answer\n"
            "basic,チェックアウトは何時ですか？,11時までです。\n"
            "facilities,WiFiは？,guest2024です。"
        ).encode("utf-8")
        rows = parse_faq_csv(csv_bytes)
        assert len(rows) == 2
        assert rows[0]["category"] == "basic"
        assert rows[0]["language_ja_question"] == "チェックアウトは何時ですか？"
        assert rows[0]["language_ja_answer"] == "11時までです。"
        assert rows[1]["category"] == "facilities"

    def test_utf8_bom_minimal_returns_rows(self):
        """UTF-8 BOM 付きの正常系 CSV もパースできる"""
        csv_bytes = (
            b"\xef\xbb\xbfcategory,language_ja_question,language_ja_answer\n"
            b"basic,Q,A"
        )
        rows = parse_faq_csv(csv_bytes)
        assert len(rows) == 1
        assert rows[0]["category"] == "basic"

    def test_optional_intent_key_priority(self):
        """オプションカラム intent_key, priority が含まれる CSV"""
        csv_bytes = (
            b"category,language_ja_question,language_ja_answer,intent_key,priority\n"
            b"basic,Q,A,basic_foo,5"
        )
        rows = parse_faq_csv(csv_bytes)
        assert len(rows) == 1
        assert rows[0].get("intent_key") == "basic_foo"
        assert rows[0].get("priority") == 5

    def test_ja_only_required_empty_optional_question_raises(self):
        """日本語の質問が空の行はエラー"""
        csv_bytes = (
            b"category,language_ja_question,language_ja_answer\n"
            b"basic,,Answer only"
        )
        with pytest.raises(CSVParseError) as exc_info:
            parse_faq_csv(csv_bytes)
        assert "日本語" in str(exc_info.value) or "必須" in str(exc_info.value)


class TestExtractLanguagesFromRows:
    """extract_languages_from_rows のテスト"""

    def test_ja_only_returns_ja(self):
        """日本語のみの行リストは {'ja'}"""
        rows = [
            {"category": "basic", "language_ja_question": "Q", "language_ja_answer": "A"}
        ]
        assert extract_languages_from_rows(rows) == {"ja"}

    def test_ja_and_en_returns_ja_en(self):
        """日本語と英語のカラムがある行は {'ja', 'en'}"""
        rows = [
            {
                "category": "basic",
                "language_ja_question": "Q",
                "language_ja_answer": "A",
                "language_en_question": "What?",
                "language_en_answer": "Answer.",
            }
        ]
        assert extract_languages_from_rows(rows) == {"ja", "en"}

    def test_multiple_languages(self):
        """複数言語カラムが混在する行リスト"""
        rows = [
            {
                "category": "basic",
                "language_ja_question": "Q",
                "language_ja_answer": "A",
                "language_zh-TW_question": "Qzh",
                "language_zh-TW_answer": "Azh",
            }
        ]
        assert extract_languages_from_rows(rows) == {"ja", "zh-TW"}
