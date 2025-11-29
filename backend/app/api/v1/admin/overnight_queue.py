"""
夜間対応キューAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.overnight_queue import (
    OvernightQueueListResponse,
    OvernightQueueResponse,
    ProcessNotificationsResponse
)
from app.services.overnight_queue_service import OvernightQueueService

router = APIRouter(prefix="/admin/overnight-queue", tags=["admin", "overnight-queue"])


@router.get("", response_model=OvernightQueueListResponse)
async def get_overnight_queue(
    include_resolved: bool = Query(False, description="解決済みを含めるか"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    夜間対応キュー取得
    
    - **include_resolved**: 解決済みを含めるか（デフォルト: False）
    
    JWT認証必須。現在のユーザーが所属する施設の夜間対応キューを返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # 夜間対応キューサービスでキュー取得
        queue_service = OvernightQueueService()
        queues = await queue_service.get_overnight_queue(
            facility_id=facility_id,
            db=db,
            include_resolved=include_resolved
        )
        
        # 統計情報を計算
        all_queues = await queue_service.get_overnight_queue(
            facility_id=facility_id,
            db=db,
            include_resolved=True
        )
        pending_count = sum(1 for q in all_queues if q.resolved_at is None)
        resolved_count = sum(1 for q in all_queues if q.resolved_at is not None)
        
        # レスポンスに変換
        queue_responses = [
            OvernightQueueResponse(
                id=queue.id,
                facility_id=queue.facility_id,
                escalation_id=queue.escalation_id,
                guest_message=queue.guest_message,
                scheduled_notify_at=queue.scheduled_notify_at,
                notified_at=queue.notified_at,
                resolved_at=queue.resolved_at,
                resolved_by=queue.resolved_by,
                created_at=queue.created_at
            )
            for queue in queues
        ]
        
        return OvernightQueueListResponse(
            queues=queue_responses,
            total=len(queue_responses),
            pending_count=pending_count,
            resolved_count=resolved_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving overnight queue: {str(e)}"
        )


@router.post("/process", response_model=ProcessNotificationsResponse)
async def process_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    手動実行処理（MVP期間中）
    
    翌朝8:00の一括通知処理を手動で実行します。
    MVP期間中はこのエンドポイントを使用して通知処理を実行します。
    
    JWT認証必須。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # 夜間対応キューサービスで通知処理実行
        queue_service = OvernightQueueService()
        processed_queues = await queue_service.process_scheduled_notifications(
            db=db,
            facility_id=facility_id
        )
        
        return ProcessNotificationsResponse(
            processed_count=len(processed_queues),
            total_count=len(processed_queues)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing notifications: {str(e)}"
        )

