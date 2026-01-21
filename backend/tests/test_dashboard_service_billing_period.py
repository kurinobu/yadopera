"""
ダッシュボードサービスの請求期間ベース集計テスト
"""

import pytest
from datetime import datetime, timedelta
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from app.services.dashboard_service import DashboardService


class TestDashboardServiceBillingPeriod:
    """ダッシュボードサービスの請求期間ベース集計テスト"""
    
    @pytest.mark.asyncio
    async def test_get_monthly_usage_within_billing_period(self, db_session: AsyncSession):
        """請求期間内の質問数が正しく集計される"""
        jst = pytz.timezone('Asia/Tokyo')
        utc = pytz.UTC
        
        # 施設を作成（プラン開始日: 2026-01-15 10:00:00 JST）
        plan_started_at_jst = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        plan_started_at_utc = plan_started_at_jst.astimezone(utc)
        
        facility = Facility(
            name="Test Hotel",
            slug="test-hotel-billing",
            email="test-billing@example.com",
            plan_type="Small",
            monthly_question_limit=200,
            plan_started_at=plan_started_at_utc,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        
        # 会話とメッセージを作成
        # 請求期間内のメッセージ（2026-01-20 15:00:00 JST = 2026-01-20 06:00:00 UTC）
        conversation1 = Conversation(
            facility_id=facility.id,
            session_id="test-session-1",
            started_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0))
        )
        db_session.add(conversation1)
        await db_session.flush()
        
        message1 = Message(
            conversation_id=conversation1.id,
            role=MessageRole.USER.value,
            content="質問1",
            created_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0))
        )
        db_session.add(message1)
        
        # 請求期間外のメッセージ（2026-02-20 15:00:00 JST = 2026-02-20 06:00:00 UTC）
        # これは2回目の請求期間なので、1回目の請求期間の集計には含まれない
        conversation2 = Conversation(
            facility_id=facility.id,
            session_id="test-session-2",
            started_at=utc.localize(datetime(2026, 2, 20, 6, 0, 0))
        )
        db_session.add(conversation2)
        await db_session.flush()
        
        message2 = Message(
            conversation_id=conversation2.id,
            role=MessageRole.USER.value,
            content="質問2",
            created_at=utc.localize(datetime(2026, 2, 20, 6, 0, 0))
        )
        db_session.add(message2)
        
        await db_session.commit()
        
        # 現在時刻を1回目の請求期間内に設定（2026-01-25 15:00:00 JST）
        # モックを使用して現在時刻を固定
        from unittest.mock import patch, MagicMock
        now_jst = jst.localize(datetime(2026, 1, 25, 15, 0, 0))
        
        # datetime.now(jst)をモック
        with patch('app.services.dashboard_service.datetime') as mock_datetime:
            # datetime.now(jst)の呼び出しをモック
            def mock_now(tz=None):
                if tz == jst:
                    return now_jst
                return datetime.now(tz)
            
            mock_datetime.now = MagicMock(side_effect=mock_now)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            service = DashboardService(db_session)
            result = await service.get_monthly_usage(facility.id)
        
        # 請求期間内のメッセージのみが集計される
        assert result is not None
        assert result.current_month_questions == 1  # message1のみ
        assert result.plan_type == "Small"
        assert result.plan_limit == 200
    
    @pytest.mark.asyncio
    async def test_get_monthly_usage_outside_billing_period(self, db_session: AsyncSession):
        """請求期間外の質問数が集計されない"""
        jst = pytz.timezone('Asia/Tokyo')
        utc = pytz.UTC
        
        # 施設を作成（プラン開始日: 2026-01-15 10:00:00 JST）
        plan_started_at_jst = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        plan_started_at_utc = plan_started_at_jst.astimezone(utc)
        
        facility = Facility(
            name="Test Hotel 2",
            slug="test-hotel-billing-2",
            email="test-billing-2@example.com",
            plan_type="Small",
            monthly_question_limit=200,
            plan_started_at=plan_started_at_utc,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        
        # 請求期間外のメッセージ（プラン開始前: 2026-01-10 15:00:00 JST）
        conversation = Conversation(
            facility_id=facility.id,
            session_id="test-session-outside",
            started_at=utc.localize(datetime(2026, 1, 10, 6, 0, 0))
        )
        db_session.add(conversation)
        await db_session.flush()
        
        message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="質問（期間外）",
            created_at=utc.localize(datetime(2026, 1, 10, 6, 0, 0))
        )
        db_session.add(message)
        await db_session.commit()
        
        # 現在時刻を1回目の請求期間内に設定（2026-01-25 15:00:00 JST）
        from unittest.mock import patch, MagicMock
        now_jst = jst.localize(datetime(2026, 1, 25, 15, 0, 0))
        
        # datetime.now(jst)をモック
        with patch('app.services.dashboard_service.datetime') as mock_datetime:
            def mock_now(tz=None):
                if tz == jst:
                    return now_jst
                return datetime.now(tz)
            
            mock_datetime.now = MagicMock(side_effect=mock_now)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            service = DashboardService(db_session)
            result = await service.get_monthly_usage(facility.id)
        
        # 請求期間外のメッセージは集計されない
        assert result is not None
        assert result.current_month_questions == 0
    
    @pytest.mark.asyncio
    async def test_get_monthly_usage_multiple_billing_periods(self, db_session: AsyncSession):
        """複数の請求期間にまたがるデータのテスト"""
        jst = pytz.timezone('Asia/Tokyo')
        utc = pytz.UTC
        
        # 施設を作成（プラン開始日: 2026-01-15 10:00:00 JST）
        plan_started_at_jst = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        plan_started_at_utc = plan_started_at_jst.astimezone(utc)
        
        facility = Facility(
            name="Test Hotel 3",
            slug="test-hotel-billing-3",
            email="test-billing-3@example.com",
            plan_type="Small",
            monthly_question_limit=200,
            plan_started_at=plan_started_at_utc,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        
        # 1回目の請求期間内のメッセージ（2026-01-20）
        conversation1 = Conversation(
            facility_id=facility.id,
            session_id="test-session-period-1",
            started_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0))
        )
        db_session.add(conversation1)
        await db_session.flush()
        
        message1 = Message(
            conversation_id=conversation1.id,
            role=MessageRole.USER.value,
            content="質問1（1回目）",
            created_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0))
        )
        db_session.add(message1)
        
        # 2回目の請求期間内のメッセージ（2026-02-20）
        conversation2 = Conversation(
            facility_id=facility.id,
            session_id="test-session-period-2",
            started_at=utc.localize(datetime(2026, 2, 20, 6, 0, 0))
        )
        db_session.add(conversation2)
        await db_session.flush()
        
        message2 = Message(
            conversation_id=conversation2.id,
            role=MessageRole.USER.value,
            content="質問2（2回目）",
            created_at=utc.localize(datetime(2026, 2, 20, 6, 0, 0))
        )
        db_session.add(message2)
        
        await db_session.commit()
        
        # 現在時刻を2回目の請求期間内に設定（2026-02-25 15:00:00 JST）
        from unittest.mock import patch, MagicMock
        now_jst = jst.localize(datetime(2026, 2, 25, 15, 0, 0))
        
        # datetime.now(jst)をモック
        with patch('app.services.dashboard_service.datetime') as mock_datetime:
            def mock_now(tz=None):
                if tz == jst:
                    return now_jst
                return datetime.now(tz)
            
            mock_datetime.now = MagicMock(side_effect=mock_now)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            service = DashboardService(db_session)
            result = await service.get_monthly_usage(facility.id)
        
        # 2回目の請求期間内のメッセージのみが集計される
        assert result is not None
        assert result.current_month_questions == 1  # message2のみ
    
    @pytest.mark.asyncio
    async def test_get_ai_automation_within_billing_period(self, db_session: AsyncSession):
        """請求期間内のAI自動応答数が正しく集計される"""
        jst = pytz.timezone('Asia/Tokyo')
        utc = pytz.UTC
        
        # 施設を作成
        plan_started_at_jst = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        plan_started_at_utc = plan_started_at_jst.astimezone(utc)
        
        facility = Facility(
            name="Test Hotel AI",
            slug="test-hotel-ai",
            email="test-ai@example.com",
            plan_type="Small",
            monthly_question_limit=200,
            plan_started_at=plan_started_at_utc,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        
        # 会話とメッセージを作成（エスカレーションなし）
        conversation = Conversation(
            facility_id=facility.id,
            session_id="test-session-ai",
            started_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0)),
            is_escalated=False
        )
        db_session.add(conversation)
        await db_session.flush()
        
        # ユーザーメッセージ
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="質問",
            created_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0))
        )
        db_session.add(user_message)
        
        # AI応答メッセージ
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content="回答",
            created_at=utc.localize(datetime(2026, 1, 20, 6, 1, 0))
        )
        db_session.add(ai_message)
        
        await db_session.commit()
        
        # 現在時刻を1回目の請求期間内に設定
        from unittest.mock import patch, MagicMock
        now_jst = jst.localize(datetime(2026, 1, 25, 15, 0, 0))
        
        # datetime.now(jst)をモック
        with patch('app.services.dashboard_service.datetime') as mock_datetime:
            def mock_now(tz=None):
                if tz == jst:
                    return now_jst
                return datetime.now(tz)
            
            mock_datetime.now = MagicMock(side_effect=mock_now)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            service = DashboardService(db_session)
            result = await service.get_ai_automation(facility.id)
        
        # 請求期間内のAI自動応答数が正しく集計される
        assert result is not None
        assert result.ai_responses == 1
        assert result.total_questions == 1
        assert result.automation_rate == 100.0
    
    @pytest.mark.asyncio
    async def test_get_escalations_summary_within_billing_period(self, db_session: AsyncSession):
        """請求期間内のエスカレーション数が正しく集計される"""
        jst = pytz.timezone('Asia/Tokyo')
        utc = pytz.UTC
        
        # 施設を作成
        plan_started_at_jst = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        plan_started_at_utc = plan_started_at_jst.astimezone(utc)
        
        facility = Facility(
            name="Test Hotel Escalation",
            slug="test-hotel-escalation",
            email="test-escalation@example.com",
            plan_type="Small",
            monthly_question_limit=200,
            plan_started_at=plan_started_at_utc,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        
        # 会話とエスカレーションを作成
        conversation = Conversation(
            facility_id=facility.id,
            session_id="test-session-escalation",
            started_at=utc.localize(datetime(2026, 1, 20, 6, 0, 0)),
            is_escalated=True
        )
        db_session.add(conversation)
        await db_session.flush()
        
        # エスカレーション（未解決）
        escalation = Escalation(
            facility_id=facility.id,
            conversation_id=conversation.id,
            created_at=utc.localize(datetime(2026, 1, 20, 6, 5, 0)),
            resolved_at=None
        )
        db_session.add(escalation)
        
        await db_session.commit()
        
        # 現在時刻を1回目の請求期間内に設定
        from unittest.mock import patch, MagicMock
        now_jst = jst.localize(datetime(2026, 1, 25, 15, 0, 0))
        
        # datetime.now(jst)をモック
        with patch('app.services.dashboard_service.datetime') as mock_datetime:
            def mock_now(tz=None):
                if tz == jst:
                    return now_jst
                return datetime.now(tz)
            
            mock_datetime.now = MagicMock(side_effect=mock_now)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            service = DashboardService(db_session)
            result = await service.get_escalations_summary(facility.id)
        
        # 請求期間内のエスカレーション数が正しく集計される
        assert result is not None
        assert result.total == 1
        assert result.unresolved == 1
        assert result.resolved == 0

