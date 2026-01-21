#!/usr/bin/env python3
"""
FAQプリセット投入スクリプト
指定された施設に30個のFAQプリセットを一括投入します。
"""

import asyncio
import argparse
import logging
import sys
import os

# Pythonパスにbackendディレクトリを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import database_url
from app.services.faq_service import FAQService
from app.data.faq_presets import FAQ_PRESETS
from app.schemas.faq import FAQRequest

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def apply_faq_presets(facility_id: int):
    """
    指定施設にFAQプリセットを投入

    Args:
        facility_id: 対象施設ID
    """
    # DB接続
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # FAQサービス初期化
            faq_service = FAQService(db)

            # プリセットをFAQRequestに変換
            faq_requests = []
            for preset in FAQ_PRESETS:
                request = FAQRequest(
                    category=preset["category"],
                    intent_key=preset["intent_key"],
                    priority=preset["priority"],
                    translations=preset["translations"],
                    is_active=True
                )
                faq_requests.append(request)

            logger.info(f"Starting bulk FAQ creation for facility_id={facility_id}, presets_count={len(faq_requests)}")

            # 一括作成実行（システムユーザーとして）
            created_faqs = await faq_service.bulk_create_faqs(
                facility_id=facility_id,
                faq_requests=faq_requests,
                user_id=None  # システム生成
            )

            logger.info(f"Bulk FAQ creation completed: created={len(created_faqs)}, facility_id={facility_id}")

            # 結果出力
            print(f"✅ プリセットFAQ投入完了")
            print(f"   施設ID: {facility_id}")
            print(f"   投入依頼数: {len(faq_requests)}")
            print(f"   作成成功数: {len(created_faqs)}")

            if len(created_faqs) < len(faq_requests):
                print(f"   ⚠️  {len(faq_requests) - len(created_faqs)}件のFAQが重複などでスキップされました")

            # カテゴリ別集計
            categories = {}
            for faq in created_faqs:
                categories[faq.category] = categories.get(faq.category, 0) + 1
            print(f"   カテゴリ別: {categories}")

        except Exception as e:
            logger.error(f"Error applying FAQ presets: {str(e)}", exc_info=True)
            print(f"❌ エラー発生: {str(e)}")
            raise
        finally:
            await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description='FAQプリセットを指定施設に投入します')
    parser.add_argument('--facility-id', type=int, required=True, help='対象施設ID')
    parser.add_argument('--dry-run', action='store_true', help='ドライラン（実際には投入しない）')

    args = parser.parse_args()

    if args.dry_run:
        print(f"🔍 ドライラン: 施設ID {args.facility_id} に {len(FAQ_PRESETS)}件のFAQを投入します")
        return

    # 非同期実行
    asyncio.run(apply_faq_presets(args.facility_id))


if __name__ == "__main__":
    main()