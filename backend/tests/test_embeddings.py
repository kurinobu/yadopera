"""
埋め込みベクトル生成テスト
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.ai.embeddings import generate_embedding, generate_faq_embedding
from app.models.faq import FAQ


class TestEmbeddings:
    """埋め込みベクトル生成テスト"""
    
    @pytest.mark.asyncio
    @patch('app.ai.embeddings.OpenAIClient')
    async def test_generate_embedding_success(self, mock_openai_client_class):
        """埋め込みベクトル生成成功テスト"""
        # モック設定
        mock_client = AsyncMock()
        mock_client.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        mock_openai_client_class.return_value = mock_client
        
        # テスト実行
        embedding = await generate_embedding("Test question")
        
        # アサーション
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
        mock_client.generate_embedding.assert_called_once_with("Test question")
    
    @pytest.mark.asyncio
    @patch('app.ai.embeddings.OpenAIClient')
    async def test_generate_embedding_failure(self, mock_openai_client_class):
        """埋め込みベクトル生成失敗テスト"""
        # モック設定（エラー時は空リストを返す）
        mock_client = AsyncMock()
        mock_client.generate_embedding = AsyncMock(return_value=[])
        mock_openai_client_class.return_value = mock_client
        
        # テスト実行
        embedding = await generate_embedding("Test question")
        
        # アサーション
        assert embedding == []
    
    @pytest.mark.asyncio
    @patch('app.ai.embeddings.generate_embedding')
    async def test_generate_faq_embedding(self, mock_generate_embedding):
        """FAQ埋め込みベクトル生成テスト"""
        # モック設定
        mock_generate_embedding.return_value = [0.1] * 1536
        
        # テスト用FAQ作成
        faq = FAQ(
            id=1,
            facility_id=1,
            category="basic",
            language="en",
            question="What time is check-in?",
            answer="Check-in is from 3pm to 10pm.",
            priority=5,
            is_active=True
        )
        
        # テスト実行
        embedding = await generate_faq_embedding(faq)
        
        # アサーション
        assert len(embedding) == 1536
        # 質問と回答が結合されて埋め込み生成されることを確認
        mock_generate_embedding.assert_called_once_with(
            "What time is check-in? Check-in is from 3pm to 10pm."
        )
    
    @pytest.mark.asyncio
    @patch('app.ai.embeddings.generate_embedding')
    async def test_generate_faq_embedding_empty(self, mock_generate_embedding):
        """FAQ埋め込みベクトル生成失敗テスト（空リスト返却）"""
        # モック設定（エラー時は空リストを返す）
        mock_generate_embedding.return_value = []
        
        # テスト用FAQ作成
        faq = FAQ(
            id=1,
            facility_id=1,
            category="basic",
            language="en",
            question="Test question",
            answer="Test answer",
            priority=5,
            is_active=True
        )
        
        # テスト実行
        embedding = await generate_faq_embedding(faq)
        
        # アサーション
        assert embedding == []


