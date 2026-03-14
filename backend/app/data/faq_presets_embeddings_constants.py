"""
FAQプリセット埋め込み 事前計算JSON の構造定義（B3）
ローダー（faq_presets_embeddings_loader）と事前計算スクリプト（generate_faq_presets_embeddings）
で共通利用するキー・パス・形式を定義する。
"""

from pathlib import Path

# 出力JSONのパス（backend ルート基準の相対パス。実行コンテキストに応じて app/data から解決）
_THIS_DIR = Path(__file__).resolve().parent
EMBEDDINGS_JSON_PATH: Path = _THIS_DIR / "faq_presets_embeddings.json"

# ルートキー
KEY_META = "meta"
KEY_EMBEDDINGS = "embeddings"

# meta 内キー
META_KEY_MODEL = "model"
META_KEY_GENERATED_AT = "generated_at"

# 埋め込みベクトル次元数（text-embedding-3-small）
EMBEDDING_DIMENSION = 1536


def make_embedding_key(intent_key: str, language: str) -> str:
    """
    embeddings 辞書のキーを生成する。
    形式: "{intent_key}:{language}"（例: basic_quiet_hours:ja）
    """
    return f"{intent_key}:{language}"


# JSON ルート構造（参照用 doc）
# {
#   "meta": {
#     "model": "text-embedding-3-small",
#     "generated_at": "2026-03-14T12:00:00Z"  # ISO8601
#   },
#   "embeddings": {
#     "basic_quiet_hours:ja": [0.01, -0.02, ...],  # 1536次元
#     "basic_quiet_hours:en": [...],
#     ...
#   }
# }
