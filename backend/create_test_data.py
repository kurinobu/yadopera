"""
テストデータ作成スクリプト
Phase 1完了のためのテストユーザー・テストデータを作成

【重要】禁止事項：
- 「check-in」「チェックイン」関連の質問をテストデータとして使用することは絶対に禁止
- 理由：このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない
- ゲストや管理者が実際に使用することは問題ないが、開発者がテストデータとして使用することは禁止
"""

import asyncio
import sys
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
from app.models.faq_translation import FAQTranslation
from app.services.faq_service import normalize_question, generate_intent_key
from app.models.faq_suggestion import FAQSuggestion  # noqa: F401
from app.models.escalation import Escalation
from app.models.escalation_schedule import EscalationSchedule  # noqa: F401
from app.models.overnight_queue import OvernightQueue
from app.models.question_pattern import QuestionPattern  # noqa: F401
from app.models.guest_feedback import GuestFeedback  # noqa: F401
from app.models.faq import FAQ
import pytz

# ============================================================================
# 【再発防止策1】禁止用語チェック関数（create_staging_test_data.pyと同じ）
# ============================================================================

FORBIDDEN_PATTERNS = [
    "check-in",
    "チェックイン",
    "checkin",
    "Check-in",
    "Check-In",
    "CHECK-IN"
]

