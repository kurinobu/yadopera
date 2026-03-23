"""
施設APIエンドポイント
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.facility import FacilityPublicResponse
from app.schemas.lead import LeadEntryRequest, LeadEntryResponse
from app.services.facility_service import FacilityService
from app.services.lead_service import LeadService
from typing import Optional

router = APIRouter(prefix="/facility", tags=["facility"])


@router.get("/{slug}", response_model=dict)
async def get_facility(
    slug: str,
    location: Optional[str] = Query(None, description="QRコード設置場所（entrance/room/kitchen/lounge）"),
    language: Optional[str] = Query("en", description="言語コード（ja, en, zh-TW, fr, ko等）"),
    db: AsyncSession = Depends(get_db)
):
    """
    施設情報取得（公開API）
    
    - **slug**: 施設slug（URL用識別子）
    - **location**: QRコード設置場所（オプション）
    - **language**: 言語コード（オプション、デフォルト: "en"）
    
    施設情報とよくある質問TOP3を返却します
    """
    facility_info = await FacilityService.get_facility_public_info(db, slug, language)
    
    # レスポンス形式（アーキテクチャ設計書に合わせる）
    facility_dict = {
        "id": facility_info.id,
        "name": facility_info.name,
        "slug": facility_info.slug,
        "email": facility_info.email,
        "phone": facility_info.phone,
        "check_in_time": facility_info.check_in_time,
        "check_out_time": facility_info.check_out_time,
        "wifi_ssid": facility_info.wifi_ssid,
        "plan_type": facility_info.plan_type,
        "available_languages": facility_info.available_languages,
    }
    if facility_info.coupon is not None:
        facility_dict["coupon"] = facility_info.coupon.dict()
    return {
        "facility": facility_dict,
        "top_questions": facility_info.top_questions,
    }


@router.post("/{slug}/lead", response_model=LeadEntryResponse)
async def create_lead_entry(
    slug: str,
    body: LeadEntryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    リードエントリー（クーポン取得）
    施設のクーポンが有効な場合、ゲスト名・メールアドレスを登録しクーポン送付メールを送信する。
    """
    facility = await FacilityService.get_facility_by_slug(db, slug)
    if facility is None:
        try:
            fid = int(slug)
            from sqlalchemy import select
            from app.models.facility import Facility
            r = await db.execute(select(Facility).where(Facility.id == fid, Facility.is_active == True))
            facility = r.scalar_one_or_none()
        except ValueError:
            facility = None
    if facility is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found")
    try:
        await LeadService.create_lead_and_send_coupon(
            db, facility, body.guest_name, body.email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return LeadEntryResponse(success=True, message="クーポンを送信しました。")


