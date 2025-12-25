"""
夜間対応キュー処理テスト
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.services.overnight_queue_service import OvernightQueueService
from app.models.overnight_queue import OvernightQueue
from app.models.escalation import Escalation
from app.models.conversation import Conversation


class TestOvernightQueue:
    """夜間対応キュー処理テスト"""
    
    @pytest.fixture
    def queue_service(self):
        """OvernightQueueServiceインスタンス"""
        return OvernightQueueService()
    
    @pytest.mark.asyncio
    async def test_add_to_overnight_queue(self, db_session, test_facility, queue_service):
        """夜間対応キュー追加テスト"""
        # 会話とエスカレーション作成
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
        
        escalation = Escalation(
            facility_id=test_facility.id,
            conversation_id=conversation.id,
            trigger_type="low_confidence",
            ai_confidence=0.5,
            escalation_mode="normal"
        )
        db_session.add(escalation)
        await db_session.commit()
        await db_session.refresh(escalation)
        
        # 夜間対応キューに追加
        queue = await queue_service.add_to_overnight_queue(
            facility_id=test_facility.id,
            escalation_id=escalation.id,
            guest_message="Test message",
            db=db_session
        )
        
        assert queue.id is not None
        assert queue.facility_id == test_facility.id
        assert queue.escalation_id == escalation.id
        assert queue.guest_message == "Test message"
        assert queue.scheduled_notify_at is not None
    
    @pytest.mark.asyncio
    async def test_get_overnight_queue(self, db_session, test_facility, queue_service):
        """夜間対応キュー取得テスト"""
        # 会話とエスカレーション作成
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
        
        escalation = Escalation(
            facility_id=test_facility.id,
            conversation_id=conversation.id,
            trigger_type="low_confidence",
            ai_confidence=0.5,
            escalation_mode="normal"
        )
        db_session.add(escalation)
        await db_session.commit()
        await db_session.refresh(escalation)
        
        # 夜間対応キューに追加
        queue = await queue_service.add_to_overnight_queue(
            facility_id=test_facility.id,
            escalation_id=escalation.id,
            guest_message="Test message",
            db=db_session
        )
        
        # キュー取得
        queues = await queue_service.get_overnight_queue(
            facility_id=test_facility.id,
            db=db_session,
            include_resolved=False
        )
        
        assert len(queues) > 0
        assert any(q.id == queue.id for q in queues)
    
    @pytest.mark.asyncio
    async def test_send_overnight_auto_reply(self, db_session, queue_service):
        """夜間自動返信メッセージ送信テスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=1,
            session_id="test-session-3",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # 夜間自動返信送信
        await queue_service.send_overnight_auto_reply(
            conversation_id=conversation.id,
            language="en",
            db=db_session
        )
        
        # メッセージが追加されたか確認
        from app.models.message import Message
        from sqlalchemy import select
        result = await db_session.execute(
            select(Message).where(Message.conversation_id == conversation.id)
        )
        messages = result.scalars().all()
        
        assert len(messages) > 0
        # システムメッセージが追加されているか確認
        system_messages = [m for m in messages if m.role == "system"]
        assert len(system_messages) > 0


