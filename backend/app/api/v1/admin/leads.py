"""
リード一覧・CSVエクスポートAPI（管理画面用）
"""

import csv
import io
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.lead_service import LeadService
from app.schemas.lead import LeadListResponse

router = APIRouter(prefix="/admin/leads", tags=["admin", "leads"])


@router.get("", response_model=LeadListResponse)
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    リード一覧取得（自施設のみ、ページネーション）
    """
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility"
        )
    return await LeadService.get_leads(db, facility_id, skip=skip, limit=limit)


@router.get("/export")
async def export_leads_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    リード一覧をCSVでダウンロード（自施設のみ）
    """
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility"
        )
    result = await LeadService.get_leads(db, facility_id, skip=0, limit=10000)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "guest_name", "email", "coupon_sent_at", "created_at"])
    for lead in result.leads:
        writer.writerow([
            lead.id,
            lead.guest_name or "",
            lead.email,
            lead.coupon_sent_at.isoformat() if lead.coupon_sent_at else "",
            lead.created_at.isoformat() if lead.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )