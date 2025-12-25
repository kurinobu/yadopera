"""
認証関連スキーマ
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """
    ログインリクエスト
    """
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード")


class UserResponse(BaseModel):
    """
    ユーザー情報レスポンス
    """
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    facility_id: int
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """
    ログインレスポンス
    """
    access_token: str = Field(..., description="JWTアクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
    expires_in: int = Field(..., description="トークン有効期限（秒）")
    user: UserResponse = Field(..., description="ユーザー情報")


class LogoutResponse(BaseModel):
    """
    ログアウトレスポンス
    """
    message: str = Field(default="Logged out successfully", description="ログアウトメッセージ")


class PasswordChangeRequest(BaseModel):
    """
    パスワード変更リクエスト
    """
    current_password: str = Field(..., min_length=1, description="現在のパスワード")
    new_password: str = Field(..., min_length=8, description="新しいパスワード（最小8文字）")
    confirm_password: str = Field(..., min_length=8, description="新しいパスワード（確認）")


class PasswordChangeResponse(BaseModel):
    """
    パスワード変更レスポンス
    """
    message: str = Field(default="Password changed successfully", description="パスワード変更メッセージ")

