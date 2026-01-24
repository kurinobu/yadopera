"""
開発者認証APIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status, Request
from datetime import timedelta
from app.schemas.developer import DeveloperLoginRequest, DeveloperLoginResponse
from app.core.jwt import create_access_token
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=DeveloperLoginResponse)
async def developer_login(
    login_data: DeveloperLoginRequest,
    request: Request
):
    """
    開発者ログイン
    
    - **password**: 開発者パスワード（環境変数DEVELOPER_PASSWORDと照合）
    
    成功時はJWTアクセストークンを返却
    """
    # 環境変数から開発者パスワードを取得
    developer_password = settings.developer_password
    
    if not developer_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Developer password not configured"
        )
    
    # パスワード照合
    if login_data.password != developer_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWTトークン生成（type='developer'を含む）
    expires_delta = timedelta(hours=settings.developer_session_expire_hours)
    access_token = create_access_token(
        data={"sub": "developer", "type": "developer"},
        expires_delta=expires_delta
    )
    
    # レスポンス作成
    return DeveloperLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.developer_session_expire_hours * 3600  # 秒単位
    )

