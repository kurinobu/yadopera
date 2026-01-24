"""
統計取得APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, cast, Date
from sqlalchemy.orm import selectinload
from typing import Dict
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.api.deps import get_current_developer
from app.models.facility import Facility
from app.models.faq import FAQ
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.escalation import Escalation
from app.models.error_log import ErrorLog
from app.models.user import User
from app.schemas.developer import SystemOverviewResponse, Errors24hResponse, FacilityListResponse, FacilitySummaryResponse

router = APIRouter()


@router.get("/overview", response_model=SystemOverviewResponse)
async def get_system_overview(
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db)
):
    """
    システム全体概要取得
    
    開発者認証必須。
    """
    try:
        # 施設数（非同期）
        facilities_result = await db.execute(select(func.count(Facility.id)))
        total_facilities = facilities_result.scalar() or 0
        
        active_facilities_result = await db.execute(
            select(func.count(Facility.id)).where(Facility.is_active == True)
        )
        active_facilities = active_facilities_result.scalar() or 0
        
        # FAQ数（非同期）
        faqs_result = await db.execute(select(func.count(FAQ.id)))
        total_faqs = faqs_result.scalar() or 0
        
        # エラー数（過去24時間、非同期）
        yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
        errors_result = await db.execute(
            select(
                ErrorLog.error_level,
                func.count(ErrorLog.id).label('count')
            )
            .where(ErrorLog.created_at >= yesterday)
            .group_by(ErrorLog.error_level)
        )
        errors_dict: Dict[str, int] = {}
        for row in errors_result.all():
            errors_dict[row.error_level] = row.count
        
        errors_24h = Errors24hResponse(
            critical=errors_dict.get("critical", 0),
            error=errors_dict.get("error", 0),
            warning=errors_dict.get("warning", 0)
        )
        
        # チャット数（過去7日、非同期）
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        chats_result = await db.execute(
            select(func.count(Message.id))
            .where(
                Message.created_at >= week_ago,
                Message.role == 'user'  # ユーザーメッセージのみカウント
            )
        )
        chats_7d = chats_result.scalar() or 0
        
        # エスカレーション数（過去7日、非同期）
        escalations_result = await db.execute(
            select(func.count(Escalation.id))
            .where(Escalation.created_at >= week_ago)
        )
        escalations_7d = escalations_result.scalar() or 0
        
        return SystemOverviewResponse(
            total_facilities=total_facilities,
            active_facilities=active_facilities,
            total_faqs=total_faqs,
            errors_24h=errors_24h,
            chats_7d=chats_7d,
            escalations_7d=escalations_7d
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system overview: {str(e)}"
        )


@router.get("/facilities", response_model=FacilityListResponse)
async def get_facilities_summary(
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db)
):
    """
    全施設一覧と基本統計取得
    
    開発者認証必須。
    """
    try:
        # サブクエリでFAQ数を取得（非同期）
        faq_count_subq = (
            select(
                FAQ.facility_id,
                func.count(FAQ.id).label('faq_count')
            )
            .group_by(FAQ.facility_id)
            .subquery()
        )
        
        # サブクエリでチャット数を取得（過去7日、非同期）
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        chat_count_subq = (
            select(
                Conversation.facility_id,
                func.count(Message.id).label('chat_count')
            )
            .join(Message, Conversation.id == Message.conversation_id)
            .where(
                Message.created_at >= week_ago,
                Message.role == 'user'
            )
            .group_by(Conversation.facility_id)
            .subquery()
        )
        
        # サブクエリでエラー数を取得（過去7日、非同期）
        error_count_subq = (
            select(
                ErrorLog.facility_id,
                func.count(ErrorLog.id).label('error_count')
            )
            .where(ErrorLog.created_at >= week_ago)
            .group_by(ErrorLog.facility_id)
            .subquery()
        )
        
        # サブクエリで最終ログイン時刻を取得（非同期）
        last_login_subq = (
            select(
                User.facility_id,
                func.max(User.last_login_at).label('last_login')
            )
            .where(User.last_login_at.isnot(None))
            .group_by(User.facility_id)
            .subquery()
        )
        
        # メインクエリ（非同期）
        facilities_result = await db.execute(
            select(
                Facility,
                func.coalesce(faq_count_subq.c.faq_count, 0).label('faq_count'),
                func.coalesce(chat_count_subq.c.chat_count, 0).label('chat_count'),
                func.coalesce(error_count_subq.c.error_count, 0).label('error_count'),
                last_login_subq.c.last_login.label('last_login')
            )
            .outerjoin(faq_count_subq, Facility.id == faq_count_subq.c.facility_id)
            .outerjoin(chat_count_subq, Facility.id == chat_count_subq.c.facility_id)
            .outerjoin(error_count_subq, Facility.id == error_count_subq.c.facility_id)
            .outerjoin(last_login_subq, Facility.id == last_login_subq.c.facility_id)
            .order_by(Facility.id)
        )
        facilities_data = facilities_result.all()
        
        # レスポンス構築
        facility_summaries = []
        for row in facilities_data:
            facility = row[0]  # Facilityオブジェクト
            facility_summaries.append(
                FacilitySummaryResponse(
                    id=facility.id,
                    name=facility.name,
                    is_active=facility.is_active,
                    faq_count=row.faq_count or 0,
                    chats_7d=row.chat_count or 0,
                    errors_7d=row.error_count or 0,
                    last_admin_login=row.last_login
                )
            )
        
        return FacilityListResponse(facilities=facility_summaries)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving facilities summary: {str(e)}"
        )

