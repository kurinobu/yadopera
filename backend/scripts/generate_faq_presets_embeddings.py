#!/usr/bin/env python3
"""
FAQプリセット埋め込み 事前計算スクリプト（B5）
FAQ_PRESETS を走査し、各 (intent_key, language) で generate_embedding(question + " " + answer) を呼び、
B3 形式の JSON を backend/app/data/faq_presets_embeddings.json に出力する。

実行: backend/ を cwd にし、OPENAI_API_KEY を設定して
  python scripts/generate_faq_presets_embeddings.py
 または
  PYTHONPATH=. python scripts/generate_faq_presets_embeddings.py
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

# backend を path に追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.faq_presets import FAQ_PRESETS
from app.ai.embeddings import generate_embedding
from app.data.faq_presets_embeddings_constants import (
    EMBEDDINGS_JSON_PATH,
    KEY_META,
    KEY_EMBEDDINGS,
    META_KEY_MODEL,
    META_KEY_GENERATED_AT,
    make_embedding_key,
)

# 埋め込みモデル名（meta に記録。app.ai.openai_client.OpenAIClient.model_embedding と一致）
EMBEDDING_MODEL = "text-embedding-3-small"


async def main() -> None:
    embeddings: dict[str, list[float]] = {}

    for preset in FAQ_PRESETS:
        intent_key = preset.get("intent_key") or ""
        for t in preset.get("translations", []):
            lang = t.get("language", "")
            question = t.get("question", "")
            answer = t.get("answer", "")
            combined = f"{question} {answer}".strip()
            if not combined:
                continue
            key = make_embedding_key(intent_key, lang)
            vec = await generate_embedding(combined)
            if vec:
                embeddings[key] = vec
            else:
                print(f"WARNING: empty embedding for {key}", file=sys.stderr)

    meta = {
        META_KEY_MODEL: EMBEDDING_MODEL,
        META_KEY_GENERATED_AT: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    payload = {KEY_META: meta, KEY_EMBEDDINGS: embeddings}

    EMBEDDINGS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EMBEDDINGS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Written {len(embeddings)} embeddings to {EMBEDDINGS_JSON_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
