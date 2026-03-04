"""
広告API（Freeプラン ゲスト画面固定フッター用）
施設が Free のときのみ広告一覧を返す。他プランは空配列。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.ad import Ad
from app.models.facility import Facility
from app.schemas.ad import AdItem, AdListResponse
from typing import Optional

router = APIRouter(prefix="/ads", tags=["ads"])


@router.get("", response_model=AdListResponse)
async def get_ads(
    facility_slug: Optional[str] = Query(None, description="施設slug（Freeプラン時のみ広告を返す）"),
    facility_id: Optional[int] = Query(None, description="施設ID（slugの代わりに指定可）"),
    db: AsyncSession = Depends(get_db),
):
    """
    広告一覧取得（公開API・認証不要）
    facility_slug または facility_id で指定した施設が Free プランの場合のみ広告を返す。
    Mini 以上は空配列を返す。
    """
    facility = None
    if facility_slug:
        r = await db.execute(select(Facility).where(Facility.slug == facility_slug, Facility.is_active == True))
        facility = r.scalar_one_or_none()
    elif facility_id is not None:
        r = await db.execute(select(Facility).where(Facility.id == facility_id, Facility.is_active == True))
        facility = r.scalar_one_or_none()

    if facility is None:
        return AdListResponse(ads=[])

    if (facility.plan_type or "Free") != "Free":
        return AdListResponse(ads=[])

    r = await db.execute(
        select(Ad).where(Ad.active == True).order_by(Ad.priority.asc(), Ad.id.asc())
    )
    rows = r.scalars().all()
    return AdListResponse(
        ads=[AdItem(id=row.id, title=row.title, description=row.description, url=row.url, affiliate_url=row.affiliate_url, priority=row.priority) for row in rows]
    )
