"""
認証APIテスト
"""

import pytest
from fastapi import status
from app.models.user import User
from app.core.security import hash_password


class TestLogin:
    """ログインAPIテスト"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """正常なログイン"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client, test_user):
        """存在しないメールアドレスでのログイン"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, test_user):
        """間違ったパスワードでのログイン"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db_session, test_facility):
        """非アクティブユーザーでのログイン"""
        from app.models.user import User
        
        inactive_user = User(
            facility_id=test_facility.id,
            email="inactive@example.com",
            password_hash=hash_password("testpassword123"),
            full_name="Inactive User",
            role="staff",
            is_active=False,
        )
        db_session.add(inactive_user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_login_validation_error(self, client):
        """バリデーションエラー（メールアドレスなし）"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        # FastAPIのバリデーションエラーは "detail" キーを使用
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0
        # エラーの詳細を確認
        error_detail = data["detail"][0]
        assert "loc" in error_detail
        assert "msg" in error_detail
        assert "type" in error_detail


class TestLogout:
    """ログアウトAPIテスト"""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client, test_user):
        """正常なログアウト"""
        # まずログイン
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # ログアウト
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Logged out successfully"
    
    @pytest.mark.asyncio
    async def test_logout_without_token(self, client):
        """トークンなしでのログアウト"""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, client):
        """無効なトークンでのログアウト"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

