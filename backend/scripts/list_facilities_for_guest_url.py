"""
ゲスト画面用URLのための施設一覧取得スクリプト

ローカル・ステージング問わず、DBに登録されている施設の id / slug を表示し、
ゲスト画面（ウェルカム・チャット等）のURLを提示する。
実行: backend ディレクトリで DATABASE_URL を設定したうえで
  python scripts/list_facilities_for_guest_url.py
Docker 利用時例:
  docker compose exec backend python scripts/list_facilities_for_guest_url.py
"""
import asyncio
import os
import sys

# backend の app を import するため
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.facility import Facility


def get_async_database_url() -> str:
    database_url = os.getenv("DATABASE_URL") or getattr(settings, "database_url", None)
    if not database_url:
        return ""
    if database_url.startswith("postgresql://") and "asyncpg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


async def main() -> None:
    async_database_url = get_async_database_url()
    if not async_database_url:
        print("❌ エラー: DATABASE_URL が設定されていません")
        print("  .env または環境変数 DATABASE_URL を設定してください")
        sys.exit(1)

    # フロントのベースURL（環境に応じて変更可能）
    frontend_base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

    engine = create_async_engine(async_database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(
                Facility.id,
                Facility.slug,
                Facility.name,
                Facility.is_active,
                Facility.plan_type,
            ).where(Facility.is_active == True).order_by(Facility.id)
        )
        rows = result.all()

    if not rows:
        print("登録されている施設がありません。")
        print("ローカルでテストする場合は create_test_data.py を実行すると slug=test-facility の施設が作成されます。")
        return

    # Premium プランの施設を先頭に
    premium_rows = [(r[0], r[1], r[2], r[3], r[4]) for r in rows if (r[4] or "").lower() == "premium"]
    other_rows = [(r[0], r[1], r[2], r[3], r[4]) for r in rows if (r[4] or "").lower() != "premium"]
    sorted_rows = premium_rows + other_rows

    print("=" * 80)
    print("ゲスト画面用URL（テスト用施設一覧）")
    print("=" * 80)
    print(f"フロントベースURL: {frontend_base}")
    print("※ パスの {slug} には slug または id（数値）のどちらも利用可能です。")
    print("※ 多言語表示の確認は Premium プラン施設で行うと、利用可能言語が最大（7言語）になります。")
    print()
    print(f"{'ID':<6} {'プラン':<10} {'slug':<32} {'名前':<18}")
    print("-" * 80)
    for id_, slug, name, _, plan in sorted_rows:
        name_short = (name or "")[:16] + (".." if len(name or "") > 16 else "")
        plan_str = (plan or "—")[:10]
        print(f"{id_:<6} {plan_str:<10} {slug:<32} {name_short:<18}")
    print("-" * 80)
    if premium_rows:
        print()
        print("【Premium プラン施設（多言語テスト推奨）】")
        for id_, slug, name, _, plan in premium_rows:
            segment = slug or str(id_)
            print(f"  {frontend_base}/f/{segment}/welcome?lang=ja")
            print(f"  {frontend_base}/f/{segment}/welcome?lang=en")
            print(f"  {frontend_base}/f/{segment}/welcome?lang=fr")
            print(f"  ※ 上記: id={id_}, slug={slug}, name={name or '(無名)'}")
        print()
    print("【全施設のゲスト画面用URL例】")
    for id_, slug, name, _, plan in sorted_rows:
        # slug を優先表示（QRコード等では slug が使われるため）
        segment = slug or str(id_)
        plan_str = (plan or "—")[:10]
        print(f"  施設: {name or '(無名)'} (id={id_}, slug={slug}, プラン={plan_str})")
        print(f"    言語選択:   {frontend_base}/f/{segment}")
        print(f"    ウェルカム: {frontend_base}/f/{segment}/welcome?lang=ja")
        print(f"    チャット:   {frontend_base}/f/{segment}/chat?lang=ja")
        print(f"    多言語確認: ?lang=ja | ?lang=en | ?lang=fr | ?lang=zh-CN | ?lang=ko 等")
        print()
    print("ローカルでは上記の施設はすべてテスト用として利用できます。")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
