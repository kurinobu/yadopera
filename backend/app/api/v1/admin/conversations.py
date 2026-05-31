"""
管理画面 会話API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from sqlalchemy import select

from app.models.conversation import Conversation
from app.schemas.chat import ChatHistoryResponse, MessageResponse, StaffReplyRequest, StaffReplyResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/admin/conversations", tags=["admin", "conversations"])


@router.get("/{session_id}", response_model=ChatHistoryResponse)
async def get_admin_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理画面用会話履歴取得（JWT の施設スコープで認可、24h 期限なし）。
    """
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility",
        )

    result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: session_id={session_id}",
        )
    if conversation.facility_id != facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This conversation belongs to another facility. "
                "Please sign in with the administrator account for the facility "
                "that received the escalation notification."
            ),
        )

    chat_service = ChatService(db)
    history = await chat_service.get_conversation_history(
        session_id=session_id,
        facility_id=facility_id,
    )
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: session_id={session_id}",
        )
    return history


@router.post("/{session_id}/reply", response_model=StaffReplyResponse, status_code=status.HTTP_201_CREATED)
async def post_staff_reply(
    session_id: str,
    request: StaffReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    管理者がゲスト会話へ手動返信（role=staff）を投稿する。
    """
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility",
        )

    try:
        chat_service = ChatService(db)
        saved = await chat_service.create_staff_reply(
            session_id=session_id,
            facility_id=facility_id,
            content=request.content,
        )
        return StaffReplyResponse(
            success=True,
            session_id=session_id,
            message=MessageResponse(
                id=saved.id,
                role=saved.role,
                content=saved.content,
                ai_confidence=saved.ai_confidence,
                matched_faq_ids=saved.matched_faq_ids,
                response_time_ms=saved.response_time_ms,
                created_at=saved.created_at,
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating staff reply: {e}",
        )
