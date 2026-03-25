"""
エスカレーション作成直後のルーティング（スタッフ不在時間内なら夜間キュー、それ以外は即時メールは呼び出し先）。
ChatService と POST /chat/escalate で共通利用する。
"""

import json
import logging
from datetime import datetime, timezone

import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.facility import Facility
from app.utils.staff_absence import is_in_staff_absence_period
from app.services.overnight_queue_service import OvernightQueueService

logger = logging.getLogger(__name__)


async def queue_escalation_if_staff_absence(
    db: AsyncSession,
    *,
    facility_id: int,
    escalation_id: int,
    conversation_id: int,
    guest_message: str,
    guest_language_for_auto_reply: str,
    overnight_queue_service: OvernightQueueService,
) -> bool:
    """
    スタッフ不在時間内なら夜間キューへ入れ自動返信し True（この場合は即時メールを送らない）。
    不在時間外、または施設が取れない場合は False（呼び出し元が即時メールを送る）。
    """
    facility = await db.get(Facility, facility_id)
    if not facility:
        logger.warning(
            "queue_escalation_if_staff_absence: facility not found facility_id=%s escalation_id=%s",
            facility_id,
            escalation_id,
        )
        return False

    timezone_str = facility.timezone or "Asia/Tokyo"
    utc_now = datetime.now(timezone.utc)
    facility_tz = pytz.timezone(timezone_str)
    local_now = utc_now.astimezone(facility_tz)

    staff_absence_periods: list = []
    if facility.staff_absence_periods:
        try:
            if isinstance(facility.staff_absence_periods, str):
                staff_absence_periods = json.loads(facility.staff_absence_periods)
            else:
                staff_absence_periods = facility.staff_absence_periods
        except (json.JSONDecodeError, TypeError, ValueError):
            staff_absence_periods = []

    current_weekday = local_now.strftime("%a").lower()

    if not is_in_staff_absence_period(
        current_time=local_now,
        current_weekday=current_weekday,
        staff_absence_periods=staff_absence_periods,
    ):
        return False

    await overnight_queue_service.add_to_overnight_queue(
        facility_id=facility_id,
        escalation_id=escalation_id,
        guest_message=guest_message,
        db=db,
    )
    await overnight_queue_service.send_overnight_auto_reply(
        conversation_id=conversation_id,
        language=guest_language_for_auto_reply,
        db=db,
    )
    return True
