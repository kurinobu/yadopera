"""
エスカレーション判定テスト
"""

import pytest
from decimal import Decimal
from datetime import datetime, time
from unittest.mock import AsyncMock, patch
from app.services.escalation_service import EscalationService
from app.models.escalation_schedule import EscalationSchedule
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class TestEscalation:
    """エスカレーション判定テスト"""
    
    @pytest.fixture
    def escalation_service(self):
        """EscalationServiceインスタンス"""
        return EscalationService()
    
    @pytest.mark.asyncio
    async def test_safety_category_escalation(self, db_session, test_facility, escalation_service):
        """安全カテゴリ即エスカレーションテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-1",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 安全カテゴリのメッセージでエスカレーション判定
        escalation_info = await escalation_service.check_escalation_needed(
            facility_id=test_facility.id,
            confidence=Decimal("0.9"),  # 高信頼度でも安全カテゴリは即エスカレ
            message="I need a hospital",
            session_id="test-session-1",
            language="en",
            conversation_id=conversation.id,
            db=db_session
        )
        
        assert escalation_info.needed is True
        assert escalation_info.trigger_type == "safety_category"
        assert escalation_info.mode == "normal"
    
    @pytest.mark.asyncio
    async def test_low_confidence_escalation(self, db_session, test_facility, escalation_service):
        """低信頼度エスカレーションテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-2",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 低信頼度でエスカレーション判定
        escalation_info = await escalation_service.check_escalation_needed(
            facility_id=test_facility.id,
            confidence=Decimal("0.5"),  # 閾値0.7未満
            message="What time is check-in?",
            session_id="test-session-2",
            language="en",
            conversation_id=conversation.id,
            db=db_session
        )
        
        assert escalation_info.needed is True
        assert escalation_info.trigger_type == "low_confidence"
    
    @pytest.mark.asyncio
    async def test_emergency_keyword_escalation(self, db_session, test_facility, escalation_service):
        """緊急キーワードエスカレーションテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-3",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 緊急キーワードでエスカレーション判定
        escalation_info = await escalation_service.check_escalation_needed(
            facility_id=test_facility.id,
            confidence=Decimal("0.8"),  # 高信頼度でも緊急キーワードは即エスカレ
            message="I need emergency help",
            session_id="test-session-3",
            language="en",
            conversation_id=conversation.id,
            db=db_session
        )
        
        assert escalation_info.needed is True
        assert escalation_info.trigger_type == "keyword"
    
    @pytest.mark.asyncio
    async def test_multiple_turns_escalation(self, db_session, test_facility, escalation_service):
        """3往復以上未解決エスカレーションテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-4",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 6メッセージ以上を作成（3往復）
        for i in range(6):
            message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER.value if i % 2 == 0 else MessageRole.ASSISTANT.value,
                content=f"Message {i}"
            )
            db_session.add(message)
        await db_session.commit()
        
        # エスカレーション判定
        escalation_info = await escalation_service.check_escalation_needed(
            facility_id=test_facility.id,
            confidence=Decimal("0.8"),  # 高信頼度でも3往復以上はエスカレ
            message="Another question",
            session_id="test-session-4",
            language="en",
            conversation_id=conversation.id,
            db=db_session
        )
        
        assert escalation_info.needed is True
        assert escalation_info.trigger_type == "multiple_turns"
    
    @pytest.mark.asyncio
    async def test_no_escalation_needed(self, db_session, test_facility, escalation_service):
        """エスカレーション不要テスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-5",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 高信頼度で通常の質問
        escalation_info = await escalation_service.check_escalation_needed(
            facility_id=test_facility.id,
            confidence=Decimal("0.8"),  # 閾値0.7以上
            message="What time is check-in?",
            session_id="test-session-5",
            language="en",
            conversation_id=conversation.id,
            db=db_session
        )
        
        assert escalation_info.needed is False
    
    @pytest.mark.asyncio
    async def test_create_escalation(self, db_session, test_facility, escalation_service):
        """エスカレーション作成テスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-6",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # エスカレーション作成
        escalation = await escalation_service.create_escalation(
            facility_id=test_facility.id,
            conversation_id=conversation.id,
            trigger_type="low_confidence",
            ai_confidence=0.5,
            escalation_mode="normal",
            notification_channels=["email"],
            db=db_session
        )
        
        assert escalation.id is not None
        assert escalation.facility_id == test_facility.id
        assert escalation.conversation_id == conversation.id
        assert escalation.trigger_type == "low_confidence"
        assert conversation.is_escalated is True


