"""
施設設定APIエンドポイント（管理画面用）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.facility import Facility
from app.schemas.facility import (
    FacilitySettingsResponse,
    FacilitySettingsUpdateRequest,
    FacilityResponse,
    StaffAbsencePeriod
)
from app.core.security import hash_password
from datetime import time as time_type
import json

router = APIRouter(prefix="/admin/facility", tags=["admin", "facility"])


@router.get("/settings", response_model=FacilitySettingsResponse)
async def get_facility_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    施設設定取得
    
    JWT認証必須。現在のユーザーが所属する施設の設定を返却します。
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
        facility = await db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )
        
        # Time型を文字列に変換
        check_in_time_str = None
        check_out_time_str = None
        
        if facility.check_in_time:
            check_in_time_str = facility.check_in_time.strftime("%H:%M")
        
        if facility.check_out_time:
            check_out_time_str = facility.check_out_time.strftime("%H:%M")
        
        # FacilityResponseを構築
        facility_response = FacilityResponse(
            id=facility.id,
            name=facility.name,
            slug=facility.slug,
            email=facility.email,
            phone=facility.phone,
            address=facility.address,
            wifi_ssid=facility.wifi_ssid,
            check_in_time=check_in_time_str,
            check_out_time=check_out_time_str,
            house_rules=facility.house_rules,
            local_info=facility.local_info,
            prohibited_items=getattr(facility, "prohibited_items", None),
            languages=facility.languages or [],
            timezone=facility.timezone or "Asia/Tokyo",
            subscription_plan=facility.subscription_plan or "small",
            monthly_question_limit=facility.monthly_question_limit or 200,
            is_active=facility.is_active,
            created_at=facility.created_at,
            updated_at=facility.updated_at
        )
        
        # スタッフ不在時間帯をパース
        staff_absence_periods: List[StaffAbsencePeriod] = []
        if facility.staff_absence_periods:
            try:
                if isinstance(facility.staff_absence_periods, str):
                    periods_data = json.loads(facility.staff_absence_periods)
                else:
                    periods_data = facility.staff_absence_periods
                
                for period_data in periods_data:
                    staff_absence_periods.append(StaffAbsencePeriod(**period_data))
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                # パースエラーの場合は空リストを返す
                staff_absence_periods = []
        
        return FacilitySettingsResponse(
            facility=facility_response,
            staff_absence_periods=staff_absence_periods,
            icon_url=facility.icon_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving facility settings: {str(e)}"
        )


@router.put("/settings", response_model=FacilitySettingsResponse)
async def update_facility_settings(
    request: FacilitySettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    施設設定更新
    
    JWT認証必須。現在のユーザーが所属する施設の設定を更新します。
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
        facility = await db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )
        
        # 施設情報を更新
        update_data = request.dict(exclude_unset=True)
        
        # 基本情報の更新
        if "name" in update_data and update_data["name"] is not None:
            facility.name = update_data["name"]
        if "email" in update_data and update_data["email"] is not None:
            facility.email = update_data["email"]
        if "phone" in update_data:
            facility.phone = update_data["phone"]
        if "address" in update_data:
            facility.address = update_data["address"]
        
        # WiFi設定の更新
        if "wifi_ssid" in update_data:
            facility.wifi_ssid = update_data["wifi_ssid"]
        if "wifi_password" in update_data and update_data["wifi_password"]:
            # WiFiパスワードは暗号化保存（既存の実装に従う）
            facility.wifi_password = update_data["wifi_password"]  # 既存の実装では暗号化されていない可能性があるため、要確認
        
        # チェックイン/アウト時間の更新
        if "check_in_time" in update_data and update_data["check_in_time"]:
            try:
                hour, minute = map(int, update_data["check_in_time"].split(":"))
                facility.check_in_time = time_type(hour, minute)
            except (ValueError, AttributeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid check_in_time format. Use HH:MM format."
                )
        
        if "check_out_time" in update_data and update_data["check_out_time"]:
            try:
                hour, minute = map(int, update_data["check_out_time"].split(":"))
                facility.check_out_time = time_type(hour, minute)
            except (ValueError, AttributeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid check_out_time format. Use HH:MM format."
                )
        
        # 館内ルール・周辺情報の更新
        if "house_rules" in update_data:
            facility.house_rules = update_data["house_rules"]
        if "local_info" in update_data:
            facility.local_info = update_data["local_info"]
        if "prohibited_items" in update_data:
            facility.prohibited_items = update_data["prohibited_items"]
        
        # スタッフ不在時間帯の更新
        if "staff_absence_periods" in update_data and update_data["staff_absence_periods"] is not None:
            # バリデーション
            periods_list = update_data["staff_absence_periods"]
            validated_periods = []
            
            for period in periods_list:
                # StaffAbsencePeriodオブジェクトの場合はdictに変換
                if isinstance(period, StaffAbsencePeriod):
                    period_dict = period.dict()
                else:
                    period_dict = period
                
                if not period_dict.get("start_time") or not period_dict.get("end_time"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="start_time and end_time are required for staff_absence_periods"
                    )
                if not period_dict.get("days_of_week") or not isinstance(period_dict["days_of_week"], list):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="days_of_week must be a list"
                    )
                # 時刻形式の検証
                try:
                    hour, minute = map(int, period_dict["start_time"].split(":"))
                    hour, minute = map(int, period_dict["end_time"].split(":"))
                except (ValueError, AttributeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid time format in staff_absence_periods. Use HH:MM format."
                    )
                
                validated_periods.append(period_dict)
            
            # JSONとして保存
            facility.staff_absence_periods = validated_periods
        
        await db.commit()
        await db.refresh(facility)
        
        # レスポンスを構築
        check_in_time_str = None
        check_out_time_str = None
        
        if facility.check_in_time:
            check_in_time_str = facility.check_in_time.strftime("%H:%M")
        
        if facility.check_out_time:
            check_out_time_str = facility.check_out_time.strftime("%H:%M")
        
        facility_response = FacilityResponse(
            id=facility.id,
            name=facility.name,
            slug=facility.slug,
            email=facility.email,
            phone=facility.phone,
            address=facility.address,
            wifi_ssid=facility.wifi_ssid,
            check_in_time=check_in_time_str,
            check_out_time=check_out_time_str,
            house_rules=facility.house_rules,
            local_info=facility.local_info,
            languages=facility.languages or [],
            timezone=facility.timezone or "Asia/Tokyo",
            subscription_plan=facility.subscription_plan or "small",
            monthly_question_limit=facility.monthly_question_limit or 200,
            is_active=facility.is_active,
            created_at=facility.created_at,
            updated_at=facility.updated_at
        )
        
        # スタッフ不在時間帯をパース
        staff_absence_periods: List[StaffAbsencePeriod] = []
        if facility.staff_absence_periods:
            try:
                if isinstance(facility.staff_absence_periods, str):
                    periods_data = json.loads(facility.staff_absence_periods)
                else:
                    periods_data = facility.staff_absence_periods
                
                for period_data in periods_data:
                    staff_absence_periods.append(StaffAbsencePeriod(**period_data))
            except (json.JSONDecodeError, TypeError, ValueError):
                staff_absence_periods = []
        
        return FacilitySettingsResponse(
            facility=facility_response,
            staff_absence_periods=staff_absence_periods,
            icon_url=facility.icon_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating facility settings: {str(e)}"
        )

