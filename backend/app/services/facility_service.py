"""
施設サービス
施設情報取得など
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.facility import Facility
from app.models.faq import FAQ
from app.schemas.facility import FacilityPublicResponse, TopQuestion
from fastapi import HTTPException, status


class FacilityService:
    """
    施設サービス
    """
    
    @staticmethod
    async def get_facility_by_slug(
        db: AsyncSession,
        slug: str
    ) -> Optional[Facility]:
        """
        施設をslugで取得
        
        Args:
            db: データベースセッション
            slug: 施設slug
            
        Returns:
            施設オブジェクト（見つからない場合はNone）
        """
        result = await db.execute(
            select(Facility).where(
                Facility.slug == slug,
                Facility.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_facility_public_info(
        db: AsyncSession,
        slug: str
    ) -> FacilityPublicResponse:
        """
        施設情報を公開用形式で取得
        
        Args:
            db: データベースセッション
            slug: 施設slugまたはID（文字列）
            
        Returns:
            施設情報公開レスポンス
            
        Raises:
            HTTPException: 施設が見つからない場合
        """
        # slugが数値IDの場合も対応
        facility = None
        
        # まず、slugとして検索を試みる
        facility = await FacilityService.get_facility_by_slug(db, slug)
        
        # slugで見つからない場合、数値IDとして検索を試みる
        if facility is None:
            try:
                facility_id = int(slug)
                result = await db.execute(
                    select(Facility).where(
                        Facility.id == facility_id,
                        Facility.is_active == True
                    )
                )
                facility = result.scalar_one_or_none()
            except ValueError:
                # slugが数値として解釈できない場合は何もしない
                pass
        
        if facility is None:
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
        
        # よくある質問TOP3を取得
        faq_query = select(FAQ).where(
            FAQ.facility_id == facility.id,
            FAQ.is_active == True
        ).order_by(
            FAQ.priority.desc(),
            FAQ.created_at.desc()
        ).limit(3)
        
        faq_result = await db.execute(faq_query)
        top_faqs = faq_result.scalars().all()
        
        # TopQuestion型に変換（フロントエンドの型定義に合わせる）
        top_questions: List[TopQuestion] = [
            TopQuestion(
                id=faq.id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category
            )
            for faq in top_faqs
        ]
        
        return FacilityPublicResponse(
            id=facility.id,
            name=facility.name,
            slug=facility.slug,
            email=facility.email,
            phone=facility.phone,
            check_in_time=check_in_time_str,
            check_out_time=check_out_time_str,
            wifi_ssid=facility.wifi_ssid,
            top_questions=top_questions,
        )

