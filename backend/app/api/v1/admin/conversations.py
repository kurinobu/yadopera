"""
管理画面 会話API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.chat import MessageResponse, StaffReplyRequest, StaffReplyResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/admin/conversations", tags=["admin", "conversations"])


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
