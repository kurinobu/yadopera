"""
ステージング環境の「check-in」関連データを完全削除するスクリプト
データベースに直接接続して「check-in」関連データを完全削除

【重要】このスクリプトは既存のデータベースに直接接続して削除処理を実行します
実行前に必ずバックアップを取得してください
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.core.config import settings

# すべてのモデルをインポート
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.faq import FAQ
from app.models.faq_translation import FAQTranslation
from app.models.faq_suggestion import FAQSuggestion
from app.models.escalation import Escalation
from app.models.overnight_queue import OvernightQueue
from app.models.guest_feedback import GuestFeedback

FORBIDDEN_PATTERNS = [
    "check-in",
    "チェックイン",
    "checkin",
    "Check-in",
    "Check-In",
    "CHECK-IN",
    "check in",  # スペースあり（「When can I check in?」など）
    "Check In",
    "CHECK IN"
]

async def delete_checkin_data():
    """ステージング環境の「check-in」関連データを完全削除"""
    
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
    print("⚠️  警告: このスクリプトは既存のデータベースに直接接続して削除処理を実行します")
    print("   実行前に必ずバックアップを取得してください\n")
    
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
            
            # 削除カウント
            deleted_counts = {
                "messages": 0,
                "faq_suggestions": 0,
                "faqs": 0,
                "escalations": 0,
                "conversations": 0,
                "overnight_queues": 0,
                "guest_feedbacks": 0
            }
            
            # ========================================================================
            # 1. 未解決エスカレーションの削除（最初に実行：外部キー制約を考慮）
            # ========================================================================
            print("=" * 80)
            print("1. 未解決エスカレーションの削除")
            print("=" * 80)
            
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
                            "message": first_user_message,
                            "conversation": escalation.conversation
                        })
            
            # エスカレーションに関連する夜間対応キューを削除
            for item in checkin_escalations:
                escalation = item["escalation"]
                # 夜間対応キューを削除
                overnight_queues_result = await session.execute(
                    select(OvernightQueue).where(
                        OvernightQueue.escalation_id == escalation.id
                    )
                )
                overnight_queues = overnight_queues_result.scalars().all()
                for queue in overnight_queues:
                    print(f"  ❌ 夜間対応キューを削除します: id={queue.id}, escalation_id={escalation.id}")
                    await session.delete(queue)
                    deleted_counts["overnight_queues"] += 1
                
                # エスカレーションを削除
                print(f"  ❌ 未解決エスカレーションを削除します: id={escalation.id}, conversation_id={escalation.conversation_id}")
                await session.delete(escalation)
                deleted_counts["escalations"] += 1
            
            await session.flush()
            print(f"  ✅ {deleted_counts['escalations']}件の未解決エスカレーションを削除しました")
            print(f"  ✅ {deleted_counts['overnight_queues']}件の夜間対応キューを削除しました")
            
            # ========================================================================
            # 2. メッセージの削除
            # ========================================================================
            print("\n" + "=" * 80)
            print("2. メッセージの削除")
            print("=" * 80)
            
            # 全てのパターンで検索（大文字小文字を区別しない、スペース・ハイフンのバリエーションも検出）
            all_checkin_messages = []
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
                all_checkin_messages.extend(messages)
            
            # 追加パターン: 「check in」のバリエーション（正規表現的な検索）
            # 「check」と「in」が近接している場合も検出
            all_messages_result = await session.execute(
                select(Message).where(
                    Message.conversation_id.in_(
                        select(Conversation.id).where(Conversation.facility_id == test_facility.id)
                    ),
                    Message.content.ilike("%check%in%")
                )
            )
            additional_messages = all_messages_result.scalars().all()
            # 既に検出されたメッセージを除外
            existing_ids = {msg.id for msg in all_checkin_messages}
            for msg in additional_messages:
                if msg.id not in existing_ids:
                    # 「check」と「in」が近接しているか確認（「check-in」「check in」など）
                    content_lower = msg.content.lower()
                    if "check" in content_lower and "in" in content_lower:
                        # 「checkout」「checking」などは除外
                        if "checkout" not in content_lower and "checking" not in content_lower:
                            all_checkin_messages.append(msg)
            
            # 重複を除去
            unique_messages = {msg.id: msg for msg in all_checkin_messages}.values()
            
            for msg in unique_messages:
                print(f"  ❌ メッセージを削除します: id={msg.id}, conversation_id={msg.conversation_id}, content=\"{msg.content[:50]}...\"")
                await session.delete(msg)
                deleted_counts["messages"] += 1
            
            await session.flush()
            print(f"  ✅ {deleted_counts['messages']}件のメッセージを削除しました")
            
            # ========================================================================
            # 3. ゲストフィードバックの削除（削除されたメッセージに関連するフィードバック）
            # ========================================================================
            print("\n" + "=" * 80)
            print("3. ゲストフィードバックの削除")
            print("=" * 80)
            
            # 削除されたメッセージIDのリストを取得
            deleted_message_ids = [msg.id for msg in unique_messages]
            
            if deleted_message_ids:
                feedbacks_result = await session.execute(
                    select(GuestFeedback).where(
                        GuestFeedback.message_id.in_(deleted_message_ids)
                    )
                )
                feedbacks = feedbacks_result.scalars().all()
                
                for feedback in feedbacks:
                    print(f"  ❌ ゲストフィードバックを削除します: id={feedback.id}, message_id={feedback.message_id}")
                    await session.delete(feedback)
                    deleted_counts["guest_feedbacks"] += 1
                
                await session.flush()
                print(f"  ✅ {deleted_counts['guest_feedbacks']}件のゲストフィードバックを削除しました")
            
            # ========================================================================
            # 4. メッセージが全て削除された会話の削除
            # ========================================================================
            print("\n" + "=" * 80)
            print("4. 空の会話の削除")
            print("=" * 80)
            
            # check-in関連のメッセージを含む会話IDを取得
            checkin_conversation_ids = set()
            for pattern in FORBIDDEN_PATTERNS:
                conversation_ids_result = await session.execute(
                    select(Message.conversation_id).where(
                        Message.conversation_id.in_(
                            select(Conversation.id).where(Conversation.facility_id == test_facility.id)
                        ),
                        Message.content.ilike(f"%{pattern}%")
                    ).distinct()
                )
                checkin_conversation_ids.update(conversation_ids_result.scalars().all())
            
            # メッセージが残っているか確認
            for conversation_id in checkin_conversation_ids:
                remaining_messages_result = await session.execute(
                    select(Message).where(Message.conversation_id == conversation_id).limit(1)
                )
                remaining_message = remaining_messages_result.scalar_one_or_none()
                
                if not remaining_message:
                    # メッセージが残っていない場合は会話も削除
                    conversation_result = await session.execute(
                        select(Conversation).where(Conversation.id == conversation_id)
                    )
                    conversation = conversation_result.scalar_one_or_none()
                    if conversation:
                        print(f"  ❌ 空の会話を削除します: id={conversation.id}, session_id={conversation.session_id}")
                        await session.delete(conversation)
                        deleted_counts["conversations"] += 1
            
            await session.flush()
            print(f"  ✅ {deleted_counts['conversations']}件の空の会話を削除しました")
            
            # ========================================================================
            # 5. FAQ提案の削除
            # ========================================================================
            print("\n" + "=" * 80)
            print("5. FAQ提案の削除")
            print("=" * 80)
            
            # 全てのパターンで検索
            all_checkin_suggestions = []
            for pattern in FORBIDDEN_PATTERNS:
                suggestions_result = await session.execute(
                    select(FAQSuggestion).where(
                        FAQSuggestion.facility_id == test_facility.id,
                        FAQSuggestion.suggested_question.ilike(f"%{pattern}%")
                    )
                )
                suggestions = suggestions_result.scalars().all()
                all_checkin_suggestions.extend(suggestions)
            
            # 重複を除去
            unique_suggestions = {s.id: s for s in all_checkin_suggestions}.values()
            
            for suggestion in unique_suggestions:
                print(f"  ❌ FAQ提案を削除します: id={suggestion.id}, question=\"{suggestion.suggested_question[:50]}...\"")
                await session.delete(suggestion)
                deleted_counts["faq_suggestions"] += 1
            
            await session.flush()
            print(f"  ✅ {deleted_counts['faq_suggestions']}件のFAQ提案を削除しました")
            
            # ========================================================================
            # 6. FAQの削除（インテントベース構造対応）
            # ========================================================================
            print("\n" + "=" * 80)
            print("6. FAQの削除")
            print("=" * 80)
            
            # 全てのパターンで検索（インテントベース構造対応: FAQTranslationから検索）
            all_checkin_faqs = []
            for pattern in FORBIDDEN_PATTERNS:
                # FAQTranslationから検索して、関連するFAQを取得
                translations_result = await session.execute(
                    select(FAQTranslation).join(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQTranslation.question.ilike(f"%{pattern}%")
                    )
                )
                translations = translations_result.scalars().all()
                # FAQ IDを取得
                faq_ids = {trans.faq_id for trans in translations}
                # FAQを取得
                if faq_ids:
                    faqs_result = await session.execute(
                        select(FAQ).where(FAQ.id.in_(faq_ids))
                    )
                    faqs = faqs_result.scalars().all()
                    all_checkin_faqs.extend(faqs)
            
            # 重複を除去
            unique_faqs = {f.id: f for f in all_checkin_faqs}.values()
            
            for faq in unique_faqs:
                # FAQTranslationを取得（ログ用）
                translation_result = await session.execute(
                    select(FAQTranslation).where(
                        FAQTranslation.faq_id == faq.id
                    ).limit(1)
                )
                translation = translation_result.scalar_one_or_none()
                question_text = translation.question[:50] if translation else f"FAQ ID: {faq.id}"
                print(f"  ❌ FAQを削除します: id={faq.id}, question=\"{question_text}...\"")
                await session.delete(faq)
                deleted_counts["faqs"] += 1
            
            await session.flush()
            print(f"  ✅ {deleted_counts['faqs']}件のFAQを削除しました")
            
            # ========================================================================
            # 7. コミット
            # ========================================================================
            await session.commit()
            
            # ========================================================================
            # 8. サマリー
            # ========================================================================
            print("\n" + "=" * 80)
            print("削除処理完了サマリー")
            print("=" * 80)
            print(f"  - メッセージ: {deleted_counts['messages']}件")
            print(f"  - FAQ提案: {deleted_counts['faq_suggestions']}件")
            print(f"  - FAQ: {deleted_counts['faqs']}件")
            print(f"  - エスカレーション: {deleted_counts['escalations']}件")
            print(f"  - 会話: {deleted_counts['conversations']}件")
            print(f"  - 夜間対応キュー: {deleted_counts['overnight_queues']}件")
            print(f"  - ゲストフィードバック: {deleted_counts['guest_feedbacks']}件")
            total = sum(deleted_counts.values())
            print(f"  - 合計: {total}件")
            
            if total > 0:
                print(f"\n  ✅ 「check-in」関連データを{total}件削除しました")
            else:
                print(f"\n  ✅ 「check-in」関連データは見つかりませんでした")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(delete_checkin_data())

