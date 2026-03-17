"""
統計取得APIエンドポイント
"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, cast, Date
from sqlalchemy.orm import selectinload
from typing import Dict
from datetime import datetime, timedelta, timezone
import pytz
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

def _get_current_month_range_utc() -> tuple[datetime, datetime]:
    """
    当月（暦月 JST）の開始・終了を UTC で返す。
    """
    jst = pytz.timezone("Asia/Tokyo")
    now_jst = datetime.now(jst)
    month_start_jst = jst.localize(datetime(now_jst.year, now_jst.month, 1, 0, 0, 0))

    if now_jst.month == 12:
        next_month_start_naive = datetime(now_jst.year + 1, 1, 1, 0, 0, 0)
    else:
        next_month_start_naive = datetime(now_jst.year, now_jst.month + 1, 1, 0, 0, 0)

    month_end_jst = jst.localize(next_month_start_naive) - timedelta(microseconds=1)
    return (
        month_start_jst.astimezone(timezone.utc),
        month_end_jst.astimezone(timezone.utc),
    )


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

        # 当月（暦月 JST）の範囲を UTC に変換
        month_start_utc, month_end_utc = _get_current_month_range_utc()

        # 有料施設数（plan_type != 'Free'）
        paid_result = await db.execute(
            select(func.count(Facility.id)).where(Facility.plan_type != "Free")
        )
        paid_facilities_count = paid_result.scalar() or 0

        # 今月の総質問数（Message.role='user'、当月）
        questions_result = await db.execute(
            select(func.count(Message.id))
            .where(Message.role == "user")
            .where(Message.created_at >= month_start_utc)
            .where(Message.created_at <= month_end_utc)
        )
        questions_current_month = questions_result.scalar() or 0

        # 今月の新規登録数（Facility.created_at が当月）
        new_reg_result = await db.execute(
            select(func.count(Facility.id))
            .where(Facility.created_at >= month_start_utc)
            .where(Facility.created_at <= month_end_utc)
        )
        new_registrations_current_month = new_reg_result.scalar() or 0

        # 今月の新規有料数（当月登録かつ plan_type != 'Free'）
        new_paid_result = await db.execute(
            select(func.count(Facility.id))
            .where(Facility.created_at >= month_start_utc)
            .where(Facility.created_at <= month_end_utc)
            .where(Facility.plan_type != "Free")
        )
        new_paid_current_month = new_paid_result.scalar() or 0

        # 解約予定施設数（cancel_at_period_end == True）
        cancel_result = await db.execute(
            select(func.count(Facility.id)).where(Facility.cancel_at_period_end == True)
        )
        cancel_at_period_end_count = cancel_result.scalar() or 0

        return SystemOverviewResponse(
            total_facilities=total_facilities,
            active_facilities=active_facilities,
            total_faqs=total_faqs,
            errors_24h=errors_24h,
            chats_7d=chats_7d,
            escalations_7d=escalations_7d,
            paid_facilities_count=paid_facilities_count,
            questions_current_month=questions_current_month,
            new_registrations_current_month=new_registrations_current_month,
            new_paid_current_month=new_paid_current_month,
            cancel_at_period_end_count=cancel_at_period_end_count,
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
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        # 当月（暦月 JST）の範囲を UTC に変換（施設別今月質問数用）
        month_start_utc, month_end_utc = _get_current_month_range_utc()

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

        # サブクエリで施設別・当月の質問数を取得
        questions_month_subq = (
            select(
                Conversation.facility_id,
                func.count(Message.id).label('questions_count')
            )
            .join(Message, Conversation.id == Message.conversation_id)
            .where(Message.role == "user")
            .where(Message.created_at >= month_start_utc)
            .where(Message.created_at <= month_end_utc)
            .group_by(Conversation.facility_id)
            .subquery()
        )

        # サブクエリで施設別・過去7日のエスカレーション数を取得
        escalations_7d_subq = (
            select(
                Escalation.facility_id,
                func.count(Escalation.id).label('escalations_count')
            )
            .where(Escalation.created_at >= week_ago)
            .group_by(Escalation.facility_id)
            .subquery()
        )
        
        # メインクエリ（非同期）
        facilities_result = await db.execute(
            select(
                Facility,
                func.coalesce(faq_count_subq.c.faq_count, 0).label('faq_count'),
                func.coalesce(chat_count_subq.c.chat_count, 0).label('chat_count'),
                func.coalesce(error_count_subq.c.error_count, 0).label('error_count'),
                last_login_subq.c.last_login.label('last_login'),
                func.coalesce(questions_month_subq.c.questions_count, 0).label('questions_current_month'),
                func.coalesce(escalations_7d_subq.c.escalations_count, 0).label('escalations_7d'),
            )
            .outerjoin(faq_count_subq, Facility.id == faq_count_subq.c.facility_id)
            .outerjoin(chat_count_subq, Facility.id == chat_count_subq.c.facility_id)
            .outerjoin(error_count_subq, Facility.id == error_count_subq.c.facility_id)
            .outerjoin(last_login_subq, Facility.id == last_login_subq.c.facility_id)
            .outerjoin(questions_month_subq, Facility.id == questions_month_subq.c.facility_id)
            .outerjoin(escalations_7d_subq, Facility.id == escalations_7d_subq.c.facility_id)
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
                    email=facility.email or "",
                    is_active=facility.is_active,
                    plan_type=facility.plan_type or "Free",
                    faq_count=row.faq_count or 0,
                    chats_7d=row.chat_count or 0,
                    errors_7d=row.error_count or 0,
                    last_admin_login=row.last_login,
                    created_at=facility.created_at,
                    questions_current_month=row.questions_current_month or 0,
                    escalations_7d=row.escalations_7d or 0,
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


@router.get("/facilities/export")
async def export_facilities_csv(
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db),
):
    """
    施設ID・施設名・メールアドレス一覧をCSVでダウンロード（開発者認証必須）
    """
    try:
        facilities_result = await db.execute(
            select(Facility).order_by(Facility.id)
        )
        facilities_data = facilities_result.all()

        output = io.StringIO()
        # UTF-8 BOM（Excel等での文字化け防止）
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["施設ID", "施設名", "メールアドレス"])
        for row in facilities_data:
            facility = row[0]
            writer.writerow([facility.id, facility.name or "", facility.email or ""])
        output.seek(0)

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = f"facilities_{date_str}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting facilities CSV: {str(e)}",
        )

