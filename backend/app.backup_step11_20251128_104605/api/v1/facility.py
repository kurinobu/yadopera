"""
施設APIエンドポイント
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.facility import FacilityPublicResponse
from app.services.facility_service import FacilityService
from typing import Optional

router = APIRouter(prefix="/facility", tags=["facility"])


@router.get("/{slug}", response_model=dict)
async def get_facility(
    slug: str,
    location: Optional[str] = Query(None, description="QRコード設置場所（entrance/room/kitchen/lounge）"),
    db: AsyncSession = Depends(get_db)
):
    """
    施設情報取得（公開API）
    
    - **slug**: 施設slug（URL用識別子）
    - **location**: QRコード設置場所（オプション）
    
    施設情報とよくある質問TOP3を返却します
    """
    facility_info = await FacilityService.get_facility_public_info(db, slug)
    
    # レスポンス形式（アーキテクチャ設計書に合わせる）
    return {
        "facility": {
            "id": facility_info.id,
            "name": facility_info.name,
            "slug": facility_info.slug,
            "email": facility_info.email,
            "phone": facility_info.phone,
            "check_in_time": facility_info.check_in_time,
            "check_out_time": facility_info.check_out_time,
            "wifi_ssid": facility_info.wifi_ssid,
        },
        "top_questions": facility_info.top_questions,
    }

