"""
ステージング環境用：月次ダッシュボード統計テスト用データ作成スクリプト

test32, test42, test52, test62, test72用のテストデータを作成します。
"""
import asyncio
import sys
from datetime import datetime, timedelta
import pytz
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, delete
from app.models.facility import Facility
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from app.core.config import settings


async def create_staging_monthly_dashboard_test_data():
    """ステージング環境用：月次ダッシュボード統計テスト用データを作成"""
    engine = create_async_engine(settings.database_url.replace('postgresql://', 'postgresql+asyncpg://'))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # JSTタイムゾーン取得
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.now(jst)
        month_start_jst = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # UTCに変換
        month_start_utc = month_start_jst.astimezone(pytz.UTC)
        
        # テストユーザーと施設のマッピング（test32, test42, test52, test62, test72）
        test_users = {
            'test32@example.com': {
                'plan': 'Free',
                'test_cases': [
                    {'name': 'Freeプラン（30件以内）', 'question_count': 15, 'ai_responses': 10, 'escalations': 2}
                ]
            },
            'test42@example.com': {
                'plan': 'Mini',
                'test_cases': [
                    {'name': 'Miniプラン', 'question_count': 50, 'ai_responses': 40, 'escalations': 5}
                ]
            },
            'test52@example.com': {
                'plan': 'Small',
                'test_cases': [
                    {'name': 'Smallプラン（上限内）', 'question_count': 100, 'ai_responses': 80, 'escalations': 10}
                ]
            },
            'test62@example.com': {
                'plan': 'Standard',
                'test_cases': [
                    {'name': 'Standardプラン', 'question_count': 300, 'ai_responses': 250, 'escalations': 15}
                ]
            },
            'test72@example.com': {
                'plan': 'Premium',
                'test_cases': [
                    {'name': 'Premiumプラン', 'question_count': 600, 'ai_responses': 550, 'escalations': 10}
                ]
            }
        }
        
        print("=" * 80)
        print("ステージング環境：月次ダッシュボード統計テスト用データ作成")
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
                select(Facility).where(Facility.id == user.facility_id)
            )
            facility = facility_result.scalar_one_or_none()
            
            if not facility:
                print(f"  ❌ 施設が見つかりません: Facility ID {user.facility_id}")
                continue
            
            print(f"  ✅ 施設: {facility.name} (ID: {facility.id}, Plan: {facility.plan_type})")
            
            # 既存の今月のデータを削除
            existing_conv_result = await session.execute(
                select(Conversation.id)
                .where(Conversation.facility_id == facility.id)
                .where(Conversation.started_at >= month_start_utc)
            )
            existing_conv_ids = [row[0] for row in existing_conv_result.all()]
            if existing_conv_ids:
                await session.execute(delete(Message).where(Message.conversation_id.in_(existing_conv_ids)))
                await session.execute(delete(Escalation).where(Escalation.conversation_id.in_(existing_conv_ids)))
                await session.execute(delete(Conversation).where(Conversation.id.in_(existing_conv_ids)))
                await session.commit()
                print(f"  ✅ 既存データを削除しました: {len(existing_conv_ids)}件の会話")
            
            # テストケースごとにデータを作成
            for test_case in config['test_cases']:
                print(f"\n  📝 {test_case['name']}を作成中...")
                print(f"     質問数: {test_case['question_count']}件")
                print(f"     AI自動応答数: {test_case['ai_responses']}件")
                print(f"     エスカレーション数: {test_case['escalations']}件")
                
                # 会話とメッセージを作成
                escalated_conversation_ids = []
                
                for i in range(test_case['question_count']):
                    # 会話を作成
                    conversation = Conversation(
                        facility_id=facility.id,
                        session_id=f"test-session-{facility.id}-{i}-{uuid.uuid4().hex[:8]}",
                        started_at=month_start_utc + timedelta(hours=i),
                        language="ja"
                    )
                    session.add(conversation)
                    await session.flush()
                    
                    # ユーザーメッセージ（質問）
                    user_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.USER.value,
                        content=f"テスト質問 {i+1}",
                        created_at=month_start_utc + timedelta(hours=i, minutes=1),
                        language="ja"
                    )
                    session.add(user_message)
                    await session.flush()
                    
                    # AI自動応答（質問数の80%程度）
                    if i < test_case['ai_responses']:
                        ai_message = Message(
                            conversation_id=conversation.id,
                            role=MessageRole.ASSISTANT.value,
                            content=f"テスト回答 {i+1}",
                            created_at=month_start_utc + timedelta(hours=i, minutes=2),
                            language="ja"
                        )
                        session.add(ai_message)
                    
                    # エスカレーション（最初のN件）
                    if i < test_case['escalations']:
                        escalated_conversation_ids.append(conversation.id)
                        escalation = Escalation(
                            facility_id=facility.id,
                            conversation_id=conversation.id,
                            guest_message=f"テスト質問 {i+1}",
                            trigger_type="low_confidence",
                            ai_confidence=0.5,
                            created_at=month_start_utc + timedelta(hours=i, minutes=3),
                            resolved_at=None,
                            language="ja"
                        )
                        session.add(escalation)
                
                await session.commit()
                print(f"  ✅ {test_case['name']}のデータを作成しました")
                print(f"     会話数: {test_case['question_count']}件")
                print(f"     エスカレーション数: {len(escalated_conversation_ids)}件")
        
        print("\n" + "=" * 80)
        print("✅ すべてのテストデータの作成が完了しました")
        print("=" * 80)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_staging_monthly_dashboard_test_data())

