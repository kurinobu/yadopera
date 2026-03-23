"""
エラーログAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.api.deps import get_current_developer
from app.models.error_log import ErrorLog
from app.models.facility import Facility
from app.models.user import User
from app.schemas.developer import ErrorLogListResponse, ErrorLogResponse, ErrorLogDetailResponse, PaginationInfo

router = APIRouter()


@router.get("/list", response_model=ErrorLogListResponse)
async def get_error_logs(
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(50, ge=1, le=100, description="1ページあたりの件数"),
    level: Optional[str] = Query(None, description="エラーレベル（critical, error, warning）"),
    facility_id: Optional[int] = Query(None, description="施設ID"),
    start_date: Optional[datetime] = Query(None, description="開始日時"),
    end_date: Optional[datetime] = Query(None, description="終了日時"),
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db)
):
    """
    エラーログ一覧取得
    
    - **page**: ページ番号（1以上）
    - **per_page**: 1ページあたりの件数（1-100）
    - **level**: エラーレベルフィルタ（オプション）
    - **facility_id**: 施設IDフィルタ（オプション）
    - **start_date**: 開始日時フィルタ（オプション）
    - **end_date**: 終了日時フィルタ（オプション）
    
    開発者認証必須。
    """
    try:
        # ベースクエリ構築
        query = select(ErrorLog).order_by(desc(ErrorLog.created_at))
        
        # フィルタリング条件を追加
        if level:
            query = query.where(ErrorLog.error_level == level)
        if facility_id:
            query = query.where(ErrorLog.facility_id == facility_id)
        if start_date:
            # timezone awareに変換
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            query = query.where(ErrorLog.created_at >= start_date)
        if end_date:
            # timezone awareに変換
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            query = query.where(ErrorLog.created_at <= end_date)
        
        # 総件数取得（非同期）
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # ページネーション適用（非同期）
        offset = (page - 1) * per_page
        errors_result = await db.execute(
            query.options(selectinload(ErrorLog.facility)).offset(offset).limit(per_page)
        )
        errors = errors_result.scalars().all()
        
        # レスポンス構築
        error_responses = []
        for error in errors:
            error_responses.append(
                ErrorLogResponse(
                    id=error.id,
                    level=error.error_level,
                    code=error.error_code,
                    message=error.error_message,
                    request_path=error.request_path,
                    facility_name=error.facility.name if error.facility else None,
                    created_at=error.created_at
                )
            )
        
        # 総ページ数計算
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        
        return ErrorLogListResponse(
            errors=error_responses,
            pagination=PaginationInfo(
                page=page,
                per_page=per_page,
                total=total,
                total_pages=total_pages
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving error logs: {str(e)}"
        )


@router.get("/{error_id}", response_model=ErrorLogDetailResponse)
async def get_error_log_detail(
    error_id: int,
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db)
):
    """
    エラーログ詳細取得
    
    - **error_id**: エラーログID
    
    開発者認証必須。
    """
    try:
        # エラーログ取得（リレーションシップも含める）
        result = await db.execute(
            select(ErrorLog)
            .options(selectinload(ErrorLog.facility), selectinload(ErrorLog.user))
            .where(ErrorLog.id == error_id)
        )
        error = result.scalar_one_or_none()
        
        if error is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error log not found"
            )
        
        # レスポンス構築
        facility_data = None
        if error.facility:
            facility_data = {
                "id": error.facility.id,
                "name": error.facility.name
            }
        
        user_data = None
        if error.user:
            user_data = {
                "id": error.user.id,
                "email": error.user.email
            }
        
        # IPアドレスを文字列に変換
        ip_address_str = None
        if error.ip_address:
            ip_address_str = str(error.ip_address)
        
        return ErrorLogDetailResponse(
            id=error.id,
            level=error.error_level,
            code=error.error_code,
            message=error.error_message,
            stack_trace=error.stack_trace,
            request_path=error.request_path,
            request_method=error.request_method,
            facility=facility_data,
            user=user_data,
            ip_address=ip_address_str,
            user_agent=error.user_agent,
            created_at=error.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving error log: {str(e)}"
        )

