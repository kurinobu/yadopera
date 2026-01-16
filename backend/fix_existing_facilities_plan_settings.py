"""
既存施設のプラン設定を修正するスクリプト
ステージング環境の既存データ（ID 31-71）に対して、subscription_planからplan_typeとmonthly_question_limitを設定
"""

import asyncio
import sys
import os
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.models.facility import Facility
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_subscription_plan_to_plan_type(subscription_plan: str) -> str:
    """subscription_planをplan_typeに変換"""
    plan_mapping = {
        'free': 'Free',
        'mini': 'Mini',
        'small': 'Small',
        'standard': 'Standard',
        'premium': 'Premium'
    }
    return plan_mapping.get(subscription_plan.lower() if subscription_plan else 'free', 'Free')


def get_plan_defaults(plan_type: str) -> dict:
    """プラン種別に応じたデフォルト値を取得"""
    defaults = {
        'Free': {
            'monthly_question_limit': 30,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Mini': {
            'monthly_question_limit': None,  # 無制限
            'faq_limit': 20,
            'language_limit': 1
        },
        'Small': {
            'monthly_question_limit': 200,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Standard': {
            'monthly_question_limit': 500,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Premium': {
            'monthly_question_limit': 1000,
            'faq_limit': None,  # 無制限
            'language_limit': None  # 無制限
        }
    }
    return defaults.get(plan_type, defaults['Free'])


async def fix_existing_facilities():
    """既存施設のプラン設定を修正"""
    # 環境変数DATABASE_URLを優先的に使用
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = settings.database_url
    
    logger.info(f"接続先データベース: {db_url[:60]}..." if len(db_url) > 60 else f"接続先データベース: {db_url}")
    
    engine = create_async_engine(db_url.replace('postgresql://', 'postgresql+asyncpg://'))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # ID 31-71の範囲の施設を取得
        result = await session.execute(
            select(Facility)
            .where(Facility.id >= 31, Facility.id <= 71)
            .order_by(Facility.id)
        )
        facilities = result.scalars().all()
        
        logger.info(f"修正対象施設数: {len(facilities)}")
        
        fixed_count = 0
        for facility in facilities:
            # subscription_planからplan_typeを変換
            plan_type = convert_subscription_plan_to_plan_type(facility.subscription_plan)
            plan_defaults = get_plan_defaults(plan_type)
            
            # 修正が必要かチェック
            needs_update = False
            
            if facility.plan_type != plan_type:
                facility.plan_type = plan_type
                needs_update = True
                logger.info(f"Facility ID {facility.id}: plan_typeを'{facility.plan_type}'から'{plan_type}'に更新")
            
            if facility.monthly_question_limit != plan_defaults['monthly_question_limit']:
                facility.monthly_question_limit = plan_defaults['monthly_question_limit']
                needs_update = True
                logger.info(f"Facility ID {facility.id}: monthly_question_limitを{plan_defaults['monthly_question_limit']}に更新")
            
            if facility.faq_limit != plan_defaults['faq_limit']:
                facility.faq_limit = plan_defaults['faq_limit']
                needs_update = True
                logger.info(f"Facility ID {facility.id}: faq_limitを{plan_defaults['faq_limit']}に更新")
            
            if facility.language_limit != plan_defaults['language_limit']:
                facility.language_limit = plan_defaults['language_limit']
                needs_update = True
                logger.info(f"Facility ID {facility.id}: language_limitを{plan_defaults['language_limit']}に更新")
            
            if needs_update:
                fixed_count += 1
                logger.info(f"Facility ID {facility.id} ({facility.name}): {facility.subscription_plan} -> {plan_type}, monthly_question_limit={plan_defaults['monthly_question_limit']}")
        
        if fixed_count > 0:
            await session.commit()
            logger.info(f"✅ {fixed_count}件の施設を修正しました")
        else:
            logger.info("✅ 修正が必要な施設はありませんでした")
        
        # 修正結果を確認
        logger.info("\n修正後の確認:")
        result = await session.execute(
            select(Facility)
            .where(Facility.id >= 31, Facility.id <= 71)
            .order_by(Facility.id)
        )
        facilities = result.scalars().all()
        
        for facility in facilities:
            logger.info(f"ID {facility.id}: {facility.name} | subscription_plan={facility.subscription_plan} | plan_type={facility.plan_type} | monthly_question_limit={facility.monthly_question_limit}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix_existing_facilities())

