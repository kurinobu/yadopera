"""
リード（クーポン取得）サービス
決済なしリード獲得: エントリー保存・クーポン送付
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.guest_lead import GuestLead
from app.models.facility import Facility
from app.schemas.lead import LeadListItem, LeadListResponse

logger = logging.getLogger(__name__)


class LeadService:
    """リード登録・一覧取得"""
    
    @staticmethod
    async def create_lead_and_send_coupon(
        db: AsyncSession,
        facility: Facility,
        guest_name: Optional[str],
        email: str,
    ) -> GuestLead:
        """
        リードを登録し、クーポン送付メールを送信する。
        
        Args:
            db: データベースセッション
            facility: 施設（coupon_* が設定されていること）
            guest_name: ゲスト名（任意）
            email: メールアドレス
        
        Returns:
            登録した GuestLead（coupon_sent_at は送信成功時に更新）
        
        Raises:
            ValueError: クーポンが無効または設定不足の場合
        """
        if not getattr(facility, "coupon_enabled", False):
            raise ValueError("Coupon is not enabled for this facility")
        if facility.coupon_discount_percent is None:
            raise ValueError("Coupon discount rate is not set")
        
        lead = GuestLead(
            facility_id=facility.id,
            guest_name=guest_name,
            email=email,
        )
        db.add(lead)
        await db.flush()  # lead.id を取得するため
        
        # 有効期限の表示用文字列（発行日 + validity_months）
        months = getattr(facility, "coupon_validity_months", None) or 6
        valid_until_dt = datetime.utcnow() + timedelta(days=months * 30)
        valid_until = valid_until_dt.strftime("%Y年%m月%d日まで")
        
        try:
            from app.services.email_service import EmailService
            email_svc = EmailService()
            sent = await email_svc.send_coupon_email(
                to_email=email,
                to_name=guest_name,
                facility_name=facility.name,
                discount_percent=facility.coupon_discount_percent,
                description=getattr(facility, "coupon_description", None),
                valid_until=valid_until,
                official_website_url=getattr(facility, "official_website_url", None),
            )
            if sent:
                lead.coupon_sent_at = datetime.utcnow()
        except Exception as e:
            logger.error(
                f"Failed to send coupon email: lead_id={lead.id}, email={email}, error={e}",
                exc_info=True
            )
            await db.commit()
            await db.refresh(lead)
            raise  # 呼び出し元で 500 等を返す。リードは保存済みのため再送は別途検討可能。
        
        await db.commit()
        await db.refresh(lead)
        return lead
    
    @staticmethod
    async def get_leads(
        db: AsyncSession,
        facility_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> LeadListResponse:
        """リード一覧を取得（ページネーション）"""
        query = (
            select(GuestLead)
            .where(GuestLead.facility_id == facility_id)
            .order_by(GuestLead.created_at.desc())
        )
        count_result = await db.execute(
            select(func.count(GuestLead.id)).where(GuestLead.facility_id == facility_id)
        )
        total = count_result.scalar() or 0
        
        result = await db.execute(query.offset(skip).limit(limit))
        leads = result.scalars().all()
        items = [
            LeadListItem(
                id=lead.id,
                facility_id=lead.facility_id,
                guest_name=lead.guest_name,
                email=lead.email,
                coupon_sent_at=lead.coupon_sent_at,
                created_at=lead.created_at,
            )
            for lead in leads
        ]
        return LeadListResponse(leads=items, total=total)