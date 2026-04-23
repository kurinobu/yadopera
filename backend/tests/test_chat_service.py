"""
チャットサービス統合テスト
"""

import uuid
import pytest
from datetime import datetime
from decimal import Decimal
import pytz
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, RAGEngineResponse, EscalationInfo
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.facility import Facility
from app.models.escalation import Escalation


class TestChatService:
    """チャットサービス統合テスト"""
    
    def test_wifi_shortcut_with_password_answers_credentials(self):
        """WiFi関連質問は施設設定のSSID/パスワードを明示し、誤誘導文言を返さない"""
        facility = Facility(
            name="Wifi Hotel",
            slug=f"wifi-shortcut-{uuid.uuid4().hex[:6]}",
            email=f"wifi-shortcut-{uuid.uuid4().hex[:6]}@example.com",
            wifi_ssid="yadobito123",
            wifi_password="wiwiwiwi",
            plan_type="Free",
            is_active=True,
        )
        service = ChatService(MagicMock())
        response = service._build_wifi_shortcut_response(
            facility=facility,
            message="WiFiの使い方を教えてください",
            language="ja",
        )
        assert response is not None
        assert "yadobito123" in response.response
        assert "wiwiwiwi" in response.response
        assert "必要ありません" not in response.response

    def test_wifi_shortcut_without_password_does_not_invent(self):
        """パスワード未設定時は捏造せずスタッフ確認に誘導する"""
        facility = Facility(
            name="Wifi No Pass",
            slug=f"wifi-no-pass-{uuid.uuid4().hex[:6]}",
            email=f"wifi-no-pass-{uuid.uuid4().hex[:6]}@example.com",
            wifi_ssid="guest-wifi",
            wifi_password=None,
            plan_type="Free",
            is_active=True,
        )
        service = ChatService(MagicMock())
        response = service._build_wifi_shortcut_response(
            facility=facility,
            message="WiFiの使い方",
            language="ja",
        )
        assert response is not None
        assert "未設定" in response.response
        assert "wiwiwiwi" not in response.response

    @pytest.mark.asyncio
    @patch('app.services.chat_service.RAGChatEngine')
    async def test_process_chat_message_new_conversation(
        self,
        mock_rag_engine_class,
        db_session,
        test_facility
    ):
        """新規会話でのメッセージ処理テスト"""
        mock_rag_response = RAGEngineResponse(
            response="Test response",
            ai_confidence=Decimal("0.8"),
            matched_faq_ids=[],
            response_time_ms=100,
            escalation=EscalationInfo(
                needed=False, mode=None, trigger_type=None, reason=None, notified=None
            ),
        )
        mock_rag_engine = AsyncMock()
        mock_rag_engine.process_message = AsyncMock(return_value=mock_rag_response)
        mock_rag_engine_class.return_value = mock_rag_engine
        
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        chat_service.rag_engine = mock_rag_engine
        
        # テスト実行（Free プランは ja のみ選択可）
        request = ChatRequest(
            facility_id=test_facility.id,
            message="What time is check-out?",
            language="ja",
        )
        
        response = await chat_service.process_chat_message(
            request=request,
            user_agent="Test Agent",
            ip_address="127.0.0.1"
        )
        
        # アサーション（ChatResponse は message に本文を持つ）
        assert response.session_id is not None
        assert response.message.content == "Test response"
        
        # 会話が作成されたか確認
        from sqlalchemy import select
        result = await db_session.execute(
            select(Conversation).where(Conversation.session_id == response.session_id)
        )
        conversation = result.scalar_one_or_none()
        assert conversation is not None
        assert conversation.facility_id == test_facility.id
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, db_session, test_facility):
        """会話履歴取得テスト"""
        # 会話作成
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-history",
            guest_language="en",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # メッセージ追加
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content="What time is check-out?"
        )
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content="Check-out is by 11:00 AM."
        )
        db_session.add(user_message)
        db_session.add(ai_message)
        await db_session.commit()
        
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        
        # テスト実行
        history = await chat_service.get_conversation_history(
            session_id="test-session-history",
            facility_id=test_facility.id
        )
        
        # アサーション
        assert history is not None
        assert history.session_id == "test-session-history"
        assert len(history.messages) == 2
        assert history.unresolved_escalation_id is None
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_unresolved_escalation_id(self, db_session, test_facility):
        """管理用履歴取得時、未解決エスカレのIDが付与される"""
        conversation = Conversation(
            facility_id=test_facility.id,
            session_id="test-session-esc-open",
            guest_language="ja",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)

        escalation = Escalation(
            facility_id=test_facility.id,
            conversation_id=conversation.id,
            trigger_type="staff_mode",
            resolved_at=None,
        )
        db_session.add(escalation)
        await db_session.commit()
        await db_session.refresh(escalation)

        chat_service = ChatService(db_session)
        history = await chat_service.get_conversation_history(
            session_id="test-session-esc-open",
            facility_id=test_facility.id,
        )
        assert history is not None
        assert history.unresolved_escalation_id == escalation.id

    @pytest.mark.asyncio
    async def test_get_conversation_history_not_found(self, db_session):
        """会話履歴が見つからない場合のテスト"""
        # チャットサービス初期化
        chat_service = ChatService(db_session)
        
        # テスト実行
        history = await chat_service.get_conversation_history(
            session_id="non-existent-session",
            facility_id=1
        )
        
        # アサーション
        assert history is None

    @pytest.mark.asyncio
    async def test_process_chat_message_over_limit_faq_only_no_rag_no_meter(self, db_session):
        """プラン超過・overage_behavior=faq_only のとき RAG とメーター報告が呼ばれず FAQ のみ応答（Step 6 検証）"""
        utc = pytz.UTC
        plan_started_at_utc = utc.localize(datetime(2026, 1, 15, 10, 0, 0))

        uid = uuid.uuid4().hex[:8]
        facility = Facility(
            name="Test Over FAQ",
            slug=f"test-over-faq-{uid}",
            email=f"over-faq-{uid}@example.com",
            plan_type="Free",
            monthly_question_limit=30,
            plan_started_at=plan_started_at_utc,
            overage_behavior="faq_only",
            is_active=True,
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.commit()

        faq_response = RAGEngineResponse(
            response="FAQ限定モードの応答",
            ai_confidence=Decimal("0.7"),
            matched_faq_ids=[],
            response_time_ms=10,
            escalation=EscalationInfo(needed=False, mode=None, trigger_type=None, reason=None, notified=None),
        )

        with patch.object(ChatService, "_should_use_faq_only_path", new_callable=AsyncMock) as mock_should:
            mock_should.return_value = True
            with patch.object(ChatService, "_build_faq_only_response", new_callable=AsyncMock) as mock_faq:
                with patch.object(ChatService, "_report_usage_to_stripe_if_needed", new_callable=AsyncMock) as mock_report:
                    mock_faq.return_value = faq_response
                    mock_rag = AsyncMock()
                    mock_rag.process_message = AsyncMock()

                    with patch("app.services.chat_service.RAGChatEngine", return_value=mock_rag):
                        service = ChatService(db_session)
                        service.rag_engine = mock_rag

                        request = ChatRequest(
                            facility_id=facility.id,
                            message="チェックアウトは何時？",
                            language="ja",
                        )
                        response = await service.process_chat_message(request=request)

                    mock_should.assert_called_once()
                    mock_faq.assert_called_once()
                    mock_report.assert_not_called()
                    mock_rag.process_message.assert_not_called()
                    assert response.message.content == "FAQ限定モードの応答"

    @pytest.mark.asyncio
    async def test_process_chat_message_over_limit_continue_billing_rag_and_meter_called(self, db_session):
        """プラン超過・overage_behavior=continue_billing のとき RAG 実行とメーター報告が行われる（Step 6 検証）"""
        jst = pytz.timezone("Asia/Tokyo")
        utc = pytz.UTC
        plan_started_at_utc = jst.localize(datetime(2026, 1, 15, 10, 0, 0)).astimezone(utc)
        period_utc = utc.localize(datetime(2026, 1, 20, 6, 0, 0))

        uid = uuid.uuid4().hex[:8]
        facility = Facility(
            name="Test Over Billing",
            slug=f"test-over-billing-{uid}",
            email=f"over-billing-{uid}@example.com",
            plan_type="Free",
            monthly_question_limit=30,
            plan_started_at=plan_started_at_utc,
            overage_behavior="continue_billing",
            is_active=True,
        )
        db_session.add(facility)
        await db_session.flush()

        for i in range(30):
            conv = Conversation(
                facility_id=facility.id,
                session_id=f"over-billing-{uid}-{i}",
                started_at=period_utc,
                guest_language="ja",
            )
            db_session.add(conv)
            await db_session.flush()
            msg = Message(
                conversation_id=conv.id,
                role=MessageRole.USER.value,
                content=f"質問{i}",
                created_at=period_utc,
            )
            db_session.add(msg)
        await db_session.commit()

        fixed_now_jst = jst.localize(datetime(2026, 1, 25, 15, 0, 0))
        rag_return = RAGEngineResponse(
            response="RAG応答",
            ai_confidence=Decimal("0.9"),
            matched_faq_ids=[],
            response_time_ms=100,
            escalation=EscalationInfo(needed=False, mode=None, trigger_type=None, reason=None, notified=None),
        )

        with patch("app.services.chat_service.datetime") as mdt:
            mdt.now = MagicMock(side_effect=lambda tz=None: fixed_now_jst.astimezone(tz) if tz else fixed_now_jst)
            with patch.object(ChatService, "_report_usage_to_stripe_if_needed", new_callable=AsyncMock) as mock_report:
                mock_rag = AsyncMock()
                mock_rag.process_message = AsyncMock(return_value=rag_return)

                with patch("app.services.chat_service.RAGChatEngine", return_value=mock_rag):
                    service = ChatService(db_session)
                    service.rag_engine = mock_rag

                    request = ChatRequest(
                        facility_id=facility.id,
                        message="チェックアウトは何時？",
                        language="ja",
                    )
                    response = await service.process_chat_message(request=request)

                mock_report.assert_called_once()
                mock_rag.process_message.assert_called_once()
                assert response.message.content == "RAG応答"

