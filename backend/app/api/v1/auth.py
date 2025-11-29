"""
認証APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    ログイン
    
    - **email**: メールアドレス
    - **password**: パスワード
    
    成功時はJWTアクセストークンを返却
    """
    return await AuthService.login(db, login_data)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ログアウト
    
    JWTトークンはクライアント側で削除
    """
    await AuthService.logout(db, current_user)
    return LogoutResponse(message="Logged out successfully")

