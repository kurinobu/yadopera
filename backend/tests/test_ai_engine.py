"""
RAG統合型AI対話エンジンテスト
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import time
from app.ai.engine import RAGChatEngine
from app.models.faq import FAQ
from app.models.facility import Facility
from app.schemas.chat import EscalationInfo, RAGEngineResponse


class TestRAGEngine:
    """RAG統合型AI対話エンジンテスト"""

    def test_build_context_includes_wifi_password_when_set(self):
        """施設に WiFi パスワードがある場合、RAG コンテキストに含まれる（ゲスト回答用・公開 API とは別経路）"""
        facility = Facility(
            name="Ctx Hotel",
            slug="ctx-wifi-has-pw",
            email="ctx@example.com",
            wifi_ssid="Guest-Net",
            wifi_password="s3cret-wifi",
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True,
        )
        engine = RAGChatEngine(MagicMock())
        ctx = engine._build_context(facility, [], "WiFi password?", language="en")
        assert "Guest-Net" in ctx
        assert "s3cret-wifi" in ctx

    def test_build_context_wifi_password_not_set_placeholder(self):
        """パスワード未設定時は Not set のみ（捏造を促さない）"""
        facility = Facility(
            name="Ctx Hotel 2",
            slug="ctx-wifi-no-pw",
            email="ctx2@example.com",
            wifi_ssid="Open-Net",
            wifi_password=None,
            check_in_time=time(15, 0),
            check_out_time=time(11, 0),
            is_active=True,
        )
        engine = RAGChatEngine(MagicMock())
        ctx = engine._build_context(facility, [], "WiFi?", language="ja")
        assert "Open-Net" in ctx
        assert "Not set" in ctx
    
    @pytest.mark.asyncio
    @patch('app.ai.engine.generate_embedding')
    @patch('app.ai.engine.search_similar_faqs')
    @patch('app.ai.engine.OpenAIClient')
    async def test_process_message_success(
        self,
        mock_openai_client_class,
        mock_search_faqs,
        mock_generate_embedding,
        db_session,
        test_facility,
    ):
        """メッセージ処理成功テスト"""
        # search_similar_faqs の後に DB から再読込するため、同じ FAQ をセッション上に載せる
        faq_in_db = FAQ(
            facility_id=test_facility.id,
            category="basic",
            intent_key="basic_checkout_time",
            priority=5,
            is_active=True,
        )
        db_session.add(faq_in_db)
        await db_session.flush()
        await db_session.refresh(faq_in_db)

        # モック設定
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_search_faqs.return_value = [faq_in_db]
        
        mock_client = AsyncMock()
        mock_client.generate_response = AsyncMock(return_value="Check-out is by 11:00 AM.")
        mock_openai_client_class.return_value = mock_client
        
        # エンジン初期化
        engine = RAGChatEngine(db_session)
        
        # テスト実行
        response = await engine.process_message(
            message="What time is check-out?",
            facility_id=test_facility.id,
            session_id="test-session-1",
            language="en"
        )
        
        # アサーション（RAGEngineResponse は session_id を含まない中間形式）
        assert response.response == "Check-out is by 11:00 AM."
        assert response.ai_confidence == Decimal("0.7")  # 暫定値
        assert len(response.matched_faq_ids) > 0
        assert isinstance(response.escalation, EscalationInfo)
    
    @pytest.mark.asyncio
    @patch('app.ai.engine.generate_embedding')
    @patch('app.ai.engine.search_similar_faqs')
    @patch('app.ai.engine.OpenAIClient')
    async def test_process_message_embedding_failure(
        self,
        mock_openai_client_class,
        mock_search_faqs,
        mock_generate_embedding,
        db_session,
        test_facility
    ):
        """埋め込み生成失敗時のテスト"""
        # モック設定（埋め込み生成失敗）
        mock_generate_embedding.return_value = []
        mock_search_faqs.return_value = []
        
        mock_client = AsyncMock()
        mock_client.generate_response = AsyncMock(return_value="I'm sorry, I couldn't find relevant information.")
        mock_openai_client_class.return_value = mock_client
        
        # エンジン初期化
        engine = RAGChatEngine(db_session)
        
        # テスト実行
        response = await engine.process_message(
            message="Test question",
            facility_id=test_facility.id,
            session_id="test-session-2",
            language="en"
        )
        
        # アサーション（埋め込み失敗でも処理は続行）
        assert response.response is not None
    
    @pytest.mark.asyncio
    @patch('app.ai.engine.generate_embedding')
    @patch('app.ai.engine.search_similar_faqs')
    @patch('app.ai.engine.OpenAIClient')
    async def test_process_message_facility_not_found(
        self,
        mock_openai_client_class,
        mock_search_faqs,
        mock_generate_embedding,
        db_session
    ):
        """施設が見つからない場合のテスト"""
        # モック設定
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_search_faqs.return_value = []
        
        mock_client = AsyncMock()
        mock_openai_client_class.return_value = mock_client
        
        # エンジン初期化
        engine = RAGChatEngine(db_session)
        
        # テスト実行（存在しない施設ID）— 例外は捕捉されフォールバック応答になる
        response = await engine.process_message(
            message="Test question",
            facility_id=99999,  # 存在しない施設ID
            session_id="test-session-3",
            language="en"
        )
        assert isinstance(response, RAGEngineResponse)
        assert response.escalation.needed is True
        assert response.escalation.trigger_type == "error"
    
    @pytest.mark.asyncio
    @patch('app.ai.engine.generate_embedding')
    @patch('app.ai.engine.search_similar_faqs')
    @patch('app.ai.engine.OpenAIClient')
    async def test_process_message_openai_error(
        self,
        mock_openai_client_class,
        mock_search_faqs,
        mock_generate_embedding,
        db_session,
        test_facility
    ):
        """OpenAI APIエラー時のフォールバックテスト"""
        # モック設定
        mock_generate_embedding.return_value = [0.1] * 1536
        mock_search_faqs.return_value = []
        
        mock_client = AsyncMock()
        mock_client.generate_response = AsyncMock(side_effect=Exception("OpenAI API error"))
        mock_openai_client_class.return_value = mock_client
        
        # エンジン初期化
        engine = RAGChatEngine(db_session)
        
        # テスト実行
        response = await engine.process_message(
            message="Test question",
            facility_id=test_facility.id,
            session_id="test-session-4",
            language="en"
        )
        
        # アサーション（エラー時はフォールバックレスポンス）
        assert response.escalation.needed is True
        assert response.escalation.trigger_type == "error"

