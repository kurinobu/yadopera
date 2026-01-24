"""
依存性注入
認証・データベースセッション取得など
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.user import User
from app.core.jwt import decode_token

# HTTPBearerスキーム（Authorization: Bearer <token>）
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    現在のユーザー取得（JWT認証）
    
    Args:
        credentials: HTTPBearer認証情報
        db: データベースセッション
        
    Returns:
        認証されたユーザー
        
    Raises:
        HTTPException: 認証失敗時
    """
    token = credentials.credentials
    
    # トークンデコード
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザーID取得
    # JWT仕様（RFC 7519）に準拠: subフィールドは文字列として返される
    sub_value = payload.get("sub")
    if sub_value is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 文字列から整数に変換（JWT仕様に準拠）
    try:
        user_id = int(sub_value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザー取得
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def get_current_developer(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    開発者認証チェック（JWT認証）
    
    Args:
        credentials: HTTPBearer認証情報
        
    Returns:
        認証された開発者のペイロード
        
    Raises:
        HTTPException: 認証失敗時
    """
    token = credentials.credentials
    
    # トークンデコード
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid developer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 開発者トークンかどうかを確認（type='developer'を含む）
    if payload.get("type") != "developer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid developer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 有効期限チェック（JWTのexpフィールドで自動チェック済み）
    
    return payload  # 認証成功時、ペイロード返却

