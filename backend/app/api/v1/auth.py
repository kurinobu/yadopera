"""
認証APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, UserResponse, PasswordChangeRequest, PasswordChangeResponse, FacilityRegisterRequest
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.security import hash_password, verify_password

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


@router.post("/register", response_model=LoginResponse)
async def register_facility(
    request: FacilityRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    施設登録
    
    - **email**: 施設管理者メールアドレス
    - **password**: パスワード（最小8文字）
    - **facility_name**: 施設名
    - **subscription_plan**: 料金プラン（デフォルト: small）
    
    成功時は施設・ユーザー作成、FAQ自動投入、JWTアクセストークンを返却
    """
    try:
        return await AuthService.register_facility(db, request)
    except IntegrityError as e:
        # データベース制約違反のハンドリング
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "idx_facilities_slug" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="施設の登録に失敗しました。同じ施設名が既に登録されている可能性があります。"
            )
        elif "idx_facilities_email" in error_str or "email" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に登録されています。"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="施設の登録中にエラーが発生しました。"
            )
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        # その他の例外
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"予期しないエラーが発生しました: {str(e)}"
        )


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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ログアウト
    
    JWTトークンはクライアント側で削除
    認証が必要だが、403エラーが発生した場合でもログアウト処理は成功として扱う
    """
    try:
        await AuthService.logout(db, current_user)
        return LogoutResponse(message="Logged out successfully")
    except HTTPException as e:
        # 403エラー（非アクティブユーザーなど）が発生した場合でも、ログアウト処理は成功として扱う
        # クライアント側でトークンを削除するため、サーバー側での処理は不要
        if e.status_code == status.HTTP_403_FORBIDDEN:
            return LogoutResponse(message="Logged out successfully")
        raise


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

