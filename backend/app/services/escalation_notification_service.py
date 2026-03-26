"""
スタッフ向けエスカレーション通知（A-4：送信の芯）。

Brevo 経由で施設の連絡先メールへ送り、成功時のみ escalations.notified_at を更新する。
`ChatService`・`POST /chat/escalate`・`OvernightQueueService.process_scheduled_notifications` から呼ばれる。
"""

import logging
from datetime import datetime, timezone

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversation import Conversation
from app.models.escalation import Escalation
from app.models.facility import Facility

logger = logging.getLogger(__name__)


def _admin_conversation_url(session_id: str) -> str:
    base = (settings.frontend_url or "").rstrip("/")
    return f"{base}/admin/conversations/{session_id}"


async def send_staff_escalation_notification(
    db: AsyncSession,
    escalation_id: int,
) -> bool:
    """
    施設担当宛に「新規のスタッフ連絡（エスカレーション）」通知メールを送る。

    - 受付番号は必ず escalations.id のみを本文・件名に含める。
    - 既に notified_at が入っている場合は送信せず True を返す（冪等）。
    - BREVO_API_KEY が無い場合は開発では warning、本番では error ログのうえ False
      （本番は `Settings` で起動時にキー必須のため通常ここには到達しないが、防御的に記録）。
    - 送信に成功した場合のみ notified_at を更新し commit する。

    Returns:
        送信成功または既に通知済みなら True。スキップ・失敗で False。
    """
    escalation = await db.get(Escalation, escalation_id)
    if not escalation:
        logger.error(
            "Escalation not found for staff notification: escalation_id=%s",
            escalation_id,
        )
        return False

    if escalation.notified_at is not None:
        logger.info(
            "Staff escalation email skipped (already notified): escalation_id=%s",
            escalation_id,
        )
        return True

    facility = await db.get(Facility, escalation.facility_id)
    conversation = await db.get(Conversation, escalation.conversation_id)

    if not facility or not facility.email:
        logger.error(
            "Facility or facility.email missing for escalation notification: "
            "escalation_id=%s facility_id=%s",
            escalation_id,
            escalation.facility_id,
        )
        return False

    if not conversation or not conversation.session_id:
        logger.error(
            "Conversation or session_id missing for escalation notification: "
            "escalation_id=%s conversation_id=%s",
            escalation_id,
            escalation.conversation_id,
        )
        return False

    if not settings.brevo_api_key:
        msg = (
            "BREVO_API_KEY not set; staff escalation email not sent: escalation_id=%s"
        )
        if settings.environment == "production":
            logger.error(msg, escalation_id)
        else:
            logger.warning(msg, escalation_id)
        return False

    receipt_id = escalation.id
    facility_name = facility.name
    session_id = conversation.session_id
    admin_url = _admin_conversation_url(session_id)
    created = escalation.created_at
    created_str = (
        created.strftime("%Y-%m-%d %H:%M:%S UTC")
        if created
        else "（記録なし）"
    )

    subject = f"【YadOPERA】スタッフ連絡 受付番号 {receipt_id}（{facility_name}）"

    html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"></head>
<body style="font-family: sans-serif; line-height: 1.6; color: #333; max-width: 640px;">
  <h2 style="color: #0c4a6e;">YadOPERA — ゲストからスタッフへの連絡</h2>
  <p><strong>施設名:</strong> {facility_name}</p>
  <p><strong>受付番号:</strong> {receipt_id}</p>
  <p><strong>作成日時:</strong> {created_str}</p>
  <p>管理画面で会話の内容を確認できます。</p>
  <p><a href="{admin_url}" style="color: #2563eb;">{admin_url}</a></p>
  <p style="font-size: 12px; color: #666;">※ 受付番号はゲスト画面の表示と同一の番号です。</p>
  <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
  <p style="font-size: 12px; color: #999;">© YadOPERA — 送信専用。返信は管理画面からお願いします。</p>
</body>
</html>
"""

    text_content = f"""YadOPERA — ゲストからスタッフへの連絡

施設名: {facility_name}
受付番号: {receipt_id}
作成日時: {created_str}

管理画面（会話）:
{admin_url}

※ 受付番号はゲスト画面の表示と同一の番号です。

---
© YadOPERA
"""

    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.brevo_api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": facility.email, "name": facility_name}],
            sender={
                "email": settings.brevo_sender_email,
                "name": settings.brevo_sender_name,
            },
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )
        api_response = api_instance.send_transac_email(send_smtp_email)
        now = datetime.now(timezone.utc)
        escalation.notified_at = now
        await db.commit()
        logger.info(
            "Staff escalation email sent: escalation_id=%s facility_id=%s to=%s message_id=%s",
            receipt_id,
            facility.id,
            facility.email,
            getattr(api_response, "message_id", None),
        )
        return True
    except ApiException as e:
        logger.error(
            "Brevo API error (staff escalation): escalation_id=%s status=%s reason=%s body=%s",
            escalation_id,
            e.status,
            e.reason,
            e.body,
        )
        await db.rollback()
        return False
    except Exception:
        logger.exception(
            "Unexpected error sending staff escalation email: escalation_id=%s",
            escalation_id,
        )
        await db.rollback()
        return False
