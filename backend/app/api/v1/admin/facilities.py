"""
施設管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.facility import Facility
from app.schemas.facility import FacilityResponse

router = APIRouter(prefix="/admin/facilities", tags=["admin", "facilities"])


@router.get("", response_model=List[FacilityResponse])
async def get_facilities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    施設一覧取得
    
    JWT認証必須。現在のユーザーが所属する施設の情報を返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # 施設情報を取得
        result = await db.execute(
            select(Facility).where(Facility.id == facility_id)
        )
        facility = result.scalar_one_or_none()
        
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )
        
        return [FacilityResponse.from_orm(facility)]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve facilities: {str(e)}"
        )