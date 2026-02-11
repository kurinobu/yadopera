"""
CSVファイルの文字コード検出（CSV一括登録用）
BOM → chardet → UTF-8/CP932 フォールバック
"""

from typing import Optional, Tuple

try:
    import chardet
except ImportError:
    chardet = None  # type: ignore


def detect_encoding(file_bytes: bytes) -> Tuple[Optional[str], float]:
    """
    CSVファイルの文字コードを検出する。

    Returns:
        (encoding, confidence). 検出できない場合は (None, 0.0)。
    """
    if not file_bytes:
        return (None, 0.0)

    # 1. BOM チェック
    if file_bytes.startswith(b"\xef\xbb\xbf"):
        return ("utf-8-sig", 1.0)
    if file_bytes.startswith(b"\xff\xfe"):
        return ("utf-16-le", 1.0)
    if file_bytes.startswith(b"\xfe\xff"):
        return ("utf-16-be", 1.0)

    # 2. chardet で検出
    if chardet is not None:
        result = chardet.detect(file_bytes)
        enc = result.get("encoding")
        confidence = result.get("confidence") or 0.0
        if enc and confidence >= 0.8:
            # よくある別名を統一
            if enc.lower() in ("shift_jis", "shift-jis", "cp932", "windows-31j"):
                return ("cp932", confidence)
            if enc.lower() in ("utf-8", "utf_8"):
                return ("utf-8", confidence)
            return (enc, confidence)

    # 3. フォールバック: UTF-8
    try:
        file_bytes.decode("utf-8")
        return ("utf-8", 0.7)
    except UnicodeDecodeError:
        pass

    # 4. フォールバック: CP932
    try:
        file_bytes.decode("cp932")
        return ("cp932", 0.6)
    except UnicodeDecodeError:
        pass

    return (None, 0.0)
