"""
スタッフ不在時間帯対応キューAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.overnight_queue import OvernightQueue
from app.models.escalation import Escalation
from app.models.conversation import Conversation
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
    スタッフ不在時間帯対応キュー取得
    
    - **include_resolved**: 解決済みを含めるか（デフォルト: False）
    
    JWT認証必須。現在のユーザーが所属する施設のスタッフ不在時間帯対応キューを返却します。
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
        
        # 会話から言語を取得（JOINを使用して効率的に取得）
        queue_ids = [q.id for q in queues]
        queue_language_map = {}
        if queue_ids:
            result = await db.execute(
                select(OvernightQueue, Escalation, Conversation)
                .join(Escalation, OvernightQueue.escalation_id == Escalation.id)
                .join(Conversation, Escalation.conversation_id == Conversation.id)
                .where(OvernightQueue.id.in_(queue_ids))
            )
            queue_data = result.all()
            queue_language_map = {
                queue.id: conversation.guest_language or "en"
                for queue, escalation, conversation in queue_data
            }
        
        # レスポンスに変換
        queue_responses = [
            OvernightQueueResponse(
                id=queue.id,
                facility_id=queue.facility_id,
                escalation_id=queue.escalation_id,
                guest_message=queue.guest_message,
                language=queue_language_map.get(queue.id, "en"),  # 会話から取得した言語を使用
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
            total=len(all_queues),  # 全キュー数（未解決+解決済み）
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
    
    スタッフ不在時間帯の終了時刻に設定された一括通知処理を手動で実行します。
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


@router.put("/{queue_id}/resolve", response_model=OvernightQueueResponse)
async def resolve_queue_item(
    queue_id: int = Path(..., description="キューID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    スタッフ不在時間帯対応キューアイテムを対応済みにする
    
    - **queue_id**: キューID
    
    JWT認証必須。現在のユーザーが所属する施設のスタッフ不在時間帯対応キューを対応済みとしてマークします。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # 夜間対応キューサービスで対応済みにする
        queue_service = OvernightQueueService()
        queue = await queue_service.resolve_queue_item(
            queue_id=queue_id,
            user_id=current_user.id,
            facility_id=facility_id,
            db=db
        )
        
        # 会話から言語を取得
        language = "en"
        if queue.escalation_id:
            result = await db.execute(
                select(Escalation, Conversation)
                .join(Conversation, Escalation.conversation_id == Conversation.id)
                .where(Escalation.id == queue.escalation_id)
            )
            escalation_data = result.first()
            if escalation_data:
                _, conversation = escalation_data
                language = conversation.guest_language or "en"
        
        # レスポンスに変換
        return OvernightQueueResponse(
            id=queue.id,
            facility_id=queue.facility_id,
            escalation_id=queue.escalation_id,
            guest_message=queue.guest_message,
            language=language,
            scheduled_notify_at=queue.scheduled_notify_at,
            notified_at=queue.notified_at,
            resolved_at=queue.resolved_at,
            resolved_by=queue.resolved_by,
            created_at=queue.created_at
        )
    
    except ValueError as e:
        # キューが見つからない、または施設IDが一致しない場合
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving overnight queue: {str(e)}"
        )

