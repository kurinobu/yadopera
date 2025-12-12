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
    SessionTokenGenerateRequest,
    SessionTokenResponse,
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


@router.post("/generate", response_model=SessionTokenResponse)
async def generate_token(
    request: SessionTokenGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    セッション統合トークン生成
    
    - **facility_id**: 施設ID
    - **session_id**: セッションID
    
    セッション統合トークン（4桁英数字）を生成し、返却します
    """
    try:
        token = await session_token_service.generate_token(
            facility_id=request.facility_id,
            primary_session_id=request.session_id,
            db=db
        )
        
        # トークン情報を取得
        token_obj = await session_token_service.get_token_by_session_id(
            session_id=request.session_id,
            db=db
        )
        
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve generated token"
            )
        
        return SessionTokenResponse(
            token=token_obj.token,
            primary_session_id=token_obj.primary_session_id,
            linked_session_ids=token_obj.linked_session_ids or [],
            expires_at=token_obj.expires_at,
            created_at=token_obj.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {str(e)}"
        )


@router.get("/session/{session_id}/token", response_model=SessionTokenResponse)
async def get_token_by_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    セッションIDから既存のトークンを取得
    
    - **session_id**: セッションID
    
    セッションIDに関連する既存のトークンを返却します
    """
    token_obj = await session_token_service.get_token_by_session_id(
        session_id=session_id,
        db=db
    )
    
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found for this session"
        )
    
    return SessionTokenResponse(
        token=token_obj.token,
        primary_session_id=token_obj.primary_session_id,
        linked_session_ids=token_obj.linked_session_ids or [],
        expires_at=token_obj.expires_at,
        created_at=token_obj.created_at
    )

