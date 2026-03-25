"""スタッフ向けエスカレーション通知メール（送信の芯）のテスト"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.models.conversation import Conversation
from app.models.escalation import Escalation
from app.services.escalation_notification_service import send_staff_escalation_notification


@pytest.mark.asyncio
async def test_send_staff_escalation_notification_success(db_session, test_facility):
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-notify-1",
        guest_language="ja",
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.refresh(conversation)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)
    eid = escalation.id

    with patch.object(settings, "brevo_api_key", "test-brevo-key"), patch.object(
        settings, "brevo_sender_email", "noreply@test.example"
    ), patch.object(settings, "brevo_sender_name", "YadOPERA Test"), patch.object(
        settings, "frontend_url", "https://app.test.example"
    ), patch(
        "app.services.escalation_notification_service.sib_api_v3_sdk.TransactionalEmailsApi"
    ) as mock_api_cls:
        mock_api = MagicMock()
        mock_api.send_transac_email.return_value = MagicMock(message_id="mid-1")
        mock_api_cls.return_value = mock_api

        ok = await send_staff_escalation_notification(db_session, eid)

    assert ok is True
    mock_api.send_transac_email.assert_called_once()

    fresh = await db_session.get(Escalation, eid)
    assert fresh is not None
    assert fresh.notified_at is not None


@pytest.mark.asyncio
async def test_send_staff_escalation_notification_idempotent(db_session, test_facility):
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-notify-2",
        guest_language="ja",
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.refresh(conversation)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)
    eid = escalation.id

    with patch.object(settings, "brevo_api_key", "test-brevo-key"), patch.object(
        settings, "brevo_sender_email", "noreply@test.example"
    ), patch.object(settings, "brevo_sender_name", "YadOPERA Test"), patch.object(
        settings, "frontend_url", "https://app.test.example"
    ), patch(
        "app.services.escalation_notification_service.sib_api_v3_sdk.TransactionalEmailsApi"
    ) as mock_api_cls:
        mock_api = MagicMock()
        mock_api.send_transac_email.return_value = MagicMock(message_id="mid-2")
        mock_api_cls.return_value = mock_api

        assert await send_staff_escalation_notification(db_session, eid) is True
        assert await send_staff_escalation_notification(db_session, eid) is True

    assert mock_api.send_transac_email.call_count == 1


@pytest.mark.asyncio
async def test_send_staff_escalation_notification_missing_row(db_session):
    ok = await send_staff_escalation_notification(db_session, 999999999)
    assert ok is False


@pytest.mark.asyncio
async def test_send_staff_escalation_notification_no_brevo_key(db_session, test_facility):
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-notify-3",
        guest_language="ja",
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.refresh(conversation)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)

    with patch.object(settings, "brevo_api_key", ""), patch(
        "app.services.escalation_notification_service.sib_api_v3_sdk.TransactionalEmailsApi"
    ) as mock_api_cls:
        ok = await send_staff_escalation_notification(db_session, escalation.id)

    assert ok is False
    mock_api_cls.assert_not_called()

    fresh = await db_session.get(Escalation, escalation.id)
    assert fresh.notified_at is None


@pytest.mark.asyncio
async def test_send_staff_escalation_notification_includes_receipt_id_everywhere(
    db_session, test_facility
):
    """件名・HTML・テキストに受付番号（escalations.id のみ）が含まれる"""
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-receipt-1",
        guest_language="ja",
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
    )
    db_session.add(conversation)
    await db_session.flush()
    await db_session.refresh(conversation)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)
    eid = escalation.id
    receipt = str(eid)

    with patch.object(settings, "brevo_api_key", "test-brevo-key"), patch.object(
        settings, "brevo_sender_email", "noreply@test.example"
    ), patch.object(settings, "brevo_sender_name", "YadOPERA Test"), patch.object(
        settings, "frontend_url", "https://app.test.example"
    ), patch(
        "app.services.escalation_notification_service.sib_api_v3_sdk.TransactionalEmailsApi"
    ) as mock_api_cls:
        mock_api = MagicMock()
        mock_api.send_transac_email.return_value = MagicMock(message_id="mid-rid")
        mock_api_cls.return_value = mock_api

        ok = await send_staff_escalation_notification(db_session, eid)

    assert ok is True
    mock_api.send_transac_email.assert_called_once()
    sent = mock_api.send_transac_email.call_args[0][0]
    assert receipt in (sent.subject or "")
    assert receipt in (sent.html_content or "")
    assert receipt in (sent.text_content or "")
    admin_path = f"/admin/conversations/{conversation.session_id}"
    assert admin_path in (sent.html_content or "")
    assert admin_path in (sent.text_content or "")
