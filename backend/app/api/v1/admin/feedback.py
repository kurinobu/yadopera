"""
フィードバック管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.dashboard import LowRatedAnswer
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/admin/feedback", tags=["admin", "feedback"])


@router.get("/negative", response_model=List[LowRatedAnswer])
async def get_negative_feedbacks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    低評価回答リスト取得（2回以上低評価がついた回答）
    
    JWT認証必須。現在のユーザーが所属する施設の低評価回答リストを返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # フィードバックサービスで低評価回答リスト取得
        feedback_service = FeedbackService(db)
        low_rated_answers = await feedback_service.get_negative_feedbacks(
            facility_id=facility_id
        )
        
        return low_rated_answers
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving negative feedbacks: {str(e)}"
        )


@router.post("/{message_id}/ignore")
async def ignore_negative_feedback(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    低評価回答を無視
    
    JWT認証必須。指定されたメッセージIDの低評価回答を無視します。
    無視された低評価回答は、低評価回答リストから除外されます。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # フィードバックサービスで低評価回答を無視
        feedback_service = FeedbackService(db)
        await feedback_service.ignore_negative_feedback(
            message_id=message_id,
            facility_id=facility_id,
            user_id=current_user.id
        )
        
        return {"message": "Negative feedback ignored successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ignoring negative feedback: {str(e)}"
        )


