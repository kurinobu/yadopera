"""
エスカレーション管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.escalation import (
    EscalationResponse,
    EscalationListResponse,
    UnresolvedQuestionResponse
)
from app.services.escalation_service import EscalationService
from app.models.escalation import Escalation

router = APIRouter(prefix="/admin/escalations", tags=["admin", "escalations"])


@router.get("", response_model=EscalationListResponse)
async def get_escalations(
    resolved: Optional[bool] = Query(None, description="解決済みを含めるか（None: すべて、True: 解決済みのみ、False: 未解決のみ）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    エスカレーション一覧取得
    
    - **resolved**: 解決済みを含めるか（None: すべて、True: 解決済みのみ、False: 未解決のみ）
    
    JWT認証必須。現在のユーザーが所属する施設のエスカレーションを返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # エスカレーションサービスでエスカレーション一覧取得
        escalation_service = EscalationService()
        
        # クエリ構築
        from sqlalchemy import select
        query = select(Escalation).where(Escalation.facility_id == facility_id)
        
        # resolvedパラメータでフィルタ
        if resolved is True:
            query = query.where(Escalation.resolved_at.isnot(None))
        elif resolved is False:
            query = query.where(Escalation.resolved_at.is_(None))
        
        query = query.order_by(Escalation.created_at.desc())
        
        result = await db.execute(query)
        escalations = result.scalars().all()
        
        # 統計情報を計算
        all_result = await db.execute(
            select(Escalation).where(Escalation.facility_id == facility_id)
        )
        all_escalations = all_result.scalars().all()
        unresolved_count = sum(1 for e in all_escalations if e.resolved_at is None)
        
        # レスポンスに変換
        escalation_responses = [
            EscalationResponse(
                id=escalation.id,
                facility_id=escalation.facility_id,
                conversation_id=escalation.conversation_id,
                trigger_type=escalation.trigger_type,
                ai_confidence=escalation.ai_confidence,
                escalation_mode=escalation.escalation_mode,
                notified_at=escalation.notified_at,
                notification_channels=escalation.notification_channels or [],
                resolved_at=escalation.resolved_at,
                resolved_by=escalation.resolved_by,
                resolution_notes=escalation.resolution_notes,
                created_at=escalation.created_at
            )
            for escalation in escalations
        ]
        
        return EscalationListResponse(
            escalations=escalation_responses,
            total=len(escalation_responses),
            unresolved=unresolved_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving escalations: {str(e)}"
        )


@router.get("/unresolved-questions", response_model=List[UnresolvedQuestionResponse])
async def get_unresolved_questions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    未解決質問リスト取得
    
    JWT認証必須。現在のユーザーが所属する施設の未解決質問を返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # エスカレーションサービスで未解決質問を取得
        escalation_service = EscalationService()
        unresolved_questions = await escalation_service.get_unresolved_questions(
            facility_id=facility_id,
            db=db
        )
        
        return unresolved_questions
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving unresolved questions: {str(e)}"
        )


