#!/usr/bin/env python3
"""
Stripe 既存顧客の優先言語（preferred_locales）を一括で日本語に設定するスクリプト。

背景:
- Stripe の請求書PDF/領収書PDF/各メールの表示言語は「顧客の優先言語」に影響される。
- 日本以外の顧客がいない前提なら、顧客ごとに手動設定するのは非現実的なので一括更新する。

重要:
- すでに確定（finalized）済みの請求書PDFは、後から言語を変えても基本的に反映されない。
  変更後は「新しく発行・確定される請求書」で日本語になっていることを確認する。

使い方:
  # 事前に STRIPE_SECRET_KEY を環境変数に設定
  STRIPE_SECRET_KEY="sk_test_..." python scripts/set_stripe_customers_preferred_locale_ja.py --dry-run
  STRIPE_SECRET_KEY="sk_test_..." python scripts/set_stripe_customers_preferred_locale_ja.py

Docker（推奨）:
  docker compose run --rm backend python scripts/set_stripe_customers_preferred_locale_ja.py --dry-run
  docker compose run --rm backend python scripts/set_stripe_customers_preferred_locale_ja.py
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

import stripe


def _iter_customers(limit_per_page: int = 100) -> Iterable[stripe.Customer]:
    starting_after = None
    while True:
        params = {"limit": limit_per_page}
        if starting_after:
            params["starting_after"] = starting_after
        resp = stripe.Customer.list(**params)
        data = resp.get("data", []) if isinstance(resp, dict) else resp.data  # type: ignore[attr-defined]
        if not data:
            return
        for c in data:
            yield c
        if hasattr(resp, "has_more"):
            has_more = bool(resp.has_more)  # type: ignore[attr-defined]
        else:
            has_more = bool(resp.get("has_more"))
        if not has_more:
            return
        starting_after = data[-1]["id"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk set Stripe customers preferred_locales to Japanese.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions but do not modify Stripe.")
    parser.add_argument("--only-if-empty", action="store_true", help="Only update customers with no preferred_locales set.")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N updates (0 = no limit).")
    args = parser.parse_args()

    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        print("Error: STRIPE_SECRET_KEY is required in environment.", file=sys.stderr)
        return 2
    stripe.api_key = key

    updated = 0
    scanned = 0
    skipped = 0

    for c in _iter_customers():
        scanned += 1
        cid = c.get("id")
        email = c.get("email") or ""
        current = c.get("preferred_locales") or []

        if args.only_if_empty and current:
            skipped += 1
            continue

        # 既に日本語が先頭ならスキップ（順序も含め厳密にしたい場合はここを変更）
        if current and current[0] == "ja":
            skipped += 1
            continue

        if args.dry_run:
            print(f"[dry-run] update customer={cid} email={email} preferred_locales {current} -> ['ja']")
        else:
            stripe.Customer.modify(cid, preferred_locales=["ja"])
            print(f"updated customer={cid} email={email} preferred_locales {current} -> ['ja']")
        updated += 1

        if args.limit and updated >= args.limit:
            break

    print(f"done scanned={scanned} updated={updated} skipped={skipped} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

