"""
Smallプラン超過テスト用データ作成スクリプト（テスト2-6用）

テスト2-6: Smallプラン（超過：220件）のデータを作成します。
"""
import asyncio
import sys
from datetime import datetime, timedelta
import pytz
import uuid
sys.path.insert(0, '/app')
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, delete
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.core.config import settings


async def create_small_overage_test_data():
    """Smallプラン超過テスト用データを作成（テスト2-6用）"""
    engine = create_async_engine(settings.database_url.replace('postgresql://', 'postgresql+asyncpg://'))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        month_start_jst = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_utc = month_start_jst.astimezone(pytz.UTC)
        
        small_facility_id = 38  # test51@example.com
        
        print('=' * 80)
        print('Smallプラン超過テスト用データ作成（テスト2-6）')
        print('=' * 80)
        
        # 既存データを削除
        existing_conv_result = await session.execute(
            select(Conversation.id)
            .where(Conversation.facility_id == small_facility_id)
            .where(Conversation.started_at >= month_start_utc)
        )
        existing_conv_ids = [row[0] for row in existing_conv_result.all()]
        if existing_conv_ids:
            await session.execute(delete(Message).where(Message.conversation_id.in_(existing_conv_ids)))
            await session.execute(delete(Conversation).where(Conversation.id.in_(existing_conv_ids)))
            await session.commit()
            print(f'  ✅ 既存データを削除しました: {len(existing_conv_ids)}件の会話')
        
        # テスト2-6用: 220件（超過、110% = 赤）
        print('\nテスト2-6用: 220件（超過、110% = 赤）を作成')
        for i in range(220):
            session_id = f'test_small_overage_{small_facility_id}_{uuid.uuid4().hex[:8]}'
            conversation = Conversation(
                facility_id=small_facility_id,
                session_id=session_id,
                guest_language='ja',
                location='entrance',
                started_at=month_start_utc + timedelta(hours=i % 24),
                last_activity_at=month_start_utc + timedelta(hours=i % 24, minutes=5),
                is_escalated=(i < 25),  # 25件をエスカレーション
                total_messages=2 if i < 180 else 1  # 180件にAI自動応答
            )
            session.add(conversation)
            await session.flush()
            
            user_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER.value,
                content=f'テスト質問 {i+1}',
                created_at=month_start_utc + timedelta(hours=i % 24, minutes=1)
            )
            session.add(user_message)
            
            if i < 180:
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT.value,
                    content=f'テスト回答 {i+1}',
                    created_at=month_start_utc + timedelta(hours=i % 24, minutes=2)
                )
                session.add(assistant_message)
        
        await session.commit()
        print(f'  ✅ 220件の質問を作成しました（超過、110% = 赤）')
        print(f'      - AI自動応答数: 180件')
        print(f'      - エスカレーション数: 25件')
        print(f'      - 使用率: 110%')
        print(f'      - ステータス: overage')
        print(f'      - 超過質問数: 20件')
        
        # 最終確認
        questions_result = await session.execute(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                Conversation.facility_id == small_facility_id,
                Message.role == MessageRole.USER.value,
                Message.created_at >= month_start_utc
            )
        )
        question_count = questions_result.scalar() or 0
        usage_percentage = (question_count / 200) * 100
        overage_questions = question_count - 200
        print(f'\n  📊 Smallプラン最終確認:')
        print(f'      質問数: {question_count}件')
        print(f'      使用率: {usage_percentage:.1f}%')
        print(f'      超過質問数: {overage_questions}件')
        print(f'      ✅ テスト2-6（超過）の準備完了')
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_small_overage_test_data())

