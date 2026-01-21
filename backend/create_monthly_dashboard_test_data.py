"""
月次ダッシュボード統計テスト用データ作成スクリプト

ブラウザテスト手順に基づいて、各プランに適切なテストデータを挿入します。
"""
import asyncio
import sys
from datetime import datetime, timedelta
import pytz
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.models.facility import Facility
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.core.config import settings


async def create_monthly_dashboard_test_data():
    """月次ダッシュボード統計テスト用データを作成"""
    engine = create_async_engine(settings.database_url.replace('postgresql://', 'postgresql+asyncpg://'))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # JSTタイムゾーン取得
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        month_start_jst = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # UTCに変換
        month_start_utc = month_start_jst.astimezone(pytz.UTC)
        
        # テストユーザーと施設のマッピング
        test_users = {
            'test31@example.com': {
                'plan': 'Free',
                'facility_id': 36,
                'test_cases': [
                    {'name': 'Freeプラン（30件以内）', 'question_count': 15, 'ai_responses': 10, 'escalations': 2}
                ]
            },
            'test41@example.com': {
                'plan': 'Mini',
                'facility_id': 37,
                'test_cases': [
                    {'name': 'Miniプラン', 'question_count': 50, 'ai_responses': 40, 'escalations': 5}
                ]
            },
            'test51@example.com': {
                'plan': 'Small',
                'facility_id': 38,
                'test_cases': [
                    {'name': 'Smallプラン（上限内）', 'question_count': 100, 'ai_responses': 80, 'escalations': 10},
                    {'name': 'Smallプラン（警告範囲）', 'question_count': 190, 'ai_responses': 150, 'escalations': 20},
                    {'name': 'Smallプラン（超過）', 'question_count': 220, 'ai_responses': 180, 'escalations': 25}
                ]
            },
            'test61@example.com': {
                'plan': 'Standard',
                'facility_id': 39,
                'test_cases': [
                    {'name': 'Standardプラン', 'question_count': 300, 'ai_responses': 250, 'escalations': 15}
                ]
            },
            'test71@example.com': {
                'plan': 'Premium',
                'facility_id': 40,
                'test_cases': [
                    {'name': 'Premiumプラン', 'question_count': 600, 'ai_responses': 550, 'escalations': 10}
                ]
            }
        }
        
        print("=" * 80)
        print("月次ダッシュボード統計テスト用データ作成")
        print("=" * 80)
        
        for email, config in test_users.items():
            print(f"\n[{email}] {config['plan']}プラン")
            print("-" * 80)
            
            # ユーザーと施設を取得
            user_result = await session.execute(select(User).where(User.email == email).limit(1))
            user = user_result.scalar_one_or_none()
            
            if not user:
                print(f"  ❌ ユーザーが見つかりません: {email}")
                continue
            
            facility_result = await session.execute(
                select(Facility).where(Facility.id == config['facility_id'])
            )
            facility = facility_result.scalar_one_or_none()
            
            if not facility:
                print(f"  ❌ 施設が見つかりません: Facility ID {config['facility_id']}")
                continue
            
            print(f"  ✅ 施設: {facility.name} (ID: {facility.id}, Plan: {facility.plan_type})")
            
            # 既存の今月のデータを確認
            existing_questions_result = await session.execute(
                select(func.count(Message.id))
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(
                    Conversation.facility_id == facility.id,
                    Message.role == MessageRole.USER.value,
                    Message.created_at >= month_start_utc
                )
            )
            existing_count = existing_questions_result.scalar() or 0
            print(f"  📊 既存の今月の質問数: {existing_count}件")
            
            # 各テストケースのデータを作成
            for test_case in config['test_cases']:
                print(f"\n  📝 テストケース: {test_case['name']}")
                print(f"     質問数: {test_case['question_count']}件")
                print(f"     AI自動応答数: {test_case['ai_responses']}件")
                print(f"     エスカレーション数: {test_case['escalations']}件")
                
                # 必要な質問数を計算（既存分を差し引く）
                needed_questions = max(0, test_case['question_count'] - existing_count)
                
                if needed_questions > 0:
                    print(f"     追加で作成: {needed_questions}件の質問")
                    
                    # 会話とメッセージを作成
                    for i in range(needed_questions):
                        # 会話を作成
                        session_id = f"test_monthly_{facility.id}_{uuid.uuid4().hex[:8]}"
                        conversation = Conversation(
                            facility_id=facility.id,
                            session_id=session_id,
                            guest_language="ja",
                            location="entrance",
                            started_at=month_start_utc + timedelta(hours=i % 24),
                            last_activity_at=month_start_utc + timedelta(hours=i % 24, minutes=5),
                            is_escalated=(i < test_case['escalations']),
                            total_messages=2
                        )
                        session.add(conversation)
                        await session.flush()
                        
                        # ユーザーメッセージを作成
                        user_message = Message(
                            conversation_id=conversation.id,
                            role=MessageRole.USER.value,
                            content=f"テスト質問 {i+1}",
                            created_at=month_start_utc + timedelta(hours=i % 24, minutes=1)
                        )
                        session.add(user_message)
                        
                        # AI自動応答メッセージを作成（AI自動応答数の範囲内の場合）
                        if i < test_case['ai_responses']:
                            assistant_message = Message(
                                conversation_id=conversation.id,
                                role=MessageRole.ASSISTANT.value,
                                content=f"テスト回答 {i+1}",
                                created_at=month_start_utc + timedelta(hours=i % 24, minutes=2)
                            )
                            session.add(assistant_message)
                    
                    await session.commit()
                    print(f"     ✅ {needed_questions}件の質問を作成しました")
                else:
                    print(f"      ℹ️  既存データで十分です（追加不要）")
                
                # 既存データを更新してエスカレーション数を調整
                if test_case['escalations'] > 0:
                    # 既存の会話を取得してエスカレーション状態を更新
                    conversations_result = await session.execute(
                        select(Conversation)
                        .where(Conversation.facility_id == facility.id)
                        .where(Conversation.started_at >= month_start_utc)
                        .limit(test_case['escalations'])
                    )
                    conversations = conversations_result.scalars().all()
                    
                    for conv in conversations:
                        conv.is_escalated = True
                    
                    await session.commit()
                    print(f"      ✅ {len(conversations)}件の会話をエスカレーション状態に更新しました")
        
        print("\n" + "=" * 80)
        print("テストデータ作成完了")
        print("=" * 80)
        
        # 最終確認
        print("\n📊 最終確認:")
        for email, config in test_users.items():
            facility_result = await session.execute(
                select(Facility).where(Facility.id == config['facility_id'])
            )
            facility = facility_result.scalar_one_or_none()
            
            if facility:
                questions_result = await session.execute(
                    select(func.count(Message.id))
                    .join(Conversation, Message.conversation_id == Conversation.id)
                    .where(
                        Conversation.facility_id == facility.id,
                        Message.role == MessageRole.USER.value,
                        Message.created_at >= month_start_utc
                    )
                )
                question_count = questions_result.scalar() or 0
                
                ai_responses_result = await session.execute(
                    select(func.count(Message.id))
                    .join(Conversation, Message.conversation_id == Conversation.id)
                    .where(
                        Conversation.facility_id == facility.id,
                        Message.role == MessageRole.ASSISTANT.value,
                        Message.created_at >= month_start_utc
                    )
                )
                ai_count = ai_responses_result.scalar() or 0
                
                escalations_result = await session.execute(
                    select(func.count(Conversation.id))
                    .where(
                        Conversation.facility_id == facility.id,
                        Conversation.is_escalated == True,
                        Conversation.started_at >= month_start_utc
                    )
                )
                escalation_count = escalations_result.scalar() or 0
                
                print(f"  {email} ({config['plan']}):")
                print(f"    質問数: {question_count}件")
                print(f"    AI自動応答数: {ai_count}件")
                print(f"    エスカレーション数: {escalation_count}件")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_monthly_dashboard_test_data())

