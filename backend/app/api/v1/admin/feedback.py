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


