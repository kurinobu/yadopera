"""
ステージング環境用テストデータ作成スクリプト
ステージング環境のデータベースに完全なテストデータを作成
（未解決質問、会話、メッセージ、FAQ、エスカレーション、夜間キューなど）

【⚠️⚠️⚠️ 重大警告：絶対に違反してはいけない禁止事項 ⚠️⚠️⚠️】
- 「check-in」「チェックイン」関連の質問をテストデータとして使用することは絶対に禁止
- 理由1：このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない
- 理由2：ゲストがチェックイン時間を聞くことは例外時以外は聞かない
- 理由3：施設管理者からすると開発者は宿泊業について無知だと思われ、ユーザー体験を低下する
- ゲストや管理者が実際に使用することは問題ないが、開発者がテストデータとして使用することは絶対に禁止
- この禁止事項を違反すると、開発者の信頼性が失われ、プロジェクト全体の品質が疑われる

【再発防止策】
1. 全てのテストデータ作成前に必ずvalidate_test_data_question()を実行
2. 全てのテストデータ作成前に必ずvalidate_all_test_data()を実行
3. データベースへの保存前に再度検証
4. 既存データの削除処理で「check in」（スペースあり）も検出
"""

import asyncio
import sys
import os
from datetime import time, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.security import hash_password
from app.core.config import settings

# すべてのモデルをインポート（リレーションシップ解決のため）
from app.models.facility import Facility
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.session_token import SessionToken  # noqa: F401
from app.models.faq import FAQ  # noqa: F401
from app.models.faq_suggestion import FAQSuggestion  # noqa: F401
from app.models.escalation import Escalation
from app.models.escalation_schedule import EscalationSchedule  # noqa: F401
from app.models.overnight_queue import OvernightQueue
from app.models.question_pattern import QuestionPattern  # noqa: F401
from app.models.guest_feedback import GuestFeedback  # noqa: F401
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import pytz

# ============================================================================
# 【再発防止策1】禁止用語チェック関数
# ============================================================================

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

def validate_test_data_question(question: str, context: str = "") -> None:
    """
    テストデータの質問文に禁止用語が含まれていないか検証
    
    【⚠️⚠️⚠️ 重大警告 ⚠️⚠️⚠️】
    この関数は絶対にスキップしてはいけません。
    禁止用語が含まれているテストデータを作成すると：
    - 施設管理者から開発者が宿泊業について無知だと思われる
    - ユーザー体験が低下する
    - プロジェクト全体の信頼性が失われる
    
    Args:
        question: 検証する質問文
        context: エラーメッセージ用のコンテキスト情報
    
    Raises:
        ValueError: 禁止用語が含まれている場合
    """
    question_lower = question.lower()
    
    # パターン1: 直接的な禁止パターンの検出
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in question_lower:
            error_msg = (
                f"❌❌❌ 重大エラー: 禁止用語「{pattern}」がテストデータに含まれています！❌❌❌\n"
                f"   質問文: \"{question}\"\n"
                f"   コンテキスト: {context}\n"
                f"\n"
                f"【⚠️⚠️⚠️ 絶対に違反してはいけない禁止事項 ⚠️⚠️⚠️】\n"
                f"理由1: このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない\n"
                f"理由2: ゲストがチェックイン時間を聞くことは例外時以外は聞かない\n"
                f"理由3: 施設管理者からすると開発者は宿泊業について無知だと思われ、ユーザー体験を低下する\n"
                f"\n"
                f"適切な質問例:\n"
                f"  - \"What time is check-out?\"\n"
                f"  - \"Where is the WiFi password?\"\n"
                f"  - \"Where is the nearest convenience store?\"\n"
            )
            raise ValueError(error_msg)
    
    # パターン2: 「check」と「in」が近接している場合の検出（「When can I check in?」など）
    if "check" in question_lower and "in" in question_lower:
        # 「checkout」「checking」などは除外
        if "checkout" not in question_lower and "checking" not in question_lower:
            # 「check」と「in」の間に単語が1-2個程度しかない場合を検出
            import re
            # 「check」の後に「in」が近接しているパターンを検出
            check_in_pattern = re.search(r'check\s+\w{0,10}\s+in', question_lower)
            if check_in_pattern:
                error_msg = (
                    f"❌❌❌ 重大エラー: 「check in」関連の表現がテストデータに含まれています！❌❌❌\n"
                    f"   質問文: \"{question}\"\n"
                    f"   検出パターン: \"{check_in_pattern.group()}\"\n"
                    f"   コンテキスト: {context}\n"
                    f"\n"
                    f"【⚠️⚠️⚠️ 絶対に違反してはいけない禁止事項 ⚠️⚠️⚠️】\n"
                    f"理由1: このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない\n"
                    f"理由2: ゲストがチェックイン時間を聞くことは例外時以外は聞かない\n"
                    f"理由3: 施設管理者からすると開発者は宿泊業について無知だと思われ、ユーザー体験を低下する\n"
                f"\n"
                f"適切な質問例:\n"
                f"  - \"What time is check-out?\"\n"
                f"  - \"Where is the WiFi password?\"\n"
                f"  - \"Where is the nearest convenience store?\"\n"
            )
            raise ValueError(error_msg)