def validate_test_data_question(question: str, context: str = "") -> None:
    """
    テストデータの質問文に禁止用語が含まれていないか検証
    
    Args:
        question: 検証する質問文
        context: エラーメッセージ用のコンテキスト情報
    
    Raises:
        ValueError: 禁止用語が含まれている場合
    """
    question_lower = question.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in question_lower:
            error_msg = (
                f"❌ 重大エラー: 禁止用語「{pattern}」がテストデータに含まれています！\n"
                f"   質問文: \"{question}\"\n"
                f"   コンテキスト: {context}\n"
                f"\n"
                f"【重要】このアプリはチェックイン済みのゲストが使用します。\n"
                f"「check-in」関連の質問をテストデータとして使用することは絶対に禁止です。\n"
                f"ゲストや管理者が実際に使用することは問題ありませんが、\n"
                f"開発者がテストデータとして使用することは禁止です。\n"
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

async def create_test_data():
    """テストデータを作成"""
    
    # データベースURLを非同期用に変換
    # postgresql:// -> postgresql+asyncpg://
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        # 既にasyncpg形式でない場合、追加
        if "postgresql" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)
    
    # データベース接続
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 既存のテスト施設を取得または作成
            from sqlalchemy import select
            result = await session.execute(
                select(Facility).where(Facility.slug == "test-facility")
            )
            test_facility = result.scalar_one_or_none()
            
            if test_facility:
                print(f"✅ 既存のテスト施設を使用します: ID={test_facility.id}, slug={test_facility.slug}")
            else:
                # テスト施設を作成
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
                await session.flush()  # IDを取得するためにflush
                
                print(f"✅ テスト施設を作成しました: ID={test_facility.id}, slug={test_facility.slug}")
            
            # 既存のテストユーザーを取得または作成
            user_result = await session.execute(
                select(User).where(User.email == "test@example.com", User.facility_id == test_facility.id)
            )
            test_user = user_result.scalar_one_or_none()
            
            if test_user:
                print(f"✅ 既存のテストユーザーを使用します: ID={test_user.id}, email={test_user.email}")
            else:
                # パスワードハッシュを生成（エラーハンドリング付き）
                try:
                    password_hash = hash_password("testpassword123")
                except Exception as e:
                    print(f"⚠️ パスワードハッシュ生成でエラーが発生しました: {e}")
                    print("⚠️ bcryptの互換性問題の可能性があります。既存のハッシュを使用します。")
                    # 既存のテストコードから取得したハッシュを使用（一時的な回避策）
                    # 実際の環境では、この方法は使用しない
                    import bcrypt
                    password_hash = bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # テストユーザーを作成
                test_user = User(
                    facility_id=test_facility.id,
                    email="test@example.com",
                    password_hash=password_hash,
                    full_name="Test User",
                    role="staff",
                    is_active=True
                )
                
                session.add(test_user)
                await session.flush()  # IDを取得するためにflush
                
                print(f"✅ テストユーザーを作成しました: ID={test_user.id}, email={test_user.email}")
            
            # 未解決質問のテストデータを作成（3件）
            print("\n📝 未解決質問のテストデータを作成中...")
            unresolved_questions_data = [
                {
                    "session_id": "test-session-unresolved-1",
                    "question": "What time is check-out?",
                    "language": "en",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.5"),
                    "days_ago": 1
                },
                {
                    "session_id": "test-session-unresolved-2",
                    "question": "Where is the nearest convenience store?",
                    "language": "en",
                    "trigger_type": "low_confidence",
                    "ai_confidence": Decimal("0.4"),
                    "days_ago": 2
                },
                {
                    "session_id": "test-session-unresolved-3",
                    "question": "チェックアウトの時間は何時ですか？",
                    "language": "ja",
                    "trigger_type": "keyword",
                    "ai_confidence": Decimal("0.6"),
                    "days_ago": 3
                }
            ]
            
            # 【再発防止策2】テストデータ作成前に必ず検証
            print("  🔍 テストデータの検証中...")
            validate_all_test_data(unresolved_questions_data, "未解決質問")
            print("  ✅ 検証完了: 禁止用語は含まれていません")
            
            for i, data in enumerate(unresolved_questions_data, 1):
                # 既存の会話を確認
                from sqlalchemy import select
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
            
            # ステップ2: カテゴリ別内訳のテストデータを作成
            print("\n📊 カテゴリ別内訳のテストデータを作成中...")
            
            # FAQを4カテゴリで作成
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
                # 既存のFAQを確認（インテントベース構造対応）
                intent_key = generate_intent_key(faq_data["category"], faq_data["question"])
                faq_result = await session.execute(
                    select(FAQ).where(
                        FAQ.facility_id == test_facility.id,
                        FAQ.category == faq_data["category"],
                        FAQ.intent_key == intent_key
                    ).limit(1)
                )
                existing_faq = faq_result.scalar_one_or_none()
                
                if existing_faq:
                    created_faqs[faq_data["category"]] = existing_faq
                    print(f"  ✅ 既存のFAQを使用します: category={faq_data['category']}, id={existing_faq.id}, intent_key={intent_key}")
                else:
                    # FAQ（インテント）を作成
                    faq = FAQ(
                        facility_id=test_facility.id,
                        category=faq_data["category"],
                        intent_key=intent_key,
                        priority=1,
                        is_active=True,
                        created_by=test_user.id
                    )
                    session.add(faq)
                    await session.flush()
                    
                    # FAQTranslation（英語版）を作成
                    faq_translation = FAQTranslation(
                        faq_id=faq.id,
                        language="en",
                        question=faq_data["question"],
                        answer=faq_data["answer"],
                        embedding=None  # テストデータでは埋め込みベクトルは生成しない（必要に応じて後で生成可能）
                    )
                    session.add(faq_translation)
                    await session.flush()
                    
                    created_faqs[faq_data["category"]] = faq
                    print(f"  ✅ FAQを作成しました: category={faq_data['category']}, id={faq.id}, intent_key={intent_key}, translation_id={faq_translation.id}")
            
            # カテゴリ別内訳用の会話とメッセージを作成（過去7日以内）
            category_conversations_data = [
                {
                    "session_id": "test-session-category-basic-1",
                    "question": "What time is check-out?",
                    "language": "en",
                    "category": "basic",
                    "days_ago": 1
                },
                {
                    "session_id": "test-session-category-basic-2",
                    "question": "What time is check-out?",
                    "language": "en",
                    "category": "basic",
                    "days_ago": 2
                },
                {
                    "session_id": "test-session-category-facilities-1",
                    "question": "Do you have WiFi?",
                    "language": "en",
                    "category": "facilities",
                    "days_ago": 3
                },
                {
                    "session_id": "test-session-category-location-1",
                    "question": "Where is the nearest convenience store?",
                    "language": "en",
                    "category": "location",
                    "days_ago": 4
                },
                {
                    "session_id": "test-session-category-trouble-1",
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
                # FAQTranslation（英語版）を取得
                translation_result = await session.execute(
                    select(FAQTranslation).where(
                        FAQTranslation.faq_id == faq.id,
                        FAQTranslation.language == "en"
                    ).limit(1)
                )
                faq_translation = translation_result.scalar_one_or_none()
                
                assistant_message_result = await session.execute(
                    select(Message).where(
                        Message.conversation_id == conversation.id,
                        Message.role == MessageRole.ASSISTANT.value
                    ).limit(1)
                )
                existing_assistant_message = assistant_message_result.scalar_one_or_none()
                
                if not existing_assistant_message:
                    # FAQTranslationから回答を取得
                    answer_text = faq_translation.answer if faq_translation else "Answer not available"
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.ASSISTANT.value,
                        content=answer_text,
                        ai_confidence=Decimal("0.9"),
                        matched_faq_ids=[faq.id],  # カテゴリ別内訳用
                        created_at=datetime.utcnow() - timedelta(days=data["days_ago"]) + timedelta(minutes=1)
                    )
                    session.add(assistant_message)
                    await session.flush()
                    print(f"    ✅ AI応答メッセージを作成しました: message_id={assistant_message.id}, matched_faq_id={faq.id}, category={data['category']}")
                else:
                    # 既存のメッセージにmatched_faq_idsを追加
                    if not existing_assistant_message.matched_faq_ids:
                        existing_assistant_message.matched_faq_ids = [faq.id]
                        await session.flush()
                        print(f"    ✅ 既存のAI応答メッセージにmatched_faq_idsを追加しました: message_id={existing_assistant_message.id}, matched_faq_id={faq.id}, category={data['category']}")
                    else:
                        print(f"    ✅ AI応答メッセージは既に存在します: message_id={existing_assistant_message.id}")
            
            # ステップ4: 夜間対応キューのテストデータを作成
            print("\n🌙 夜間対応キューのテストデータを作成中...")
            
            overnight_queue_data = [
                {
                    "session_id": "test-session-overnight-1",
                    "question": "What time is breakfast?",
                    "language": "en",
                    "days_ago": 1
                },
                {
                    "session_id": "test-session-overnight-2",
                    "question": "朝食の時間は何時ですか？",
                    "language": "ja",
                    "days_ago": 2
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
            
            # コミット
            await session.commit()
            
            print("\n✅ テストデータの作成が完了しました！")
            print("\nテストユーザー情報:")
            print(f"  メールアドレス: test@example.com")
            print(f"  パスワード: testpassword123")
            print(f"  施設slug: test-facility")
            print(f"\nゲスト画面URL: http://localhost:5173/f/test-facility?location=entrance")
            print(f"管理画面ログインURL: http://localhost:5173/admin/login")
            print(f"\n未解決質問リスト:")
            print(f"  管理画面のFAQ管理画面で確認できます: http://localhost:5173/admin/faqs")
            print(f"\nカテゴリ別内訳:")
            print(f"  管理画面のダッシュボードで確認できます: http://localhost:5173/admin/dashboard")
            print(f"\n夜間対応キュー:")
            print(f"  管理画面のダッシュボードで確認できます: http://localhost:5173/admin/dashboard")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_data())

