#!/usr/bin/env python3
"""
宿泊事業者向けFAQデータ更新スクリプト
既存のFAQデータを修正案に基づいて更新します。
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Pythonパスにbackendディレクトリを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

from app.models.operator_help import OperatorFaq, OperatorFaqTranslation

# insert_operator_faqs.pyからデータをインポート
from scripts.insert_operator_faqs import OPERATOR_FAQ_DATA

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def update_operator_faqs():
    """
    宿泊事業者向けFAQデータ更新
    """
    # DB接続（環境変数DATABASE_URLから取得、なければsettingsから取得）
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        try:
            from app.core.config import settings
            database_url = settings.database_url
        except Exception as e:
            print(f"❌ エラー: DATABASE_URLが設定されていません: {e}")
            print("環境変数DATABASE_URLを設定してください:")
            print("  export DATABASE_URL='postgresql://postgres:password@host:port/database'")
            sys.exit(1)
    
    if database_url.startswith("postgresql://"):
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_database_url = database_url
    
    engine = create_async_engine(async_database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            updated_count = 0
            created_count = 0
            not_found_count = 0

            for faq_data in OPERATOR_FAQ_DATA:
                # 既存チェック
                result = await db.execute(
                    select(OperatorFaq).where(OperatorFaq.intent_key == faq_data['intent_key'])
                )
                existing_faq = result.scalar_one_or_none()

                if existing_faq:
                    # 既存データを更新
                    # 翻訳データを更新
                    for lang, translation_data in faq_data['translations'].items():
                        # 既存の翻訳データを取得
                        trans_result = await db.execute(
                            select(OperatorFaqTranslation).where(
                                OperatorFaqTranslation.faq_id == existing_faq.id,
                                OperatorFaqTranslation.language == lang
                            )
                        )
                        existing_translation = trans_result.scalar_one_or_none()

                        if existing_translation:
                            # 更新
                            existing_translation.question = translation_data['question']
                            existing_translation.answer = translation_data['answer']
                            existing_translation.keywords = translation_data.get('keywords')
                            existing_translation.related_url = translation_data.get('related_url')
                            existing_translation.updated_at = datetime.utcnow()
                            logger.info(f"Updated translation: {faq_data['intent_key']} ({lang})")
                        else:
                            # 新規作成
                            translation = OperatorFaqTranslation(
                                faq_id=existing_faq.id,
                                language=lang,
                                question=translation_data['question'],
                                answer=translation_data['answer'],
                                keywords=translation_data.get('keywords'),
                                related_url=translation_data.get('related_url')
                            )
                            db.add(translation)
                            logger.info(f"Created translation: {faq_data['intent_key']} ({lang})")
                    
                    # FAQマスターも更新（必要に応じて）
                    existing_faq.category = faq_data['category']
                    existing_faq.display_order = faq_data['display_order']
                    existing_faq.is_active = True
                    existing_faq.updated_at = datetime.utcnow()
                    
                    updated_count += 1
                    logger.info(f"Updated FAQ: {faq_data['intent_key']} ({faq_data['category']})")
                else:
                    # 新規作成
                    operator_faq = OperatorFaq(
                        category=faq_data['category'],
                        intent_key=faq_data['intent_key'],
                        display_order=faq_data['display_order'],
                        is_active=True
                    )
                    db.add(operator_faq)
                    await db.flush()  # IDを取得するためにflush

                    # 翻訳データ作成
                    for lang, translation_data in faq_data['translations'].items():
                        translation = OperatorFaqTranslation(
                            faq_id=operator_faq.id,
                            language=lang,
                            question=translation_data['question'],
                            answer=translation_data['answer'],
                            keywords=translation_data.get('keywords'),
                            related_url=translation_data.get('related_url')
                        )
                        db.add(translation)

                    created_count += 1
                    logger.info(f"Created FAQ: {faq_data['intent_key']} ({faq_data['category']})")

            await db.commit()

            logger.info(f"Operator FAQ update completed: updated={updated_count}, created={created_count}")
            print(f"✅ 宿泊事業者向けFAQデータ更新完了")
            print(f"   更新数: {updated_count}")
            print(f"   作成数: {created_count}")

            # カテゴリ別集計
            result = await db.execute(
                select(OperatorFaq.category, func.count(OperatorFaq.id))
                .group_by(OperatorFaq.category)
            )
            categories = {row[0]: row[1] for row in result.all()}
            print(f"   カテゴリ別: {categories}")

        except Exception as e:
            logger.error(f"Error updating operator FAQs: {str(e)}", exc_info=True)
            await db.rollback()
            print(f"❌ エラー発生: {str(e)}")
            raise
        finally:
            await engine.dispose()


def main():
    """メイン関数"""
    print("🚀 宿泊事業者向けFAQデータ更新を開始します...")
    print(f"   更新予定数: {len(OPERATOR_FAQ_DATA)}件")
    asyncio.run(update_operator_faqs())


if __name__ == "__main__":
    main()

