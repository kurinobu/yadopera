"""
チャットAPIエンドポイントテスト
"""

import pytest
from datetime import datetime
from fastapi import status
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class TestChatAPI:
    """チャットAPIエンドポイントテスト"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires OpenAI API key and complex mocking")
    async def test_send_chat_message(self, client, test_facility):
        """チャットメッセージ送信テスト（スキップ）"""
        # このテストはOpenAI APIキーと複雑なモックが必要なためスキップ
        # 統合テスト環境で実行する
        pass
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, client, db_session, test_facility):
        """会話履歴取得APIテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-api-session",
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
        
        # API呼び出し
        response = client.get(f"/api/v1/chat/history/test-api-session")
        
        # アサーション
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "test-api-session"
        assert len(data["messages"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_chat_history_not_found(self, client):
        """会話履歴が見つからない場合のテスト"""
        # API呼び出し
        response = client.get("/api/v1/chat/history/non-existent-session")
        
        # アサーション
        assert response.status_code == status.HTTP_404_NOT_FOUND

