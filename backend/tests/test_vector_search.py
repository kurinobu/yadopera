"""
pgvector検索テスト
"""

import os
import pytest
from unittest.mock import AsyncMock, patch
from app.ai.vector_search import search_similar_faqs, search_similar_patterns
from app.models.faq import FAQ
from app.models.question_pattern import QuestionPattern
from decimal import Decimal

# PostgreSQLテスト環境のチェック
USE_POSTGRES_TEST = os.getenv("USE_POSTGRES_TEST", "false").lower() == "true"


class TestVectorSearch:
    """pgvector検索テスト"""
    
    @pytest.fixture
    def mock_embedding(self):
        """モック埋め込みベクトル"""
        return [0.1] * 1536
    
    @pytest.mark.asyncio
    async def test_search_similar_faqs_empty_embedding(self, db_session):
        """空の埋め込みベクトルでの検索テスト"""
        result = await search_similar_faqs(
            facility_id=1,
            embedding=[],
            top_k=3,
            threshold=0.7,
            db=db_session
        )
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_similar_faqs_no_db(self):
        """データベースセッションなしでの検索テスト"""
        result = await search_similar_faqs(
            facility_id=1,
            embedding=[0.1] * 1536,
            top_k=3,
            threshold=0.7,
            db=None
        )
        
        assert result == []
    
    @pytest.mark.asyncio
    @pytest.mark.postgres
    @pytest.mark.skipif(not USE_POSTGRES_TEST, reason="pgvector is not available in SQLite test database. Use USE_POSTGRES_TEST=true to run this test.")
    async def test_search_similar_faqs_with_data(self, db_session, test_facility, mock_embedding):
        """データありでの類似FAQ検索テスト（PostgreSQL + pgvectorが必要）"""
        # このテストはPostgreSQL + pgvector環境で実行する必要がある
        # USE_POSTGRES_TEST=true で実行
        from app.models.faq import FAQ
        
        # テスト用FAQデータ作成
        faq = FAQ(
            facility_id=test_facility.id,
            question="What is the WiFi password?",
            answer="The WiFi password is guest123",
            category="basic",
            embedding=mock_embedding,
            is_active=True,
        )
        db_session.add(faq)
        await db_session.commit()
        
        # 類似FAQ検索実行
        result = await search_similar_faqs(
            facility_id=test_facility.id,
            embedding=mock_embedding,
            top_k=3,
            threshold=0.7,
            db=db_session
        )
        
        # 結果確認
        assert len(result) > 0
        assert result[0]["question"] == "What is the WiFi password?"
    
    @pytest.mark.asyncio
    async def test_search_similar_patterns_empty_embedding(self, db_session):
        """空の埋め込みベクトルでのパターン検索テスト"""
        result = await search_similar_patterns(
            facility_id=1,
            embedding=[],
            threshold=Decimal("0.85"),
            top_k=1,
            db=db_session
        )
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_similar_patterns_no_db(self):
        """データベースセッションなしでのパターン検索テスト"""
        result = await search_similar_patterns(
            facility_id=1,
            embedding=[0.1] * 1536,
            threshold=Decimal("0.85"),
            top_k=1,
            db=None
        )
        
        assert result == []
    
    @pytest.mark.asyncio
    @pytest.mark.postgres
    @pytest.mark.skipif(not USE_POSTGRES_TEST, reason="pgvector is not available in SQLite test database. Use USE_POSTGRES_TEST=true to run this test.")
    async def test_search_similar_patterns_with_data(self, db_session, test_facility, mock_embedding):
        """データありでの類似パターン検索テスト（PostgreSQL + pgvectorが必要）"""
        # このテストはPostgreSQL + pgvector環境で実行する必要がある
        # USE_POSTGRES_TEST=true で実行
        from app.models.question_pattern import QuestionPattern
        
        # テスト用質問パターンデータ作成
        pattern = QuestionPattern(
            facility_id=test_facility.id,
            pattern_embedding=mock_embedding,
            total_count=10,
            resolved_count=8,
            is_active=True,
        )
        db_session.add(pattern)
        await db_session.commit()
        
        # 類似パターン検索実行
        result = await search_similar_patterns(
            facility_id=test_facility.id,
            embedding=mock_embedding,
            threshold=Decimal("0.85"),
            top_k=1,
            db=db_session
        )
        
        # 結果確認
        assert len(result) > 0
        assert result[0]["total_count"] == 10
        assert result[0]["resolved_count"] == 8

