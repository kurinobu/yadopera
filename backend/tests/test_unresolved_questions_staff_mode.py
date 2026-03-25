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


@pytest.mark.asyncio
async def test_unresolved_questions_question_uses_latest_user_before_escalation_created_at(
    db_session, test_facility, mock_openai_patch
):
    """
    スクショと同様の時系列を再現:
      - スリッパ（USER）
      - バスタオル（USER）直後に staff_mode（エスカレーション作成）
      - フェイスタオル（USER）

    未解決リスト生成時に question/message_id に使うのは、
    messages.role=user のうち「escalation.created_at 以前の直近USER」だけ。
    """
    service = EscalationService()
    suggestion_service = FAQSuggestionService(db_session)

    t0 = datetime(2026, 3, 25, 18, 10, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 3, 25, 18, 12, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 25, 18, 14, 0, tzinfo=timezone.utc)
    esc_t = datetime(2026, 3, 25, 18, 12, 30, tzinfo=timezone.utc)  # バスタオル直後に staff_mode

    conversation = Conversation(
        facility_id=test_facility.id,
        session_id="sess-unresolved-staff-mode-2",
        guest_language="ja",
        started_at=t0,
        last_activity_at=t2,
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    # USER: スリッパ
    msg_slippers = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content="スリッパを貸してもらえますか？",
        created_at=t0,
    )
    db_session.add(msg_slippers)
    await db_session.commit()
    await db_session.refresh(msg_slippers)

    # USER: バスタオル（staff_mode作成対象）
    msg_towel = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content="新しいバスタオルは借りたいです",
        created_at=t1,
    )
    db_session.add(msg_towel)
    await db_session.commit()
    await db_session.refresh(msg_towel)

    # USER: フェイスタオル（staff_mode作成後）
    msg_face_towel = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER.value,
        content="フェイスタオルも追加で借りたいです",
        created_at=t2,
    )
    db_session.add(msg_face_towel)
    await db_session.commit()
    await db_session.refresh(msg_face_towel)

    escalation = Escalation(
        facility_id=test_facility.id,
        conversation_id=conversation.id,
        trigger_type="staff_mode",
        escalation_mode="normal",
        ai_confidence=0.10,
        created_at=esc_t,
    )
    db_session.add(escalation)
    await db_session.commit()
    await db_session.refresh(escalation)

    # ASSISTANTは作らない（staff_mode想定）
    unresolved = await service.get_unresolved_questions(
        facility_id=test_facility.id, db=db_session
    )

    assert len(unresolved) == 1
    assert unresolved[0].id == escalation.id
    # question/message_id の元は「直近USER（escalation.created_at以前）」であるべき
    assert unresolved[0].message_id == msg_towel.id
    assert unresolved[0].question == msg_towel.content

    # その message_id で FAQ 提案が生成できることも担保
    with mock_openai_patch:
        suggestion = await suggestion_service.generate_suggestion(
            facility_id=test_facility.id, message_id=msg_towel.id
        )
    assert suggestion.source_message_id == msg_towel.id

