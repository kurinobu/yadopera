"""
FAQプリセット埋め込み 事前計算JSON のローダー（B4）
モジュールロード時に faq_presets_embeddings.json を読み、
get_preset_embedding(intent_key, language) で事前計算済みベクトルを返す。
ファイルが無い・キーが無い場合は None を返す。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.data.faq_presets_embeddings_constants import (
    EMBEDDINGS_JSON_PATH,
    KEY_EMBEDDINGS,
    make_embedding_key,
)

logger = logging.getLogger(__name__)

# モジュールロード時に1回だけ読み込んだ embeddings 辞書（キー: intent_key:lang, 値: list[float]）
_embeddings_map: Optional[Dict[str, List[float]]] = None


def _load_embeddings_json() -> None:
    """JSON ファイルを読み、_embeddings_map に格納する。ファイルが無い場合は空のまま。"""
    global _embeddings_map
    if _embeddings_map is not None:
        return
    if not EMBEDDINGS_JSON_PATH.exists():
        logger.debug(
            "faq_presets_embeddings.json not found at %s, preset embeddings disabled",
            EMBEDDINGS_JSON_PATH,
        )
        _embeddings_map = {}
        return
    try:
        with open(EMBEDDINGS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _embeddings_map = data.get(KEY_EMBEDDINGS) or {}
        if not isinstance(_embeddings_map, dict):
            logger.warning(
                "faq_presets_embeddings.json: '%s' is not a dict, preset embeddings disabled",
                KEY_EMBEDDINGS,
            )
            _embeddings_map = {}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(
            "Failed to load faq_presets_embeddings.json: %s, preset embeddings disabled",
            e,
        )
        _embeddings_map = {}


def get_preset_embedding(intent_key: str, language: str) -> Optional[List[float]]:
    """
    事前計算済み埋め込みベクトルを取得する。

    Args:
        intent_key: プリセットの intent_key（例: basic_quiet_hours）
        language: 言語コード（例: ja, en）

    Returns:
        1536次元の float リスト。ファイルが無い・キーが無い・不正な値の場合は None。
    """
    _load_embeddings_json()
    if _embeddings_map is None or not _embeddings_map:
        return None
    key = make_embedding_key(intent_key, language)
    value = _embeddings_map.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(x, (int, float)) for x in value):
        return None
    return list(value)


# モジュールロード時に JSON を1回読み込む
_load_embeddings_json()
