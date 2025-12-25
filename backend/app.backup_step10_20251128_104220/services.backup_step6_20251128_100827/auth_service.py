"""
認証サービス
認証ビジネスロジック
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.user import User
from app.core.security import verify_password, hash_password
from app.core.jwt import create_access_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from fastapi import HTTPException, status
from typing import Optional


class AuthService:
    """
    認証サービス
    """
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        login_data: LoginRequest
    ) -> Optional[User]:
        """
        ユーザー認証
        
        Args:
            db: データベースセッション
            login_data: ログインリクエストデータ
            
        Returns:
            認証されたユーザー（認証失敗時はNone）
        """
        # ユーザー取得
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return None
        
        # パスワード検証
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # アクティブユーザーか確認
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def login(
        db: AsyncSession,
        login_data: LoginRequest
    ) -> LoginResponse:
        """
        ログイン処理
        
        Args:
            db: データベースセッション
            login_data: ログインリクエストデータ
            
        Returns:
            ログインレスポンス
            
        Raises:
            HTTPException: 認証失敗時
        """
        # ユーザー認証
        user = await AuthService.authenticate_user(db, login_data)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 最終ログイン時刻更新
        user.last_login_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        # JWTトークン生成
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        # レスポンス作成
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # 秒単位
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                facility_id=user.facility_id,
                is_active=user.is_active,
            )
        )
    
    @staticmethod
    async def logout(
        db: AsyncSession,
        user: User
    ) -> dict:
        """
        ログアウト処理（JWTは無効化しない、クライアント側で削除）
        
        Args:
            db: データベースセッション
            user: ユーザー
            
        Returns:
            ログアウトレスポンス
        """
        # JWTはステートレスなので、サーバー側での無効化は不要
        # 必要に応じてRedisに無効化リストを保存することも可能
        return {"message": "Logged out successfully"}

