#!/usr/bin/env python3
"""
新規登録時 自動登録FAQ 精査用一覧のCSVを出力するスクリプト。
backend/ を cwd にして実行: python scripts/export_faq_presets_for_review.py
出力先: docs/新規登録時_自動登録FAQ_精査用一覧.csv
"""
import csv
import os
import sys

# backend を path に追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.faq_presets import FAQ_PRESETS


def get_ja_qa(preset: dict) -> tuple:
    """プリセットから日本語の質問・回答を取得"""
    for t in preset.get("translations", []):
        if t.get("language") == "ja":
            return (t.get("question", ""), t.get("answer", ""))
    return ("", "")


def main():
    # 優先度順（降順）＝ plan_limits.filter_faq_presets_by_plan と同じ並び
    sorted_presets = sorted(
        FAQ_PRESETS,
        key=lambda x: x.get("priority", 1),
        reverse=True,
    )
    rows = []
    for i, preset in enumerate(sorted_presets, start=1):
        q_ja, a_ja = get_ja_qa(preset)
        投入区分 = "現在投入中（20件）" if i <= 20 else "30件化で追加予定"
        rows.append({
            "No": i,
            "投入区分": 投入区分,
            "intent_key": preset.get("intent_key", ""),
            "category": preset.get("category", ""),
            "priority": preset.get("priority", ""),
            "question_ja": q_ja,
            "answer_ja": a_ja,
            "修正メモ": "",
        })

    # リポジトリルートの docs に出力（backend の2つ上）
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_path = os.path.join(repo_root, "docs", "新規登録時_自動登録FAQ_精査用一覧.csv")

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["No", "投入区分", "intent_key", "category", "priority", "question_ja", "answer_ja", "修正メモ"],
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
