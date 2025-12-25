"""
定期監査スクリプト: check-in関連データの検出とアラート
毎日実行され、禁止データが検出された場合はアラートを送信

使用方法:
    python audit_checkin_data.py

実行環境:
    - ローカル環境: docker exec yadopera-backend python audit_checkin_data.py
    - ステージング環境: 直接実行
    - 本番環境: 実行しない（テスト施設のみ対象）
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import select
from app.core.config import settings
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.faq_translation import FAQTranslation
from app.models.faq import FAQ
from app.models.faq_suggestion import FAQSuggestion
from app.models.escalation import Escalation

FORBIDDEN_PATTERNS = [
    "check-in", "チェックイン", "checkin",
    "Check-in", "Check-In", "CHECK-IN",
    "check in", "Check In", "CHECK IN"
]

async def audit_checkin_data():
    """check-in関連データの定期監査"""
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    if not database_url:
        print("❌ エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        if "postgresql" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)
    
    print(f"📊 データベース接続: {database_url.split('@')[1] if '@' in database_url else '***'}")
    print("🔍 check-in関連データの定期監査を開始します...\n")
    
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
                print("⚠️  警告: テスト施設が見つかりません（監査をスキップします）")
                await engine.dispose()
                return
            
            violations = []
            
            # 1. メッセージの検出
            print("=" * 80)
            print("1. メッセージの検出")
            print("=" * 80)
            all_checkin_messages = []
            for pattern in FORBIDDEN_PATTERNS:
                messages_result = await session.execute(
                    select(Message).join(Conversation).where(
                        Conversation.facility_id == test_facility.id,
                        Message.content.ilike(f"%{pattern}%")
                    )
                )
                messages = messages_result.scalars().all()
                # 「checkout」「checking」などは除外
                for msg in messages:
                    content_lower = msg.content.lower()
                    if "checkout" not in content_lower and "checking" not in content_lower:
                        all_checkin_messages.append(msg)
            
            # 重複を除去
            unique_messages = {msg.id: msg for msg in all_checkin_messages}.values()
            
            if unique_messages:
                violations.append({
                    "type": "messages",
                    "count": len(unique_messages),
                    "items": list(unique_messages)
                })
                print(f"  ❌ {len(unique_messages)}件の禁止メッセージが検出されました")
                for msg in list(unique_messages)[:5]:  # 最初の5件のみ表示
                    print(f"    - Message ID: {msg.id}, Content: \"{msg.content[:50]}...\"")
                if len(unique_messages) > 5:
                    print(f"    ... 他 {len(unique_messages) - 5}件")
            else:
                print("  ✅ 禁止メッセージは検出されませんでした")
            
            # 2. FAQ提案の検出
            print("\n" + "=" * 80)
            print("2. FAQ提案の検出")
            print("=" * 80)
            all_checkin_suggestions = []
            for pattern in FORBIDDEN_PATTERNS:
                suggestions_result = await session.execute(
                    select(FAQSuggestion).where(
                        FAQSuggestion.facility_id == test_facility.id,
                        FAQSuggestion.suggested_question.ilike(f"%{pattern}%")
                    )
                )
                suggestions = suggestions_result.scalars().all()
                for suggestion in suggestions:
                    content_lower = suggestion.suggested_question.lower()
                    if "checkout" not in content_lower and "checking" not in content_lower:
                        all_checkin_suggestions.append(suggestion)
            
            unique_suggestions = {s.id: s for s in all_checkin_suggestions}.values()
            
            if unique_suggestions:
                violations.append({
                    "type": "faq_suggestions",
                    "count": len(unique_suggestions),
                    "items": list(unique_suggestions)
                })
                print(f"  ❌ {len(unique_suggestions)}件の禁止FAQ提案が検出されました")
                for s in list(unique_suggestions)[:5]:
                    print(f"    - Suggestion ID: {s.id}, Question: \"{s.suggested_question[:50]}...\"")
                if len(unique_suggestions) > 5:
                    print(f"    ... 他 {len(unique_suggestions) - 5}件")
            else:
                print("  ✅ 禁止FAQ提案は検出されませんでした")
            
            # 3. FAQ翻訳の検出
            print("\n" + "=" * 80)
            print("3. FAQ翻訳の検出")
            print("=" * 80)
            all_checkin_translations = []
            for pattern in FORBIDDEN_PATTERNS:
                translations_result = await session.execute(
                    select(FAQTranslation).join(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQTranslation.question.ilike(f"%{pattern}%")
                    )
                )
                translations = translations_result.scalars().all()
                for trans in translations:
                    content_lower = trans.question.lower()
                    if "checkout" not in content_lower and "checking" not in content_lower:
                        all_checkin_translations.append(trans)
            
            unique_translations = {t.id: t for t in all_checkin_translations}.values()
            
            if unique_translations:
                violations.append({
                    "type": "faq_translations",
                    "count": len(unique_translations),
                    "items": list(unique_translations)
                })
                print(f"  ❌ {len(unique_translations)}件の禁止FAQ翻訳が検出されました")
                for t in list(unique_translations)[:5]:
                    print(f"    - Translation ID: {t.id}, FAQ ID: {t.faq_id}, Question: \"{t.question[:50]}...\"")
                if len(unique_translations) > 5:
                    print(f"    ... 他 {len(unique_translations) - 5}件")
            else:
                print("  ✅ 禁止FAQ翻訳は検出されませんでした")
            
            # 4. エスカレーションの検出
            print("\n" + "=" * 80)
            print("4. エスカレーションの検出")
            print("=" * 80)
            escalations_result = await session.execute(
                select(Escalation).join(Conversation).where(
                    Escalation.facility_id == test_facility.id,
                    Escalation.resolved_at.is_(None)
                ).options(joinedload(Escalation.conversation))
            )
            escalations = escalations_result.scalars().all()
            
            checkin_escalations = []
            for escalation in escalations:
                if not escalation.conversation:
                    continue
                first_user_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == escalation.conversation.id,
                        Message.role == MessageRole.USER.value
                    ).order_by(Message.created_at.asc()).limit(1)
                )
                first_user_message = first_user_message_result.scalar_one_or_none()
                if first_user_message:
                    content_lower = first_user_message.content.lower()
                    is_checkin_related = any(
                        pattern.lower() in content_lower 
                        for pattern in FORBIDDEN_PATTERNS
                    )
                    if is_checkin_related:
                        content_lower_msg = first_user_message.content.lower()
                        if "checkout" not in content_lower_msg and "checking" not in content_lower_msg:
                            checkin_escalations.append(escalation)
            
            if checkin_escalations:
                violations.append({
                    "type": "escalations",
                    "count": len(checkin_escalations),
                    "items": checkin_escalations
                })
                print(f"  ❌ {len(checkin_escalations)}件の禁止エスカレーションが検出されました")
                for e in checkin_escalations[:5]:
                    print(f"    - Escalation ID: {e.id}, Conversation ID: {e.conversation_id}")
                if len(checkin_escalations) > 5:
                    print(f"    ... 他 {len(checkin_escalations) - 5}件")
            else:
                print("  ✅ 禁止エスカレーションは検出されませんでした")
            
            # 結果の報告
            print("\n" + "=" * 80)
            print("監査結果サマリー")
            print("=" * 80)
            
            if violations:
                total_count = sum(v["count"] for v in violations)
                print(f"\n❌❌❌ 重大違反: check-in関連データが{total_count}件検出されました！❌❌❌\n")
                for violation in violations:
                    print(f"  - {violation['type']}: {violation['count']}件")
                print("\n【即座対応が必要です】")
                print("  1. delete_checkin_data.pyを実行して禁止データを削除してください")
                print("  2. 原因を特定して再発防止策を強化してください")
                print("  3. 重大指示違反記録を更新してください")
                sys.exit(1)
            else:
                print("\n✅ 監査完了: check-in関連データは検出されませんでした")
                print("  すべてのテストデータは適切です。")
        
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(audit_checkin_data())

