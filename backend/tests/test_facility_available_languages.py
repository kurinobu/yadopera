"""
施設情報取得APIの利用可能言語取得テスト
各プランでの言語取得をテスト
"""

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time

from app.models.facility import Facility
from app.services.facility_service import FacilityService


class TestFacilityAvailableLanguages:
    """施設情報取得APIの利用可能言語取得テスト"""
    
    @pytest.fixture
    async def test_facility_free(self, db_session: AsyncSession):
        """Freeプランのテスト用施設（言語数制限: 1、日本語のみ）"""
        facility = Facility(
            name="Test Hotel Free",
            slug="test-hotel-free",
            email="test-free@example.com",
            plan_type="Free",
            language_limit=1,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_mini(self, db_session: AsyncSession):
        """Miniプランのテスト用施設（言語数制限: 2、日本語＋英語）"""
        facility = Facility(
            name="Test Hotel Mini",
            slug="test-hotel-mini",
            email="test-mini@example.com",
            plan_type="Mini",
            language_limit=2,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_small(self, db_session: AsyncSession):
        """Smallプランのテスト用施設（言語数制限: 3、日本語＋英語＋中国語）"""
        facility = Facility(
            name="Test Hotel Small",
            slug="test-hotel-small",
            email="test-small@example.com",
            plan_type="Small",
            language_limit=3,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_standard(self, db_session: AsyncSession):
        """Standardプランのテスト用施設（言語数制限: 4、日本語＋英語＋中国語＋フランス語）"""
        facility = Facility(
            name="Test Hotel Standard",
            slug="test-hotel-standard",
            email="test-standard@example.com",
            plan_type="Standard",
            language_limit=4,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_premium(self, db_session: AsyncSession):
        """Premiumプランのテスト用施設（言語数制限: 無制限、全言語対応）"""
        facility = Facility(
            name="Test Hotel Premium",
            slug="test-hotel-premium",
            email="test-premium@example.com",
            plan_type="Premium",
            language_limit=None,  # 無制限
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_no_plan(self, db_session: AsyncSession):
        """プランが設定されていないテスト用施設（デフォルト: Free）"""
        facility = Facility(
            name="Test Hotel No Plan",
            slug="test-hotel-no-plan",
            email="test-no-plan@example.com",
            plan_type=None,  # プラン未設定
            language_limit=1,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.mark.asyncio
    async def test_get_facility_free_plan_languages(
        self, db_session: AsyncSession, test_facility_free: Facility
    ):
        """Freeプラン: 日本語のみが返されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_free.slug
        )
        
        assert result.plan_type == "Free"
        assert result.available_languages == ["ja"]
    
    @pytest.mark.asyncio
    async def test_get_facility_mini_plan_languages(
        self, db_session: AsyncSession, test_facility_mini: Facility
    ):
        """Miniプラン: 日本語＋英語が返されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_mini.slug
        )
        
        assert result.plan_type == "Mini"
        assert result.available_languages == ["ja", "en"]
    
    @pytest.mark.asyncio
    async def test_get_facility_small_plan_languages(
        self, db_session: AsyncSession, test_facility_small: Facility
    ):
        """Smallプラン: 日本語＋英語＋中国語が返されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_small.slug
        )
        
        assert result.plan_type == "Small"
        assert result.available_languages == ["ja", "en", "zh-TW"]
    
    @pytest.mark.asyncio
    async def test_get_facility_standard_plan_languages(
        self, db_session: AsyncSession, test_facility_standard: Facility
    ):
        """Standardプラン: 日本語＋英語＋中国語＋フランス語が返されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_standard.slug
        )
        
        assert result.plan_type == "Standard"
        assert result.available_languages == ["ja", "en", "zh-TW", "fr"]
    
    @pytest.mark.asyncio
    async def test_get_facility_premium_plan_languages(
        self, db_session: AsyncSession, test_facility_premium: Facility
    ):
        """Premiumプラン: Standardプラン＋韓国語が返されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_premium.slug
        )
        
        assert result.plan_type == "Premium"
        # Premiumプラン: Standardプラン（日本語、英語、中国語、フランス語）＋韓国語
        expected_languages = ["ja", "en", "zh-TW", "fr", "ko"]
        assert result.available_languages == expected_languages
    
    @pytest.mark.asyncio
    async def test_get_facility_no_plan_defaults_to_free(
        self, db_session: AsyncSession, test_facility_no_plan: Facility
    ):
        """プランが設定されていない場合: デフォルト（Free）として処理されることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, test_facility_no_plan.slug
        )
        
        # plan_typeがNoneの場合、デフォルトで"Free"として処理される
        assert result.plan_type == "Free"
        # デフォルトは日本語のみ
        assert result.available_languages == ["ja"]
    
    @pytest.mark.asyncio
    async def test_get_facility_not_found(
        self, db_session: AsyncSession
    ):
        """施設が見つからない場合: 404エラーが発生することを確認"""
        with pytest.raises(HTTPException) as exc_info:
            await FacilityService.get_facility_public_info(
                db_session, "non-existent-facility"
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Facility not found"
    
    @pytest.mark.asyncio
    async def test_get_facility_by_id(
        self, db_session: AsyncSession, test_facility_free: Facility
    ):
        """数値IDで施設情報を取得できることを確認"""
        result = await FacilityService.get_facility_public_info(
            db_session, str(test_facility_free.id)
        )
        
        assert result.id == test_facility_free.id
        assert result.plan_type == "Free"
        assert result.available_languages == ["ja"]

