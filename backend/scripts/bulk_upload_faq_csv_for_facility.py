#!/usr/bin/env python3
"""
CSV一括登録 代行履行用スクリプト（方法C）
指定施設に対してCSVファイルからFAQを一括登録する。有料代行サービス運用用。
施設に紐づく1ユーザーを uploaded_by（監査用）として使用する。
"""

import argparse
import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import database_url
from app.models.facility import Facility
from app.models.user import User
from app.services.faq_service import FAQService
from app.services.csv_parser import parse_faq_csv

# 10MB（APIと同一）
MAX_CSV_SIZE_BYTES = 10 * 1024 * 1024

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run(facility_id: int, csv_path: str, dry_run: bool) -> None:
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSVファイルが見つかりません: {csv_path}")

    with open(csv_path, "rb") as f:
        file_bytes = f.read()

    if len(file_bytes) > MAX_CSV_SIZE_BYTES:
        raise ValueError(
            f"ファイルサイズは{MAX_CSV_SIZE_BYTES // (1024*1024)}MB以内にしてください（現在: {len(file_bytes)} bytes）"
        )

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        facility = await db.get(Facility, facility_id)
        if not facility:
            raise ValueError(f"施設が見つかりません: facility_id={facility_id}")

        if facility.plan_type not in ("Standard", "Premium"):
            raise ValueError(
                f"CSV一括登録はStandard/Premiumプランのみ利用可能です（現在: {facility.plan_type}）"
            )

        result = await db.execute(
            select(User).where(User.facility_id == facility_id).limit(1)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(
                f"施設 facility_id={facility_id} に紐づくユーザーが1人もいません。代行実行には対象施設のユーザーが最低1人必要です。"
            )
        user_id = user.id

        if dry_run:
            rows = parse_faq_csv(file_bytes)
            if not rows:
                raise ValueError("CSVに有効なデータ行がありません")
            print(f"🔍 ドライラン: facility_id={facility_id}")
            print(f"   施設名: {getattr(facility, 'name', 'N/A')}")
            print(f"   プラン: {facility.plan_type}")
            print(f"   uploaded_by に使用するユーザーID: {user_id}")
            print(f"   CSV行数: {len(rows)} 件（実際には登録しません）")
            return

        faq_service = FAQService(db)
        result = await faq_service.bulk_create_faqs_from_csv(
            facility_id=facility_id,
            file_bytes=file_bytes,
            user_id=user_id,
            mode="add",
        )
        print("✅ CSV一括登録完了")
        print(f"   施設ID: {facility_id}")
        print(f"   登録件数: {result['success_count']}")
        print(f"   処理時間: {result['processing_time_seconds']} 秒")
        print(f"   uploaded_at: {result['uploaded_at']}")
        print(f"   uploaded_by: {result['uploaded_by']}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="指定施設にCSVからFAQを一括登録（代行履行用・方法C）"
    )
    parser.add_argument(
        "--facility-id",
        type=int,
        required=True,
        help="対象施設ID",
    )
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="CSVファイルのパス（UTF-8。フォーマットは FAQ_CSV_format_guide.md に準拠）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ドライラン（CSV検証と施設チェックのみ。実際には登録しない）",
    )
    args = parser.parse_args()

    try:
        asyncio.run(run(args.facility_id, args.csv, args.dry_run))
    except (FileNotFoundError, ValueError) as e:
        logger.error(str(e))
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("bulk_upload_faq_csv_for_facility error")
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
