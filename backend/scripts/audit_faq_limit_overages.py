"""
A5: 既存施設のFAQ上限超過棚卸しスクリプト

- facilities.faq_limit と FAQ実件数（インテント単位）を照合
- 上限超過施設を抽出
- 接続先指紋（DB名/ホスト/ポート）を出力
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        from app.core.config import settings  # lazy import

        db_url = settings.database_url

    if not db_url:
        print("❌ DATABASE_URL が設定されていません。")
        return 2

    engine = create_async_engine(_to_asyncpg_url(db_url))
    try:
        async with engine.connect() as conn:
            # 接続先指紋
            fp = await conn.execute(
                text(
                    "select current_database() as db, inet_server_addr() as host, inet_server_port() as port"
                )
            )
            row = fp.mappings().first()
            print("== Connection fingerprint ==")
            print(f"db={row['db']} host={row['host']} port={row['port']}")

            # 施設ごとの件数・上限照合
            result = await conn.execute(
                text(
                    """
                    select
                      f.id,
                      f.name,
                      f.plan_type,
                      f.subscription_plan,
                      f.faq_limit,
                      count(q.id) as faq_count
                    from facilities f
                    left join faqs q on q.facility_id = f.id
                    group by f.id, f.name, f.plan_type, f.subscription_plan, f.faq_limit
                    order by f.id
                    """
                )
            )
            rows = result.mappings().all()

            over = []
            for r in rows:
                limit = r["faq_limit"]
                count = int(r["faq_count"] or 0)
                if limit is not None and count > int(limit):
                    over.append(r)

            print("\n== Summary ==")
            print(f"facilities={len(rows)} over_limit={len(over)}")

            print("\n== Over limit facilities ==")
            if not over:
                print("none")
            else:
                for r in over:
                    print(
                        f"id={r['id']} name={r['name']} plan_type={r['plan_type']} "
                        f"subscription_plan={r['subscription_plan']} "
                        f"faq_count={r['faq_count']} faq_limit={r['faq_limit']}"
                    )
    except Exception as e:
        print(f"❌ audit failed: {e}")
        return 1
    finally:
        await engine.dispose()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

