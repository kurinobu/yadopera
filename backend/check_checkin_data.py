"""
ステージング環境の「check-in」関連データを確認するスクリプト
データベースを直接確認して「check-in」関連データを特定
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from sqlalchemy.orm import joinedload
from app.core.config import settings

# すべてのモデルをインポート
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.faq import FAQ
from app.models.faq_suggestion import FAQSuggestion
from app.models.escalation import Escalation

FORBIDDEN_PATTERNS = [
    "check-in",
    "チェックイン",
    "checkin",
    "Check-in",
    "Check-In",
    "CHECK-IN"
]

async def check_checkin_data():
    """ステージング環境の「check-in」関連データを確認"""
    
    # 環境変数からデータベースURLを取得
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    
    if not database_url:
        print("❌ エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    # データベースURLを非同期用に変換
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        if "postgresql" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)
    
    print(f"📊 データベース接続: {database_url.split('@')[1] if '@' in database_url else '***'}")
    
    # データベース接続
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # テスト施設を取得
            result = await session.execute(
                select(Facility).where(Facility.slug == "test-facility")
            )
            test_facility = result.scalar_one_or_none()
            
            if not test_facility:
                print("❌ エラー: テスト施設が見つかりません")
                sys.exit(1)
            
            print(f"✅ テスト施設を確認: ID={test_facility.id}, slug={test_facility.slug}\n")
            
            # 1. メッセージの確認
            print("=" * 80)
            print("1. メッセージの確認")
            print("=" * 80)
            
            for pattern in FORBIDDEN_PATTERNS:
                messages_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id.in_(
                            select(Conversation.id).where(Conversation.facility_id == test_facility.id)
                        ),
                        Message.content.ilike(f"%{pattern}%")
                    )
                )
                messages = messages_result.scalars().all()
                
                if messages:
                    print(f"\n  🔍 パターン「{pattern}」で検索: {len(messages)}件見つかりました")
                    for msg in messages:
                        print(f"    - Message ID: {msg.id}, Conversation ID: {msg.conversation_id}")
                        print(f"      Role: {msg.role}, Content: \"{msg.content[:100]}...\"")
                        print(f"      Created: {msg.created_at}")
                else:
                    print(f"  ✅ パターン「{pattern}」: 見つかりませんでした")
            
            # 2. FAQ提案の確認
            print("\n" + "=" * 80)
            print("2. FAQ提案の確認")
            print("=" * 80)
            
            for pattern in FORBIDDEN_PATTERNS:
                suggestions_result = await session.execute(
                    select(FAQSuggestion).where(
                        FAQSuggestion.facility_id == test_facility.id,
                        FAQSuggestion.suggested_question.ilike(f"%{pattern}%")
                    )
                )
                suggestions = suggestions_result.scalars().all()
                
                if suggestions:
                    print(f"\n  🔍 パターン「{pattern}」で検索: {len(suggestions)}件見つかりました")
                    for suggestion in suggestions:
                        print(f"    - FAQSuggestion ID: {suggestion.id}")
                        print(f"      Question: \"{suggestion.suggested_question[:100]}...\"")
                        print(f"      Status: {suggestion.status}, Created: {suggestion.created_at}")
                else:
                    print(f"  ✅ パターン「{pattern}」: 見つかりませんでした")
            
            # 3. FAQの確認
            print("\n" + "=" * 80)
            print("3. FAQの確認")
            print("=" * 80)
            
            for pattern in FORBIDDEN_PATTERNS:
                faqs_result = await session.execute(
                    select(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQ.question.ilike(f"%{pattern}%")
                    )
                )
                faqs = faqs_result.scalars().all()
                
                if faqs:
                    print(f"\n  🔍 パターン「{pattern}」で検索: {len(faqs)}件見つかりました")
                    for faq in faqs:
                        print(f"    - FAQ ID: {faq.id}")
                        print(f"      Question: \"{faq.question[:100]}...\"")
                        print(f"      Category: {faq.category}, Is Active: {faq.is_active}")
                        print(f"      Created: {faq.created_at}")
                else:
                    print(f"  ✅ パターン「{pattern}」: 見つかりませんでした")
            
            # 4. エスカレーションの確認
            print("\n" + "=" * 80)
            print("4. エスカレーションの確認")
            print("=" * 80)
            
            # 未解決エスカレーションを取得
            unresolved_escalations_result = await session.execute(
                select(Escalation).where(
                    Escalation.facility_id == test_facility.id,
                    Escalation.resolved_at.is_(None)
                ).options(joinedload(Escalation.conversation))
            )
            unresolved_escalations = unresolved_escalations_result.scalars().all()
            
            checkin_escalations = []
            for escalation in unresolved_escalations:
                if not escalation.conversation:
                    continue
                
                # 会話の最初のユーザーメッセージを取得
                first_user_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == escalation.conversation.id,
                        Message.role == MessageRole.USER.value
                    ).order_by(Message.created_at.asc()).limit(1)
                )
                first_user_message = first_user_message_result.scalar_one_or_none()
                
                if first_user_message:
                    message_content_lower = first_user_message.content.lower()
                    is_checkin_related = any(
                        pattern.lower() in message_content_lower 
                        for pattern in FORBIDDEN_PATTERNS
                    )
                    
                    if is_checkin_related:
                        checkin_escalations.append({
                            "escalation": escalation,
                            "message": first_user_message
                        })
            
            if checkin_escalations:
                print(f"\n  🔍 「check-in」関連の未解決エスカレーション: {len(checkin_escalations)}件見つかりました")
                for item in checkin_escalations:
                    escalation = item["escalation"]
                    message = item["message"]
                    print(f"    - Escalation ID: {escalation.id}, Conversation ID: {escalation.conversation_id}")
                    print(f"      Message ID: {message.id}, Question: \"{message.content[:100]}...\"")
                    print(f"      Created: {escalation.created_at}")
            else:
                print("  ✅ 「check-in」関連の未解決エスカレーション: 見つかりませんでした")
            
            # 5. サマリー
            print("\n" + "=" * 80)
            print("5. サマリー")
            print("=" * 80)
            
            total_messages = 0
            total_suggestions = 0
            total_faqs = 0
            total_escalations = len(checkin_escalations)
            
            for pattern in FORBIDDEN_PATTERNS:
                messages_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id.in_(
                            select(Conversation.id).where(Conversation.facility_id == test_facility.id)
                        ),
                        Message.content.ilike(f"%{pattern}%")
                    )
                )
                total_messages += len(messages_result.scalars().all())
                
                suggestions_result = await session.execute(
                    select(FAQSuggestion).where(
                        FAQSuggestion.facility_id == test_facility.id,
                        FAQSuggestion.suggested_question.ilike(f"%{pattern}%")
                    )
                )
                total_suggestions += len(suggestions_result.scalars().all())
                
                faqs_result = await session.execute(
                    select(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQ.question.ilike(f"%{pattern}%")
                    )
                )
                total_faqs += len(faqs_result.scalars().all())
            
            print(f"\n  📊 合計:")
            print(f"    - メッセージ: {total_messages}件")
            print(f"    - FAQ提案: {total_suggestions}件")
            print(f"    - FAQ: {total_faqs}件")
            print(f"    - 未解決エスカレーション: {total_escalations}件")
            print(f"    - 合計: {total_messages + total_suggestions + total_faqs + total_escalations}件")
            
            if total_messages + total_suggestions + total_faqs + total_escalations > 0:
                print(f"\n  ⚠️ 「check-in」関連データが{total_messages + total_suggestions + total_faqs + total_escalations}件見つかりました")
                print(f"     削除処理が必要です")
            else:
                print(f"\n  ✅ 「check-in」関連データは見つかりませんでした")
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_checkin_data())

