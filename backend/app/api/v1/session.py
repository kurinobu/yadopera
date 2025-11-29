"""
セッション統合トークンAPIエンドポイント（v0.3新規）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.session import (
    SessionLinkRequest,
    SessionLinkResponse,
    SessionTokenVerifyResponse,
)
from app.services.session_token_service import SessionTokenService

router = APIRouter(prefix="/session", tags=["session"])

# サービスインスタンス
session_token_service = SessionTokenService()


@router.post("/link", response_model=SessionLinkResponse)
async def link_session(
    request: SessionLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    セッション統合
    
    - **facility_id**: 施設ID
    - **token**: セッション統合トークン（4桁英数字）
    - **current_session_id**: 現在のセッションID
    
    成功時はセッションが統合され、会話履歴が統合されます
    """
    try:
        token_obj = await session_token_service.link_session(
            facility_id=request.facility_id,
            token=request.token,
            new_session_id=request.current_session_id,
            db=db
        )
        
        return SessionLinkResponse(
            success=True,
            message="Session linked successfully",
            primary_session_id=token_obj.primary_session_id,
            linked_session_ids=token_obj.linked_session_ids or [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link session: {str(e)}"
        )


@router.get("/token/{token}", response_model=SessionTokenVerifyResponse)
async def verify_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    セッション統合トークン検証
    
    - **token**: セッション統合トークン（4桁英数字）
    
    トークンの有効性を確認し、トークン情報を返却します
    """
    token_obj = await session_token_service.verify_token(token, db)
    
    if token_obj is None:
        return SessionTokenVerifyResponse(
            valid=False,
            message="Invalid or expired token"
        )
    
    return SessionTokenVerifyResponse(
        valid=True,
        token=token_obj.token,
        primary_session_id=token_obj.primary_session_id,
        linked_session_ids=token_obj.linked_session_ids or [],
        expires_at=token_obj.expires_at,
        message="Token is valid"
    )

