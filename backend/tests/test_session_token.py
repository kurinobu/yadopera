"""
会話引き継ぎコードAPIテスト
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models.conversation import Conversation
from app.models.session_token import SessionToken


class TestSessionTokenVerify:
    """会話引き継ぎコード検証APIテスト"""
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, client, db_session, test_facility):
        """正常なトークン検証"""
        # 会話セッション作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-1",
            guest_language="en",
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
        response = await client.get("/api/v1/session/token/TEST")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert data["token"] == "TEST"
        assert data["primary_session_id"] == "test-session-1"
        assert "expires_at" in data
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, client):
        """無効なトークン検証"""
        response = await client.get("/api/v1/session/token/INVALID")
        
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
            guest_language="en",
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
        response = await client.get("/api/v1/session/token/EXPIRED")
        
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
            guest_language="en",
        )
        db_session.add(primary_conversation)
        
        # 新しいセッション作成
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session",
            guest_language="en",
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
        response = await client.post(
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
            guest_language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # セッション統合（無効なトークン）
        response = await client.post(
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
        # プライマリセッション作成（外部キー制約を満たすため）
        primary_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="primary-session-2",
            guest_language="en",
        )
        db_session.add(primary_conversation)
        
        # 新しいセッション作成
        new_conversation = Conversation(
            facility_id=test_facility.id,
            session_id="new-session-3",
            guest_language="en",
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
        response = await client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "EXPIRED2",
                "current_session_id": "new-session-3"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        # アーキテクチャ設計書の標準エラーフォーマットに準拠
        assert "error" in data
        assert "expired" in data["error"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_link_session_wrong_facility(self, client, db_session, test_facility):
        """異なる施設のトークンでのセッション統合"""
        # 別の施設作成
        from app.models.facility import Facility
        from sqlalchemy import select
        import uuid
        
        # ユニークなslugを生成（テストの重複実行を防ぐ）
        unique_slug = f"other-hotel-{uuid.uuid4().hex[:8]}"
        
        # 既存の施設を削除（重複を防ぐ）
        result = await db_session.execute(
            select(Facility).where(Facility.email == "other@example.com")
        )
        existing_facilities = result.scalars().all()
        for existing_facility in existing_facilities:
            await db_session.delete(existing_facility)
        await db_session.commit()
        
        other_facility = Facility(
            name="Other Hotel",
            slug=unique_slug,
            email="other@example.com",
            is_active=True,
        )
        db_session.add(other_facility)
        await db_session.commit()
        
        # 別施設のプライマリセッション作成（外部キー制約を満たすため）
        other_conversation = Conversation(
            facility_id=other_facility.id,
            session_id="other-session",
            guest_language="en",
        )
        db_session.add(other_conversation)
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
            guest_language="en",
        )
        db_session.add(new_conversation)
        await db_session.commit()
        
        # セッション統合（異なる施設のトークン）
        response = await client.post(
            "/api/v1/session/link",
            json={
                "facility_id": test_facility.id,
                "token": "OTHER",
                "current_session_id": "new-session-4"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        # アーキテクチャ設計書の標準エラーフォーマットに準拠
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"