def validate_test_data_answer(answer: str, context: str = "") -> None:
    """
    テストデータの回答文に禁止用語が含まれていないか検証
    
    Args:
        answer: 検証する回答文
        context: エラーメッセージ用のコンテキスト情報
    
    Raises:
        ValueError: 禁止用語が含まれている場合
    """
    answer_lower = answer.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in answer_lower:
            # 回答文の場合は、禁止用語が含まれていてもエラーにはしない
            # （施設情報として「Check-in: 15:00」のような表示は問題ない）
            # ただし、警告は出す
            print(f"  ⚠️ 警告: 回答文に「{pattern}」が含まれています: \"{answer[:50]}...\"")
            print(f"     （施設情報としての表示は問題ありませんが、注意してください）")

def validate_test_data_dict(data: dict, data_type: str = "テストデータ") -> None:
    """
    テストデータ辞書に禁止用語が含まれていないか検証
    
    Args:
        data: 検証するデータ辞書
        data_type: データタイプ（エラーメッセージ用）
    
    Raises:
        ValueError: 禁止用語が含まれている場合
    """
    if "question" in data:
        validate_test_data_question(data["question"], f"{data_type} (question)")
    if "answer" in data:
        validate_test_data_answer(data["answer"], f"{data_type} (answer)")
    if "content" in data:
        validate_test_data_question(data["content"], f"{data_type} (content)")

def validate_all_test_data(test_data_list: list, data_type: str = "テストデータ") -> None:
    """
    テストデータリスト全体を検証
    
    Args:
        test_data_list: 検証するテストデータリスト
        data_type: データタイプ（エラーメッセージ用）
    
    Raises:
        ValueError: 禁止用語が含まれている場合
    """
    for i, data in enumerate(test_data_list, 1):
        try:
            validate_test_data_dict(data, f"{data_type} [{i}]")
        except ValueError as e:
            print(f"\n{'='*80}")
            print(f"【検証エラー】")
            print(f"{'='*80}")
            print(str(e))
            print(f"{'='*80}\n")
            raise

