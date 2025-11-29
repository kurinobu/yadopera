"""
チャットサービス統合テスト
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class TestChatService:
    """チャットサービス統合テスト"""
    
    @pytest.mark.asyncio
    @patch('app.services.chat_service.RAGChatEngine')
    async def test_process_chat_message_new_conversation(
        self,
        mock_rag_engine_class,
        db_session,
        test_facility
    ):
        """新規会話でのメッセージ処理テスト"""
        # モック設定
        mock_rag_engine = AsyncMock()
        mock_response = AsyncMock()
        mock_response.message_id = 1
        mock_response.session_id = "new-session-1"
        mock_response.response = "Test response"
        mock_response.ai_confidence = 0.8
        mock_response.source = "rag_generated"
        mock_response.matched_faq_ids = [1]
        mock_response.response_time_ms = 100
        mock_response.escalation.needed = False
        
        mock_rag_engine.process_message = AsyncMock(return_value=mock_response)
        mock_rag_engine_class.return_value = mock_rag_engine
        
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        chat_service.rag_engine = mock_rag_engine
        
        # テスト実行
        request = ChatRequest(
            facility_id=test_facility.id,
            message="What time is check-in?",
            language="en"
        )
        
        response = await chat_service.process_chat_message(
            request=request,
            user_agent="Test Agent",
            ip_address="127.0.0.1"
        )
        
        # アサーション
        assert response.session_id is not None
        assert response.response == "Test response"
        
        # 会話が作成されたか確認
        from sqlalchemy import select
        result = await db_session.execute(
            select(Conversation).where(Conversation.session_id == response.session_id)
        )
        conversation = result.scalar_one_or_none()
        assert conversation is not None
        assert conversation.facility_id == test_facility.id
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, db_session, test_facility):
        """会話履歴取得テスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-history",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # メッセージ追加
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="What time is check-in?"
        )
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content="Check-in is from 3pm to 10pm."
        )
        db_session.add(user_message)
        db_session.add(ai_message)
        await db_session.commit()
        
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        
        # テスト実行
        history = await chat_service.get_conversation_history(
            session_id="test-session-history",
            facility_id=test_facility.id
        )
        
        # アサーション
        assert history is not None
        assert history.session_id == "test-session-history"
        assert len(history.messages) == 2
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_not_found(self, db_session):
        """会話履歴が見つからない場合のテスト"""
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        
        # テスト実行
        history = await chat_service.get_conversation_history(
            session_id="non-existent-session",
            facility_id=1
        )
        
        # アサーション
        assert history is None

