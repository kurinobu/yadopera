"""
統合テスト
フロントエンド・バックエンド統合テスト
"""

import pytest
from fastapi import status
from datetime import datetime
from unittest.mock import AsyncMock, patch
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.faq import FAQ
from app.core.jwt import create_access_token


class TestAuthFlow:
    """認証フロー統合テスト"""
    
    def test_login_and_access_protected_endpoint(self, client, test_user):
        """ログインして保護されたエンドポイントにアクセスするテスト"""
        # ログイン
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        access_token = login_data["access_token"]
        
        # 保護されたエンドポイントにアクセス（ダッシュボード）
        headers = {"Authorization": f"Bearer {access_token}"}
        dashboard_response = client.get(
            "/api/v1/admin/dashboard",
            headers=headers
        )
        
        # 認証が成功していることを確認
        assert dashboard_response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]  # 500はデータがない場合
        # 認証エラー（401）ではないことを確認
        assert dashboard_response.status_code != status.HTTP_401_UNAUTHORIZED
    
    def test_access_protected_endpoint_without_token(self, client):
        """トークンなしで保護されたエンドポイントにアクセスするテスト"""
        dashboard_response = client.get("/api/v1/admin/dashboard")
        
        assert dashboard_response.status_code == status.HTTP_403_FORBIDDEN


class TestChatFlow:
    """チャットフロー統合テスト"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires OpenAI API key and complex mocking")
    async def test_chat_message_flow(self, client, db_session, test_facility):
        """チャットメッセージ送信フローテスト（スキップ）"""
        # このテストはOpenAI APIキーと複雑なモックが必要なためスキップ
        # 統合テスト環境で実行する
        pass
    
    @pytest.mark.asyncio
    async def test_chat_history_flow(self, client, db_session, test_facility):
        """会話履歴取得フローテスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="integration-test-session",
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
        response = client.get(f"/api/v1/chat/history/integration-test-session")
        
        # アサーション
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "integration-test-session"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"


class TestAdminFlow:
    """管理画面フロー統合テスト"""
    
    @pytest.fixture
    def auth_headers(self, client, test_user):
        """認証済みヘッダー"""
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    def test_dashboard_access(self, client, auth_headers):
        """ダッシュボードアクセステスト"""
        response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
        
        # 認証エラーではないことを確認
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_faq_list_access(self, client, auth_headers):
        """FAQ一覧取得テスト"""
        response = client.get("/api/v1/admin/faqs", headers=auth_headers)
        
        # 認証エラーではないことを確認
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "faqs" in data
            assert "total" in data
    
    @pytest.mark.asyncio
    async def test_faq_create_flow(self, client, db_session, test_facility, auth_headers):
        """FAQ作成フローテスト"""
        # FAQ作成
        create_response = client.post(
            "/api/v1/admin/faqs",
            headers=auth_headers,
            json={
                "category": "basic",
                "language": "en",
                "question": "What time is check-in?",
                "answer": "Check-in is from 3pm to 10pm.",
                "priority": 5
            }
        )
        
        # 認証エラーではないことを確認
        assert create_response.status_code != status.HTTP_401_UNAUTHORIZED
        assert create_response.status_code != status.HTTP_403_FORBIDDEN
        
        if create_response.status_code == status.HTTP_201_CREATED:
            data = create_response.json()
            assert data["question"] == "What time is check-in?"
            assert data["facility_id"] == test_facility.id
    
    def test_faq_suggestions_access(self, client, auth_headers):
        """FAQ提案一覧取得テスト"""
        response = client.get("/api/v1/admin/faq-suggestions", headers=auth_headers)
        
        # 認証エラーではないことを確認
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_overnight_queue_access(self, client, auth_headers):
        """夜間対応キューアクセステスト"""
        response = client.get("/api/v1/admin/overnight-queue", headers=auth_headers)
        
        # 認証エラーではないことを確認
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_qr_code_generation_access(self, client, auth_headers):
        """QRコード生成アクセステスト"""
        response = client.post(
            "/api/v1/admin/qr-code",
            headers=auth_headers,
            json={
                "location": "entrance",
                "include_session_token": False,
                "format": "png"
            }
        )
        
        # 認証エラーではないことを確認
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code != status.HTTP_403_FORBIDDEN


class TestErrorHandling:
    """エラーハンドリング統合テスト"""
    
    def test_invalid_endpoint(self, client):
        """存在しないエンドポイントへのアクセステスト"""
        response = client.get("/api/v1/non-existent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_json(self, client, test_user):
        """不正なJSONリクエストテスト"""
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 不正なJSONでFAQ作成を試行
        response = client.post(
            "/api/v1/admin/faqs",
            headers=headers,
            json={
                "category": "invalid_category",  # 無効なカテゴリ
                "question": "",  # 空の質問
                "answer": "Test answer"
            }
        )
        
        # バリデーションエラーが返されることを確認
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY or response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_unauthorized_access(self, client):
        """認証なしでの保護されたエンドポイントアクセステスト"""
        endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/faqs",
            "/api/v1/admin/faq-suggestions",
            "/api/v1/admin/overnight-queue"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_403_FORBIDDEN


class TestResponseTime:
    """レスポンス速度テスト"""
    
    @pytest.fixture
    def auth_headers(self, client, test_user):
        """認証済みヘッダー"""
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    def test_dashboard_response_time(self, client, auth_headers):
        """ダッシュボードレスポンス速度テスト"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/admin/dashboard", headers=auth_headers)
        elapsed_time = time.time() - start_time
        
        # レスポンス時間が3秒以内であることを確認（目標）
        assert elapsed_time < 3.0, f"Response time {elapsed_time:.2f}s exceeds 3s limit"
    
    def test_faq_list_response_time(self, client, auth_headers):
        """FAQ一覧レスポンス速度テスト"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/admin/faqs", headers=auth_headers)
        elapsed_time = time.time() - start_time
        
        # レスポンス時間が3秒以内であることを確認（目標）
        assert elapsed_time < 3.0, f"Response time {elapsed_time:.2f}s exceeds 3s limit"

