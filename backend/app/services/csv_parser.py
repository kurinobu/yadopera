"""
CSV一括登録用パーサー
必須カラム検証・行バリデーション・FAQRequest 用の辞書リストを返す
"""

import io
import logging
from typing import Any, Dict, List, Optional, Set

import pandas as pd

from app.utils.encoding_detector import detect_encoding

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["category", "language_ja_question", "language_ja_answer"]
VALID_CATEGORIES = {"basic", "facilities", "location", "trouble"}
LANG_PAIRS = [
    ("ja", "language_ja_question", "language_ja_answer"),
    ("en", "language_en_question", "language_en_answer"),
    ("zh-TW", "language_zh-TW_question", "language_zh-TW_answer"),
    ("fr", "language_fr_question", "language_fr_answer"),
    ("ko", "language_ko_question", "language_ko_answer"),
]
QUESTION_MAX_LEN = 500
ANSWER_MAX_LEN = 2000


class CSVParseError(ValueError):
    """CSV解析・バリデーションエラー"""
    pass


def parse_faq_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    CSV をパースし、行ごとの辞書リストを返す。
    必須カラム検証・文字コード検出を行う。

    Raises:
        CSVParseError: 必須カラム欠落・文字コード検出失敗・空ファイルなど
    """
    if not file_bytes or len(file_bytes) == 0:
        raise CSVParseError("CSVファイルが空です")

    encoding, confidence = detect_encoding(file_bytes)
    if encoding is None:
        raise CSVParseError(
            "CSVファイルの文字コードを検出できませんでした。UTF-8（BOM付き推奨）で保存してください。"
        )

    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
    except Exception as e:
        logger.warning(f"pandas read_csv failed: {e}")
        raise CSVParseError("CSVファイルの形式が不正です") from e

    # カラム名の前後空白除去
    df.columns = df.columns.str.strip() if hasattr(df.columns, "str") else df.columns

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise CSVParseError(f"必須カラムが不足しています: {', '.join(sorted(missing))}")

    # 空行を除く
    df = df.dropna(how="all").reset_index(drop=True)
    if len(df) == 0:
        raise CSVParseError("CSVにデータ行がありません")

    rows: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        row_num = int(idx) + 2  # 1-based + ヘッダー
        d = _row_to_dict(row, row_num)
        if d is not None:
            rows.append(d)
    return rows


def _row_to_dict(row: pd.Series, row_num: int) -> Optional[Dict[str, Any]]:
    """1行を辞書に変換。必須が空の行はスキップ（None）。バリデーションでエラーなら CSVParseError."""
    cat = _get_str(row, "category", row_num).strip().lower()
    if cat not in VALID_CATEGORIES:
        raise CSVParseError(f"行 {row_num}: カテゴリは basic / facilities / location / trouble のいずれかを指定してください（値: {cat}）")

    q_ja = _get_str(row, "language_ja_question", row_num)
    a_ja = _get_str(row, "language_ja_answer", row_num)
    if not q_ja or not a_ja:
        raise CSVParseError(f"行 {row_num}: 日本語の質問文・回答文は必須です")

    if len(q_ja) > QUESTION_MAX_LEN:
        raise CSVParseError(f"行 {row_num}: 質問文は{QUESTION_MAX_LEN}文字以内で入力してください")
    if len(a_ja) > ANSWER_MAX_LEN:
        raise CSVParseError(f"行 {row_num}: 回答文は{ANSWER_MAX_LEN}文字以内で入力してください")

    out: Dict[str, Any] = {
        "category": cat,
        "language_ja_question": q_ja,
        "language_ja_answer": a_ja,
        "_row_num": row_num,
    }

    intent_key = _get_str_opt(row, "intent_key")
    if intent_key:
        intent_key = intent_key.strip()
        if len(intent_key) > 100:
            raise CSVParseError(f"行 {row_num}: intent_key は100文字以内で指定してください")
        out["intent_key"] = intent_key

    priority = _get_int_opt(row, "priority", 3, 1, 5)
    out["priority"] = priority

    is_active = _get_bool_opt(row, "is_active", True)
    out["is_active"] = is_active

    for lang, col_q, col_a in LANG_PAIRS:
        if lang == "ja":
            continue
        q = _get_str_opt(row, col_q)
        a = _get_str_opt(row, col_a)
        if q is not None or a is not None:
            q = (q or "").strip()
            a = (a or "").strip()
            if q and len(q) > QUESTION_MAX_LEN:
                raise CSVParseError(f"行 {row_num}: {col_q} は{QUESTION_MAX_LEN}文字以内で入力してください")
            if a and len(a) > ANSWER_MAX_LEN:
                raise CSVParseError(f"行 {row_num}: {col_a} は{ANSWER_MAX_LEN}文字以内で入力してください")
            out[col_q] = q or None
            out[col_a] = a or None

    return out


def _get_str(row: pd.Series, key: str, row_num: int) -> str:
    if key not in row:
        raise CSVParseError(f"行 {row_num}: 必須カラム {key} がありません")
    v = row[key]
    if pd.isna(v):
        return ""
    return str(v).strip()


def _get_str_opt(row: pd.Series, key: str) -> Optional[str]:
    if key not in row or pd.isna(row[key]):
        return None
    s = str(row[key]).strip()
    return s if s else None


def _get_int_opt(row: pd.Series, key: str, default: int, lo: int, hi: int) -> int:
    if key not in row or pd.isna(row[key]):
        return default
    try:
        v = int(row[key])
        return max(lo, min(hi, v))
    except (ValueError, TypeError):
        return default


def _get_bool_opt(row: pd.Series, key: str, default: bool) -> bool:
    if key not in row or pd.isna(row[key]):
        return default
    v = row[key]
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return default


def extract_languages_from_rows(rows: List[Dict[str, Any]]) -> Set[str]:
    """パース済み行リストから、含まれる言語コードの集合を返す（ja は常に含まれる）。"""
    langs: Set[str] = {"ja"}
    for r in rows:
        for lang, col_q, col_a in LANG_PAIRS:
            if lang == "ja":
                continue
            if r.get(col_q) or r.get(col_a):
                langs.add(lang)
    return langs
