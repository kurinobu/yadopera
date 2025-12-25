"""
セッション統合トークンAPIテスト
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models.conversation import Conversation
from app.models.session_token import SessionToken


class TestSessionTokenVerify:
    """セッション統合トークン検証APIテスト"""
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, client, db_session, test_facility):
        """正常なトークン検証"""
        # 会話セッション作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-1",
            language="en",
        )
        db_session.add(conversation)
        await db_session.commit()
        
        # トークン作成
        token_obj = SessionToken(
            facility_id=test_facility.id,
            token="TEST",
            primary_session_id="test-session-1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(token_obj)
        await db_session.commit()
        
        # トークン検証
        response = client.get("/api/v1/session/token/TEST")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert data["token"] == "TEST"
        assert data["primary_session_id"] == "test-session-1"
        assert "expires_at" in data
    
    def test_verify_token_invalid(self, client):
        """無効なトークン検証"""
        response = client.get("/api/v1/session/token/INVALID")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert "Invalid or expired token" in data["message"]
    
    @pytest.mark.asyncio
    async def test_verify_token_expired(self, client, db_session, test_facility):
        """期限切れトークン検証"""
        # 会話セッション作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-2",
            language="en",
        )
        db_session.add(conversation)
        await db_session.commit()
        
        # 期限切れトークン作成
        token_obj = SessionToken(
            facility_id=test_facility.id,
            token="EXPIRED",
            primary_session_id="test-session-2",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(token_obj)
        await db_session.commit()
        
        # トークン検証
        response = client.get("/api/v1/session/token/EXPIRED")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False


class TestSessionLink:
    """セッション統合APIテスト"""
    
    @pytest.mark.asyncio
    async def test_link_session_success(self, client, db_session, test_facility):
        """正常なセッション統合"""
        # プライマリセッション作成
        primary_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="primary-session",
            language="en",
        )
        db_session.add(primary_conversation)
        
        # 新しいセッション作成
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session",
            language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # トークン作成
        token_obj = SessionToken(
            facility_id=test_facility.id,
            token="LINK",
            primary_session_id="primary-session",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(token_obj)
        await db_session.commit()
        
        # セッション統合
        response = client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "LINK",
                "current_session_id": "new-session"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["primary_session_id"] == "primary-session"
        assert "new-session" in data["linked_session_ids"]
    
    @pytest.mark.asyncio
    async def test_link_session_invalid_token(self, client, db_session, test_facility):
        """無効なトークンでのセッション統合"""
        # 新しいセッション作成
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session-2",
            language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # セッション統合（無効なトークン）
        response = client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "INVALID",
                "current_session_id": "new-session-2"
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_link_session_expired_token(self, client, db_session, test_facility):
        """期限切れトークンでのセッション統合"""
        # 新しいセッション作成
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session-3",
            language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # 期限切れトークン作成
        token_obj = SessionToken(
            facility_id=test_facility.id,
            token="EXPIRED2",
            primary_session_id="primary-session-2",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(token_obj)
        await db_session.commit()
        
        # セッション統合
        response = client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "EXPIRED2",
                "current_session_id": "new-session-3"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "expired" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_link_session_wrong_facility(self, client, db_session, test_facility):
        """異なる施設のトークンでのセッション統合"""
        # 別の施設作成
        from app.models.facility import Facility
        
        other_facility = Facility(
            name="Other Hotel",
            slug="other-hotel",
            email="other@example.com",
            is_active=True,
        )
        db_session.add(other_facility)
        await db_session.commit()
        
        # 別施設のトークン作成
        token_obj = SessionToken(
            facility_id=other_facility.id,
            token="OTHER",
            primary_session_id="other-session",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(token_obj)
        await db_session.commit()
        
        # 新しいセッション作成（test_facility）
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session-4",
            language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # セッション統合（異なる施設のトークン）
        response = client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "OTHER",
                "current_session_id": "new-session-4"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

