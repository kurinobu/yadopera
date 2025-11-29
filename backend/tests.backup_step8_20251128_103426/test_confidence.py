"""
信頼度スコア計算テスト
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai.confidence import calculate_confidence
from app.models.faq import FAQ


class TestConfidence:
    """信頼度スコア計算テスト"""
    
    @pytest.fixture
    def mock_faq(self):
        """モックFAQ"""
        faq = FAQ(
            id=1,
            facility_id=1,
            category="basic",
            language="en",
            question="What time is check-in?",
            answer="Check-in is from 3pm to 10pm.",
            priority=5,
            is_active=True,
            created_by=None  # テンプレートFAQ
        )
        return faq
    
    @pytest.fixture
    def mock_custom_faq(self):
        """モックカスタムFAQ"""
        faq = FAQ(
            id=2,
            facility_id=1,
            category="basic",
            language="en",
            question="Custom question",
            answer="Custom answer",
            priority=5,
            is_active=True,
            created_by=1  # カスタムFAQ
        )
        return faq
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_base_confidence(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """基本信頼度スコアテスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="This is a test response.",
            similar_faqs=[],
            question="Test question",
            facility_id=1,
            db=db_session
        )
        
        # 基本信頼度は0.7
        assert confidence == Decimal("0.7")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_short_response_penalty(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """短い回答のペナルティテスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="Short",  # 20文字未満
            similar_faqs=[],
            question="Test question",
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 - 0.2ペナルティ = 0.5
        assert confidence == Decimal("0.5")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_uncertain_phrase_penalty(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """不確実性ワード検出ペナルティテスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="I'm not sure about that.",
            similar_faqs=[],
            question="Test question",
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 - 0.15ペナルティ = 0.55
        assert confidence == Decimal("0.55")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_proper_noun_bonus(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """固有名詞ボーナステスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="This is a test response.",
            similar_faqs=[],
            question="Where is Tokyo Station?",  # 固有名詞含む
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 + 0.1ボーナス = 0.8
        assert confidence == Decimal("0.8")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_number_bonus(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """数値ボーナステスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="This is a test response.",
            similar_faqs=[],
            question="What time is check-in at 3pm?",  # 数値含む
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 + 0.1ボーナス = 0.8
        assert confidence == Decimal("0.8")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_custom_faq_bonus(self, mock_generate_embedding, mock_search_patterns, db_session, mock_custom_faq):
        """カスタムFAQボーナステスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="This is a test response.",
            similar_faqs=[mock_custom_faq],
            question="Test question",
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 + 0.15（FAQ類似度）+ 0.2（カスタムFAQ）= 1.05 → 1.0（クリップ）
        assert confidence == Decimal("1.0")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_confidence_clipping(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """信頼度スコアのクリッピングテスト（0.0-1.0）"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        # 非常に短い回答 + 不確実性ワード
        confidence = await calculate_confidence(
            response_text="Maybe",  # 短い + 不確実性ワード
            similar_faqs=[],
            question="Test",
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 - 0.2（短い）- 0.15（不確実性）= 0.35
        # ただし、クリップされて0.0以上になる
        assert confidence >= Decimal("0.0")
        assert confidence <= Decimal("1.0")
    
    @pytest.mark.asyncio
    @patch('app.ai.confidence.search_similar_patterns')
    @patch('app.ai.confidence.generate_embedding')
    async def test_multiple_penalties(self, mock_generate_embedding, mock_search_patterns, db_session, mock_faq):
        """複数のペナルティが適用されるテスト"""
        # モック設定
        mock_generate_embedding.return_value = []
        mock_search_patterns.return_value = []
        
        confidence = await calculate_confidence(
            response_text="Maybe",  # 短い + 不確実性ワード
            similar_faqs=[],
            question="Test question",
            facility_id=1,
            db=db_session
        )
        
        # 基本0.7 - 0.2（短い）- 0.15（不確実性）= 0.35
        assert confidence == Decimal("0.35")