async def create_staging_test_data():
    """
    ステージング環境のテストデータを作成
    
    【⚠️⚠️⚠️ 重大警告：絶対に違反してはいけない禁止事項 ⚠️⚠️⚠️】
    - 「check-in」「チェックイン」関連の質問をテストデータとして使用することは絶対に禁止
    - 理由1: このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない
    - 理由2: ゲストがチェックイン時間を聞くことは例外時以外は聞かない
    - 理由3: 施設管理者からすると開発者は宿泊業について無知だと思われ、ユーザー体験を低下する
    - この禁止事項を違反すると、開発者の信頼性が失われ、プロジェクト全体の品質が疑われる
    """
    
    # 環境変数からデータベースURLを取得
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    
    if not database_url:
        print("❌ エラー: DATABASE_URLが設定されていません")
        print("ステージング環境のデータベース接続情報を設定してください")
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
            # 既存のテスト施設を取得または作成
            result = await session.execute(
                select(Facility).where(Facility.slug == "test-facility")
            )
            test_facility = result.scalar_one_or_none()
            
            if test_facility:
                print(f"✅ 既存のテスト施設を使用します: ID={test_facility.id}, slug={test_facility.slug}")
            else:
                # テスト施設を作成
                from datetime import time
                test_facility = Facility(
                    name="Test Facility",
                    slug="test-facility",
                    email="test@example.com",
                    phone="090-1234-5678",
                    address="Test Address, Test City",
                    wifi_ssid="TestWiFi",
                    wifi_password="testpassword123",
                    check_in_time=time(15, 0),
                    check_out_time=time(11, 0),
                    house_rules="禁煙（中庭の喫煙エリアのみ可）、門限23:00、静粛時間22:00-8:00、キッチン使用可能時間~21:00",
                    local_info="最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）、レストラン: 多数あり",
                    languages=["en", "ja"],
                    timezone="Asia/Tokyo",
                    subscription_plan="small",
                    monthly_question_limit=200,
                    staff_absence_periods=[{"start_time": "22:00", "end_time": "08:00", "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}],
                    icon_url=None,
                    is_active=True
                )
                
                session.add(test_facility)
                await session.flush()
                await session.commit()
                
                print(f"✅ テスト施設を作成しました: ID={test_facility.id}, slug={test_facility.slug}")
            
            # 既存のテストユーザーを確認
            user_result = await session.execute(
                select(User).where(User.email == "test@example.com", User.facility_id == test_facility.id)
            )
            test_user = user_result.scalar_one_or_none()
            
            if test_user:
                # 既存のユーザーのパスワードをリセット
                print(f"⚠️ 既存のテストユーザーが見つかりました: ID={test_user.id}, email={test_user.email}")
                print("パスワードをリセットします...")
                
                try:
                    password_hash = hash_password("testpassword123")
                except Exception as e:
                    print(f"⚠️ パスワードハッシュ生成でエラーが発生しました: {e}")
                    import bcrypt
                    password_hash = bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                test_user.password_hash = password_hash
                test_user.is_active = True
                await session.commit()
                
                print(f"✅ テストユーザーのパスワードをリセットしました: ID={test_user.id}, email={test_user.email}")
            else:
                # テストユーザーを作成
                print("テストユーザーを作成します...")
                
                try:
                    password_hash = hash_password("testpassword123")
                except Exception as e:
                    print(f"⚠️ パスワードハッシュ生成でエラーが発生しました: {e}")
                    import bcrypt
                    password_hash = bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                test_user = User(
                    facility_id=test_facility.id,
                    email="test@example.com",
                    password_hash=password_hash,
                    full_name="Test User",
                    role="staff",
                    is_active=True
                )
                
                session.add(test_user)
                await session.flush()
                await session.commit()
                
                print(f"✅ テストユーザーを作成しました: ID={test_user.id}, email={test_user.email}")
            
            # 【重要】既存の「check-in」関連データを完全削除
            # delete_checkin_data.pyの削除処理を参考に、外部キー制約を考慮した削除順序で実装
            print("\n🗑️ 既存の「check-in」関連データを完全削除中...")
            
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
            # 2. メッセージの削除（全てのパターンで検索し、重複を除去）
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
            # 5. FAQ提案の削除（全てのパターンで検索し、重複を除去）
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
            # 6. FAQの削除（全てのパターンで検索し、重複を除去）
            # ========================================================================
            print("\n" + "=" * 80)
            print("6. FAQの削除")
            print("=" * 80)
            
            # 全てのパターンで検索
            all_checkin_faqs = []
            for pattern in FORBIDDEN_PATTERNS:
                faqs_result = await session.execute(
                    select(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQ.question.ilike(f"%{pattern}%")
                    )
                )
                faqs = faqs_result.scalars().all()
                all_checkin_faqs.extend(faqs)
            
            # 重複を除去
            unique_faqs = {f.id: f for f in all_checkin_faqs}.values()
            
            for faq in unique_faqs:
                print(f"  ❌ FAQを削除します: id={faq.id}, question=\"{faq.question[:50]}...\"")
                await session.delete(faq)
                deleted_counts["faqs"] += 1
            
                await session.flush()
            print(f"  ✅ {deleted_counts['faqs']}件のFAQを削除しました")
            
            # ========================================================================
            # 7. サマリー
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
            
            await session.flush()
            print("  ✅ 既存の「check-in」関連データの削除が完了しました")
            
            # 未解決質問のテストデータを作成（5件）
            print("\n📝 未解決質問のテストデータを作成中...")
            unresolved_questions_data = [
                {
                    "session_id": "staging-session-unresolved-1",
                    "question": "What time is check-out?",
                    "language": "en",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.5"),
                    "days_ago": 1
                },
                {
                    "session_id": "staging-session-unresolved-2",
                    "question": "Where is the nearest convenience store?",
                    "language": "en",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.4"),
                    "days_ago": 2
                },
                {
                    "session_id": "staging-session-unresolved-3",
                    "question": "チェックアウトの時間は何時ですか？",
                    "language": "ja",
                    "trigger_type": "keyword",
                    "ai_confidence": Decimal("0.6"),
                    "days_ago": 3
                },
                {
                    "session_id": "staging-session-unresolved-4",
                    "question": "Where can I find the WiFi password?",
                    "language": "en",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.45"),
                    "days_ago": 4
                },
                {
                    "session_id": "staging-session-unresolved-5",
                    "question": "レストランはありますか？",
                    "language": "ja",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.55"),
                    "days_ago": 5
                }
            ]
            
            # 【再発防止策2】テストデータ作成前に必ず検証
            print("  🔍 テストデータの検証中...")
            validate_all_test_data(unresolved_questions_data, "未解決質問")
            print("  ✅ 検証完了: 禁止用語は含まれていません")
            
            for i, data in enumerate(unresolved_questions_data, 1):
                # 既存の会話を確認
                conversation_result = await session.execute(
                    select(Conversation).where(Conversation.session_id == data["session_id"])
                )
                existing_conversation = conversation_result.scalar_one_or_none()
                
                if existing_conversation:
                    print(f"  ⚠️ 未解決質問 {i} は既に存在します: session_id={data['session_id']}, conversation_id={existing_conversation.id}")
                    # 既存のエスカレーションを確認
                    escalation_result = await session.execute(
                        select(Escalation).where(
                            Escalation.conversation_id == existing_conversation.id,
                            Escalation.resolved_at.is_(None)
                        )
                    )
                    existing_escalation = escalation_result.scalar_one_or_none()
                    if existing_escalation:
                        print(f"    ✅ 未解決のエスカレーションも存在します: escalation_id={existing_escalation.id}")
                    else:
                        print(f"    ⚠️ 未解決のエスカレーションが存在しません。作成します...")
                        # 既存の会話にユーザーメッセージが存在するか確認
                        message_result = await session.execute(
                            select(Message).where(
                                Message.conversation_id == existing_conversation.id,
                                Message.role == MessageRole.USER.value
                            ).limit(1)
                        )
                        existing_user_message = message_result.scalar_one_or_none()
                        
                        if not existing_user_message:
                            # 【再発防止策3】メッセージ作成前に再度検証
                            validate_test_data_question(data["question"], f"未解決質問メッセージ作成時（既存会話） (session_id={data['session_id']})")
                            
                            # ユーザーメッセージを作成
                            user_message = Message(
                                conversation_id=existing_conversation.id,
                                role=MessageRole.USER.value,
                                content=data["question"],
                                created_at=datetime.utcnow() - timedelta(days=data["days_ago"])
                            )
                            session.add(user_message)
                            await session.flush()
                            print(f"    ✅ ユーザーメッセージを作成しました: message_id={user_message.id}")
                        
                        # 既存の会話に未解決のエスカレーションを作成
                        escalation = Escalation(
                            facility_id=test_facility.id,
                            conversation_id=existing_conversation.id,
                            trigger_type=data["trigger_type"],
                            ai_confidence=data["ai_confidence"],
                            escalation_mode="normal",
                            notification_channels=["email"],
                            resolved_at=None  # 未解決
                        )
                        session.add(escalation)
                        await session.flush()
                        print(f"    ✅ 未解決のエスカレーションを作成しました: escalation_id={escalation.id}")
                    continue
                
                # 会話を作成
                conversation = Conversation(
                    facility_id=test_facility.id,
                    session_id=data["session_id"],
                    guest_language=data["language"],
                    location="entrance",
                    started_at=datetime.utcnow() - timedelta(days=data["days_ago"]),
                    last_activity_at=datetime.utcnow() - timedelta(hours=data["days_ago"] * 2),
                    is_escalated=True,
                    total_messages=2
                )
                session.add(conversation)
                await session.flush()
                
                # 【再発防止策3】メッセージ作成前に再度検証
                validate_test_data_question(data["question"], f"未解決質問メッセージ作成時 (session_id={data['session_id']})")
                
                # ユーザーメッセージを作成
                user_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.USER.value,
                    content=data["question"],
                    created_at=datetime.utcnow() - timedelta(days=data["days_ago"])
                )
                session.add(user_message)
                await session.flush()
                
                # アシスタントメッセージを作成（低信頼度の回答）
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT.value,
                    content="I'm sorry, I couldn't find a clear answer to your question. Please contact our staff for assistance.",
                    ai_confidence=data["ai_confidence"],
                    created_at=datetime.utcnow() - timedelta(days=data["days_ago"]) + timedelta(minutes=1)
                )
                session.add(assistant_message)
                await session.flush()
                
                # 未解決のエスカレーションを作成
                escalation = Escalation(
                    facility_id=test_facility.id,
                    conversation_id=conversation.id,
                    trigger_type=data["trigger_type"],
                    ai_confidence=data["ai_confidence"],
                    escalation_mode="normal",
                    notification_channels=["email"],
                    resolved_at=None  # 未解決
                )
                session.add(escalation)
                await session.flush()
                
                print(f"  ✅ 未解決質問 {i} を作成しました: escalation_id={escalation.id}, message_id={user_message.id}, question=\"{data['question'][:50]}...\"")
            
            # 既存のFAQを全て削除（テストデータを完全に再作成するため）
            print("\n🗑️ 既存のFAQを削除中...")
            all_faqs_result = await session.execute(
                select(FAQ).where(FAQ.facility_id == test_facility.id)
            )
            all_faqs = all_faqs_result.scalars().all()
            for faq in all_faqs:
                print(f"  ❌ FAQを削除します: id={faq.id}, question=\"{faq.question[:50]}...\"")
                await session.delete(faq)
            await session.flush()
            
            # カテゴリ別内訳のテストデータを作成
            print("\n📊 カテゴリ別内訳のテストデータを作成中...")
            
            # FAQを4カテゴリで作成（必ず新規作成）
            faq_categories = [
                {"category": "basic", "question": "What time is check-out?", "answer": "Check-out time is 11:00 AM."},
                {"category": "facilities", "question": "Do you have WiFi?", "answer": "Yes, we have free WiFi. The password is in your room."},
                {"category": "location", "question": "Where is the nearest convenience store?", "answer": "There is a convenience store about 5 minutes walk from here."},
                {"category": "trouble", "question": "I lost my room key.", "answer": "Please contact the front desk. We will help you immediately."}
            ]
            
            # 【再発防止策2】FAQテストデータ作成前に必ず検証
            print("  🔍 FAQテストデータの検証中...")
            validate_all_test_data(faq_categories, "FAQ")
            print("  ✅ 検証完了: 禁止用語は含まれていません")
            
            created_faqs = {}
            for faq_data in faq_categories:
                faq = FAQ(
                    facility_id=test_facility.id,
                    category=faq_data["category"],
                    language="en",
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    priority=1,
                    is_active=True,
                    created_by=test_user.id
                )
                session.add(faq)
                await session.flush()
                created_faqs[faq_data["category"]] = faq
                print(f"  ✅ FAQを作成しました: category={faq_data['category']}, id={faq.id}, question=\"{faq_data['question']}\"")
            
            # カテゴリ別内訳用の会話とメッセージを作成（過去7日以内）
            category_conversations_data = [
                {
                    "session_id": "staging-session-category-basic-1",
                    "question": "What time is check-out?",
                    "language": "en",
                    "category": "basic",
                    "days_ago": 1
                },
                {
                    "session_id": "staging-session-category-basic-2",
                    "question": "What time is check-out?",
                    "language": "en",
                    "category": "basic",
                    "days_ago": 2
                },
                {
                    "session_id": "staging-session-category-facilities-1",
                    "question": "Do you have WiFi?",
                    "language": "en",
                    "category": "facilities",
                    "days_ago": 3
                },
                {
                    "session_id": "staging-session-category-location-1",
                    "question": "Where is the nearest convenience store?",
                    "language": "en",
                    "category": "location",
                    "days_ago": 4
                },
                {
                    "session_id": "staging-session-category-trouble-1",
                    "question": "I lost my room key.",
                    "language": "en",
                    "category": "trouble",
                    "days_ago": 5
                }
            ]
            
            # 【再発防止策2】カテゴリ別会話テストデータ作成前に必ず検証
            print("  🔍 カテゴリ別会話テストデータの検証中...")
            validate_all_test_data(category_conversations_data, "カテゴリ別会話")
            print("  ✅ 検証完了: 禁止用語は含まれていません")
            
            for data in category_conversations_data:
                # 既存の会話を確認
                conversation_result = await session.execute(
                    select(Conversation).where(Conversation.session_id == data["session_id"])
                )
                existing_conversation = conversation_result.scalar_one_or_none()
                
                if existing_conversation:
                    conversation = existing_conversation
                    # 【重要】既存の会話のstarted_atを強制的に過去7日間の範囲内に更新（カテゴリ別内訳用）
                    new_started_at = datetime.utcnow() - timedelta(days=data["days_ago"])
                    conversation.started_at = new_started_at
                    conversation.last_activity_at = datetime.utcnow() - timedelta(hours=data["days_ago"] * 2)
                    await session.flush()
                    print(f"  ✅ 既存の会話のstarted_atを更新しました: session_id={data['session_id']}, conversation_id={conversation.id}, started_at={new_started_at}")
                else:
                    # 会話を作成
                    conversation = Conversation(
                        facility_id=test_facility.id,
                        session_id=data["session_id"],
                        guest_language=data["language"],
                        location="entrance",
                        started_at=datetime.utcnow() - timedelta(days=data["days_ago"]),
                        last_activity_at=datetime.utcnow() - timedelta(hours=data["days_ago"] * 2),
                        is_escalated=False,
                        total_messages=2
                    )
                    session.add(conversation)
                    await session.flush()
                    print(f"  ✅ 会話を作成しました: session_id={data['session_id']}, conversation_id={conversation.id}")
                
                # ユーザーメッセージを作成（既存チェック）
                user_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == conversation.id,
                        Message.role == MessageRole.USER.value
                    ).limit(1)
                )
                existing_user_message = user_message_result.scalar_one_or_none()
                
                if not existing_user_message:
                    # 【再発防止策3】メッセージ作成前に再度検証
                    validate_test_data_question(data["question"], f"カテゴリ別会話メッセージ作成時 (session_id={data['session_id']})")
                    
                    user_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.USER.value,
                        content=data["question"],
                        created_at=datetime.utcnow() - timedelta(days=data["days_ago"])
                    )
                    session.add(user_message)
                    await session.flush()
                    print(f"    ✅ ユーザーメッセージを作成しました: message_id={user_message.id}")
                else:
                    user_message = existing_user_message
                    print(f"    ✅ ユーザーメッセージは既に存在します: message_id={user_message.id}")
                
                # AI応答メッセージを作成（matched_faq_idsを含む）
                faq = created_faqs[data["category"]]
                assistant_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == conversation.id,
                        Message.role == MessageRole.ASSISTANT.value
                    ).limit(1)
                )
                existing_assistant_message = assistant_message_result.scalar_one_or_none()
                
                if not existing_assistant_message:
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.ASSISTANT.value,
                        content=faq.answer,
                        ai_confidence=Decimal("0.9"),
                        matched_faq_ids=[faq.id],  # カテゴリ別内訳用
                        created_at=datetime.utcnow() - timedelta(days=data["days_ago"]) + timedelta(minutes=1)
                    )
                    session.add(assistant_message)
                    await session.flush()
                    print(f"    ✅ AI応答メッセージを作成しました: message_id={assistant_message.id}, matched_faq_id={faq.id}, category={data['category']}")
                else:
                    # 【重要】既存のメッセージのmatched_faq_idsを確実に設定（カテゴリ別内訳用）
                    if not existing_assistant_message.matched_faq_ids or faq.id not in (existing_assistant_message.matched_faq_ids or []):
                        existing_assistant_message.matched_faq_ids = [faq.id]  # 最初のマッチしたFAQのみ
                    # created_atも強制的に過去7日間の範囲内に更新
                    new_created_at = datetime.utcnow() - timedelta(days=data["days_ago"]) + timedelta(minutes=1)
                    existing_assistant_message.created_at = new_created_at
                    await session.flush()
                    print(
                        f"    ✅ 既存のAI応答メッセージを更新しました: "
                        f"message_id={existing_assistant_message.id}, matched_faq_id={faq.id}, "
                        f"category={data['category']}, created_at={new_created_at}"
                    )
            
            # 夜間対応キューのテストデータを作成
            print("\n🌙 夜間対応キューのテストデータを作成中...")
            
            overnight_queue_data = [
                {
                    "session_id": "staging-session-overnight-1",
                    "question": "What time is breakfast?",
                    "language": "en",
                    "days_ago": 1
                },
                {
                    "session_id": "staging-session-overnight-2",
                    "question": "朝食の時間は何時ですか？",
                    "language": "ja",
                    "days_ago": 2
                },
                {
                    "session_id": "staging-session-overnight-3",
                    "question": "Where can I leave my luggage?",
                    "language": "en",
                    "days_ago": 1
                },
                {
                    "session_id": "staging-session-overnight-4",
                    "question": "タクシーを呼べますか？",
                    "language": "ja",
                    "days_ago": 2
                },
                {
                    "session_id": "staging-session-overnight-5",
                    "question": "Is late breakfast available?",
                    "language": "en",
                    "days_ago": 3
                },
                {
                    "session_id": "staging-session-overnight-6",
                    "question": "ドライヤーはありますか？",
                    "language": "ja",
                    "days_ago": 4
                },
                {
                    "session_id": "staging-session-overnight-7",
                    "question": "Can I store food in a fridge?",
                    "language": "en",
                    "days_ago": 5
                }
            ]
            
            # 【再発防止策2】夜間対応キューテストデータ作成前に必ず検証
            print("  🔍 夜間対応キューテストデータの検証中...")
            validate_all_test_data(overnight_queue_data, "夜間対応キュー")
            print("  ✅ 検証完了: 禁止用語は含まれていません")
            
            for data in overnight_queue_data:
                # 既存の会話を確認
                conversation_result = await session.execute(
                    select(Conversation).where(Conversation.session_id == data["session_id"])
                )
                existing_conversation = conversation_result.scalar_one_or_none()
                
                if existing_conversation:
                    conversation = existing_conversation
                    print(f"  ⚠️ 会話は既に存在します: session_id={data['session_id']}, conversation_id={conversation.id}")
                else:
                    # 会話を作成
                    conversation = Conversation(
                        facility_id=test_facility.id,
                        session_id=data["session_id"],
                        guest_language=data["language"],
                        location="entrance",
                        started_at=datetime.utcnow() - timedelta(days=data["days_ago"]),
                        last_activity_at=datetime.utcnow() - timedelta(hours=data["days_ago"] * 2),
                        is_escalated=True,
                        total_messages=2
                    )
                    session.add(conversation)
                    await session.flush()
                    print(f"  ✅ 会話を作成しました: session_id={data['session_id']}, conversation_id={conversation.id}")
                
                # ユーザーメッセージを作成
                user_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == conversation.id,
                        Message.role == MessageRole.USER.value
                    ).limit(1)
                )
                existing_user_message = user_message_result.scalar_one_or_none()
                
                if not existing_user_message:
                    # 【再発防止策3】メッセージ作成前に再度検証
                    validate_test_data_question(data["question"], f"夜間対応キューメッセージ作成時 (session_id={data['session_id']})")
                    
                    user_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.USER.value,
                        content=data["question"],
                        created_at=datetime.utcnow() - timedelta(days=data["days_ago"])
                    )
                    session.add(user_message)
                    await session.flush()
                    print(f"    ✅ ユーザーメッセージを作成しました: message_id={user_message.id}")
                else:
                    user_message = existing_user_message
                    print(f"    ✅ ユーザーメッセージは既に存在します: message_id={user_message.id}")
                
                # エスカレーションを作成
                escalation_result = await session.execute(
                    select(Escalation).where(
                        Escalation.conversation_id == conversation.id,
                        Escalation.resolved_at.is_(None)
                    )
                )
                existing_escalation = escalation_result.scalar_one_or_none()
                
                if existing_escalation:
                    escalation = existing_escalation
                    print(f"    ✅ エスカレーションは既に存在します: escalation_id={escalation.id}")
                else:
                    escalation = Escalation(
                        facility_id=test_facility.id,
                        conversation_id=conversation.id,
                        trigger_type="low_confidence",
                        ai_confidence=Decimal("0.5"),
                        escalation_mode="normal",
                        notification_channels=["email"],
                        resolved_at=None
                    )
                    session.add(escalation)
                    await session.flush()
                    print(f"    ✅ エスカレーションを作成しました: escalation_id={escalation.id}")
                
                # 夜間対応キューを確認
                queue_result = await session.execute(
                    select(OvernightQueue).where(
                        OvernightQueue.escalation_id == escalation.id,
                        OvernightQueue.resolved_at.is_(None)
                    )
                )
                existing_queue = queue_result.scalar_one_or_none()
                
                if existing_queue:
                    print(f"    ✅ 夜間対応キューは既に存在します: queue_id={existing_queue.id}")
                else:
                    # 夜間対応キューを作成（翌朝8:00を計算）
                    timezone_str = test_facility.timezone or 'Asia/Tokyo'
                    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
                    facility_tz = pytz.timezone(timezone_str)
                    local_now = utc_now.astimezone(facility_tz)
                    
                    # 翌朝8:00を計算
                    if local_now.hour < 8:
                        scheduled_time_local = local_now.replace(hour=8, minute=0, second=0, microsecond=0)
                    else:
                        scheduled_time_local = (local_now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
                    
                    scheduled_time = scheduled_time_local.astimezone(pytz.UTC).replace(tzinfo=None)
                    
                    overnight_queue = OvernightQueue(
                        facility_id=test_facility.id,
                        escalation_id=escalation.id,
                        guest_message=data["question"],
                        scheduled_notify_at=scheduled_time
                    )
                    session.add(overnight_queue)
                    await session.flush()
                    print(f"    ✅ 夜間対応キューを作成しました: queue_id={overnight_queue.id}, scheduled_notify_at={scheduled_time}")
            
            # ゲストフィードバックのテストデータを作成
            print("\n💬 ゲストフィードバックのテストデータを作成中...")
            
            # 既存のメッセージを取得（フィードバック用）
            feedback_messages_result = await session.execute(
                select(Message).where(
                    Message.conversation_id.in_(
                        select(Conversation.id).where(Conversation.facility_id == test_facility.id)
                    ),
                    Message.role == MessageRole.ASSISTANT.value
                ).limit(10)
            )
            feedback_messages = feedback_messages_result.scalars().all()
            
            if feedback_messages:
                # ポジティブフィードバック（5件）
                positive_count = 0
                for i, msg in enumerate(feedback_messages[:5]):
                    # 既存のフィードバックを確認
                    existing_feedback_result = await session.execute(
                        select(GuestFeedback).where(
                            GuestFeedback.message_id == msg.id,
                            GuestFeedback.feedback_type == "positive"
                        )
                    )
                    existing_feedback = existing_feedback_result.scalar_one_or_none()
                    
                    if not existing_feedback:
                        feedback = GuestFeedback(
                            message_id=msg.id,
                            facility_id=test_facility.id,
                            feedback_type="positive",
                            created_at=datetime.utcnow() - timedelta(days=7-i)
                        )
                        session.add(feedback)
                        await session.flush()
                        positive_count += 1
                        print(f"  ✅ ポジティブフィードバックを作成しました: message_id={msg.id}, feedback_id={feedback.id}")
                    else:
                        print(f"  ⚠️ ポジティブフィードバックは既に存在します: message_id={msg.id}, feedback_id={existing_feedback.id}")
                
                # ネガティブフィードバック（3件、1回ずつ）
                negative_count = 0
                for i, msg in enumerate(feedback_messages[5:8] if len(feedback_messages) >= 8 else feedback_messages[5:]):
                    # 既存のフィードバックを確認
                    existing_feedback_result = await session.execute(
                        select(GuestFeedback).where(
                            GuestFeedback.message_id == msg.id,
                            GuestFeedback.feedback_type == "negative"
                        )
                    )
                    existing_feedbacks = existing_feedback_result.scalars().all()
                    
                    if len(existing_feedbacks) == 0:
                        feedback = GuestFeedback(
                            message_id=msg.id,
                            facility_id=test_facility.id,
                            feedback_type="negative",
                            created_at=datetime.utcnow() - timedelta(days=7-i)
                        )
                        session.add(feedback)
                        await session.flush()
                        negative_count += 1
                        print(f"  ✅ ネガティブフィードバックを作成しました: message_id={msg.id}, feedback_id={feedback.id}")
                    else:
                        print(f"  ⚠️ ネガティブフィードバックは既に存在します: message_id={msg.id}, count={len(existing_feedbacks)}")
                
                # 低評価回答（2回以上）のテストデータを作成
                print("\n👎 低評価回答（2回以上）のテストデータを作成中...")
                low_rated_count = 0
                
                # 低評価回答（2回以上）用の新しい会話とメッセージを作成（確実に作成するため）
                low_rated_questions = [
                    {
                        "session_id": "staging-session-low-rated-1",
                        "question": "Where is the laundry room?",
                        "answer": "The laundry room is on the 2nd floor.",
                        "days_ago": 5
                    },
                    {
                        "session_id": "staging-session-low-rated-2",
                        "question": "Is there a parking lot?",
                        "answer": "Sorry, we don't have a parking lot.",
                        "days_ago": 6
                    },
                    {
                        "session_id": "staging-session-low-rated-3",
                        "question": "What amenities are available?",
                        "answer": "We have a gym and a spa. Please check the front desk for details.",
                        "days_ago": 7
                    },
                    {
                        "session_id": "staging-session-low-rated-4",
                        "question": "Where is the vending machine?",
                        "answer": "The vending machine is located near the elevator on each floor.",
                        "days_ago": 8
                    },
                    {
                        "session_id": "staging-session-low-rated-5",
                        "question": "タオルはどこにありますか？",
                        "answer": "タオルは各客室のバスルームに用意されています。",
                        "days_ago": 9
                    }
                ]
                
                # 【再発防止策2】低評価回答テストデータ作成前に必ず検証
                print("  🔍 低評価回答テストデータの検証中...")
                validate_all_test_data(low_rated_questions, "低評価回答")
                print("  ✅ 検証完了: 禁止用語は含まれていません")
                
                for data in low_rated_questions:
                    # 既存の会話を確認
                    conversation_result = await session.execute(
                        select(Conversation).where(Conversation.session_id == data["session_id"])
                    )
                    existing_conversation = conversation_result.scalar_one_or_none()
                    
                    if existing_conversation:
                        conversation = existing_conversation
                        print(f"  ⚠️ 会話は既に存在します: session_id={data['session_id']}, conversation_id={conversation.id}")
                    else:
                        # 会話を作成
                        conversation = Conversation(
                            facility_id=test_facility.id,
                            session_id=data["session_id"],
                            guest_language="en",
                            location="entrance",
                            started_at=datetime.utcnow() - timedelta(days=data["days_ago"]),
                            last_activity_at=datetime.utcnow() - timedelta(hours=data["days_ago"] * 2),
                            is_escalated=False,
                            total_messages=2
                        )
                        session.add(conversation)
                        await session.flush()
                        print(f"  ✅ 会話を作成しました: session_id={data['session_id']}, conversation_id={conversation.id}")
                    
                    # ユーザーメッセージを作成
                    user_message_result = await session.execute(
                        select(Message).where(
                            Message.conversation_id == conversation.id,
                            Message.role == MessageRole.USER.value
                        ).limit(1)
                    )
                    existing_user_message = user_message_result.scalar_one_or_none()
                    
                    if not existing_user_message:
                        # 【再発防止策3】メッセージ作成前に再度検証
                        validate_test_data_question(data["question"], f"低評価回答メッセージ作成時 (session_id={data['session_id']})")
                        
                        user_message = Message(
                            conversation_id=conversation.id,
                            role=MessageRole.USER.value,
                            content=data["question"],
                            created_at=datetime.utcnow() - timedelta(days=data["days_ago"])
                        )
                        session.add(user_message)
                        await session.flush()
                        print(f"    ✅ ユーザーメッセージを作成しました: message_id={user_message.id}")
                    else:
                        user_message = existing_user_message
                        print(f"    ✅ ユーザーメッセージは既に存在します: message_id={user_message.id}")
                    
                    # AI応答メッセージを作成
                    assistant_message_result = await session.execute(
                        select(Message).where(
                            Message.conversation_id == conversation.id,
                            Message.role == MessageRole.ASSISTANT.value
                        ).limit(1)
                    )
                    existing_assistant_message = assistant_message_result.scalar_one_or_none()
                    
                    if not existing_assistant_message:
                        assistant_message = Message(
                            conversation_id=conversation.id,
                            role=MessageRole.ASSISTANT.value,
                            content=data["answer"],
                            ai_confidence=Decimal("0.6"),
                            created_at=datetime.utcnow() - timedelta(days=data["days_ago"]) + timedelta(minutes=1)
                        )
                        session.add(assistant_message)
                        await session.flush()
                        print(f"    ✅ AI応答メッセージを作成しました: message_id={assistant_message.id}")
                    else:
                        assistant_message = existing_assistant_message
                        print(f"    ✅ AI応答メッセージは既に存在します: message_id={assistant_message.id}")
                    
                    # このAI応答メッセージに対して2回のネガティブフィードバックを作成
                    existing_negative_result = await session.execute(
                        select(GuestFeedback).where(
                            GuestFeedback.message_id == assistant_message.id,
                            GuestFeedback.feedback_type == "negative"
                        )
                    )
                    existing_negative_count = len(existing_negative_result.scalars().all())
                    
                    # 2回以上になるように追加
                    needed_count = max(0, 2 - existing_negative_count)
                    for j in range(needed_count):
                        feedback = GuestFeedback(
                            message_id=assistant_message.id,
                            facility_id=test_facility.id,
                            feedback_type="negative",
                            created_at=datetime.utcnow() - timedelta(days=data["days_ago"] - j)
                        )
                        session.add(feedback)
                        await session.flush()
                        print(f"  ✅ 低評価フィードバックを追加しました: message_id={assistant_message.id}, feedback_id={feedback.id} (合計{existing_negative_count + j + 1}回)")
                        low_rated_count += 1
                
                print(f"  ✅ 低評価回答（2回以上）のテストデータ作成完了: {low_rated_count}件追加")
                
                print(f"  ✅ ゲストフィードバックのテストデータ作成完了: ポジティブ={positive_count}件, ネガティブ={negative_count}件, 低評価回答（2回以上）={low_rated_count}件追加")
            else:
                print(f"  ⚠️ フィードバック用のメッセージが見つかりませんでした。先に会話とメッセージを作成してください。")
            
            # コミット
            await session.commit()
            
            # キャッシュをクリア（FAQ、ダッシュボードのキャッシュを無効化）
            print("\n🗑️ キャッシュをクリア中...")
            try:
                from app.core.cache import delete_cache_pattern
                # FAQキャッシュをクリア
                faq_cache_count = await delete_cache_pattern(f"faq:list:*facility_id={test_facility.id}*")
                print(f"  ✅ FAQキャッシュをクリアしました: {faq_cache_count}件")
                # ダッシュボードキャッシュをクリア
                dashboard_cache_count = await delete_cache_pattern(f"dashboard:data:facility_id={test_facility.id}")
                print(f"  ✅ ダッシュボードキャッシュをクリアしました: {dashboard_cache_count}件")
            except Exception as e:
                print(f"  ⚠️ キャッシュクリアでエラーが発生しました（無視します）: {e}")
            
            print("\n✅ ステージング環境のテストデータ作成が完了しました！")
            print("\nテストユーザー情報:")
            print(f"  メールアドレス: test@example.com")
            print(f"  パスワード: testpassword123")
            print(f"  施設slug: test-facility")
            print(f"\nゲスト画面URL: https://yadopera-frontend-staging.onrender.com/f/test-facility?location=entrance")
            print(f"管理画面ログインURL: https://yadopera-frontend-staging.onrender.com/admin/login")
            print(f"\n未解決質問リスト:")
            print(f"  管理画面のFAQ管理画面で確認できます: https://yadopera-frontend-staging.onrender.com/admin/faqs")
            print(f"\nカテゴリ別内訳:")
            print(f"  管理画面のダッシュボードで確認できます: https://yadopera-frontend-staging.onrender.com/admin/dashboard")
            print(f"\n夜間対応キュー:")
            print(f"  管理画面のダッシュボードで確認できます: https://yadopera-frontend-staging.onrender.com/admin/dashboard")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_staging_test_data())

