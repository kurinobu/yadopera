"""
認証APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user, get_optional_user
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, UserResponse, PasswordChangeRequest, PasswordChangeResponse
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.security import hash_password, verify_password
from typing import Optional

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザー情報取得
    
    JWTトークンから現在のユーザー情報を返却
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        facility_id=current_user.facility_id,
        is_active=current_user.is_active
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    optional_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ログアウト
    
    JWTトークンはクライアント側で削除
    認証はオプション（トークンが無効でもログアウト処理は成功）
    403エラーが発生してもログアウト処理は成功として扱う
    """
    try:
        # ユーザーが認証されている場合のみ、ログアウト処理を実行
        if optional_user is not None:
            await AuthService.logout(db, optional_user)
        return LogoutResponse(message="Logged out successfully")
    except Exception:
        # エラーが発生してもログアウト処理は成功として扱う
        # クライアント側でトークンを削除するため、サーバー側での処理は不要
        return LogoutResponse(message="Logged out successfully")


@router.put("/password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    パスワード変更
    
    JWT認証必須。現在のユーザーのパスワードを変更します。
    
    - **current_password**: 現在のパスワード
    - **new_password**: 新しいパスワード（最小8文字）
    - **confirm_password**: 新しいパスワード（確認）
    """
    try:
        # 現在のパスワードを検証
        if not verify_password(request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # 新しいパスワードを検証
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password do not match"
            )
        
        # パスワード強度チェック（最小8文字）
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # パスワードをハッシュ化して更新
        current_user.password_hash = hash_password(request.new_password)
        await db.commit()
        
        return PasswordChangeResponse(message="Password changed successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )

