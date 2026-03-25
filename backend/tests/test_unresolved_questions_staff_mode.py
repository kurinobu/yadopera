"""
未解決質問リスト（FAQ管理）に staff_mode を確実に載せるためのテスト
"""

from datetime import datetime, timezone

import pytest

from app.services.escalation_service import EscalationService
from app.services.faq_suggestion_service import FAQSuggestionService
from app.models.conversation import Conversation
from app.models.escalation import Escalation
from app.models.message import Message, MessageRole


@pytest.mark.asyncio
async def test_unresolved_questions_includes_staff_mode_without_assistant(
    db_session, test_facility, mock_openai_patch
):
    """ASSISTANTメッセージが無い（例: staff_mode）でも未解決質問に含まれること"""
    service = EscalationService()

    utc_now = datetime.now(timezone.utc)
    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-unresolved-staff-mode-1",
        guest_language="ja",
        started_at=utc_now,
        last_activity_at=utc_now,
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
        escalation_mode="normal",
        ai_confidence=0.10,
        # notification_channels はデフォルトを利用
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)

    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content="チェックインは何時からですか？",
        created_at=utc_now,
    )
    db_session.add(user_message)
    await db_session.commit()
    await db_session.refresh(user_message)

    # ASSISTANTメッセージは作らない（staff_mode想定）
    unresolved = await service.get_unresolved_questions(
        facility_id=test_facility.id, db=db_session
    )

    assert len(unresolved) == 1
    assert unresolved[0].id == escalation.id
    # staff_mode を含めるため message_id は USERロール側になる
    assert unresolved[0].message_id == user_message.id

    # ついでに、その message_id から FAQ提案生成できること（USER role でも）
    suggestion_service = FAQSuggestionService(db_session)
    with mock_openai_patch:
        suggestion = await suggestion_service.generate_suggestion(
            facility_id=test_facility.id,
            message_id=user_message.id,
        )

    assert suggestion.id is not None
    assert suggestion.facility_id == test_facility.id
    assert suggestion.source_message_id == user_message.id
    assert suggestion.suggested_category is not None

