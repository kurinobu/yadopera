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

from sqlalchemy import func, select
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


async def run(
    facility_id: int | None,
    csv_path: str,
    dry_run: bool,
    user_email: str | None = None,
) -> None:
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
        user_id: int
        resolved_facility_id: int

        if user_email:
            email_norm = user_email.strip().lower()
            result = await db.execute(
                select(User).where(func.lower(User.email) == email_norm)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"ユーザーが見つかりません: email={user_email}")
            if not user.facility_id:
                raise ValueError(
                    f"ユーザー {user_email} に施設が紐づいていません（facility_id なし）"
                )
            user_id = user.id
            resolved_facility_id = user.facility_id
        else:
            assert facility_id is not None
            resolved_facility_id = facility_id
            result = await db.execute(
                select(User).where(User.facility_id == facility_id).limit(1)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(
                    f"施設 facility_id={facility_id} に紐づくユーザーが1人もいません。代行実行には対象施設のユーザーが最低1人必要です。"
                )
            user_id = user.id

        facility = await db.get(Facility, resolved_facility_id)
        if not facility:
            raise ValueError(f"施設が見つかりません: facility_id={resolved_facility_id}")

        if facility.plan_type not in ("Standard", "Premium"):
            raise ValueError(
                f"CSV一括登録はStandard/Premiumプランのみ利用可能です（現在: {facility.plan_type}）"
            )

        if dry_run:
            rows = parse_faq_csv(file_bytes)
            if not rows:
                raise ValueError("CSVに有効なデータ行がありません")
            print(f"🔍 ドライラン: facility_id={resolved_facility_id}")
            if user_email:
                print(f"   指定ユーザー: {user_email}")
            print(f"   施設名: {getattr(facility, 'name', 'N/A')}")
            print(f"   プラン: {facility.plan_type}")
            print(f"   uploaded_by に使用するユーザーID: {user_id}")
            print(f"   CSV行数: {len(rows)} 件（実際には登録しません）")
            return

        faq_service = FAQService(db)
        result = await faq_service.bulk_create_faqs_from_csv(
            facility_id=resolved_facility_id,
            file_bytes=file_bytes,
            user_id=user_id,
            mode="add",
        )
        print("✅ CSV一括登録完了")
        print(f"   施設ID: {resolved_facility_id}")
        print(f"   登録件数: {result['success_count']}")
        print(f"   処理時間: {result['processing_time_seconds']} 秒")
        print(f"   uploaded_at: {result['uploaded_at']}")
        print(f"   uploaded_by: {result['uploaded_by']}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="指定施設にCSVからFAQを一括登録（代行履行用・方法C）"
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--facility-id",
        type=int,
        help="対象施設ID（--user-email とどちらか一方）",
    )
    target.add_argument(
        "--user-email",
        type=str,
        help="対象ユーザーのメール（施設はこのユーザーに紐づく facility_id。uploaded_by もこのユーザー）",
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
        asyncio.run(
            run(
                facility_id=args.facility_id,
                csv_path=args.csv,
                dry_run=args.dry_run,
                user_email=args.user_email,
            )
        )
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
