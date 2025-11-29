"""
pgvector検索テスト
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.ai.vector_search import search_similar_faqs, search_similar_patterns
from app.models.faq import FAQ
from app.models.question_pattern import QuestionPattern
from decimal import Decimal


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
    @pytest.mark.skip(reason="pgvector is not available in SQLite test database")
    async def test_search_similar_faqs_with_data(self, db_session, test_facility, mock_embedding):
        """データありでの類似FAQ検索テスト（pgvectorが必要なためスキップ）"""
        # このテストはPostgreSQL + pgvector環境で実行する必要がある
        # SQLiteではスキップ
        pass
    
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
    @pytest.mark.skip(reason="pgvector is not available in SQLite test database")
    async def test_search_similar_patterns_with_data(self, db_session, test_facility, mock_embedding):
        """データありでの類似パターン検索テスト（pgvectorが必要なためスキップ）"""
        # このテストはPostgreSQL + pgvector環境で実行する必要がある
        # SQLiteではスキップ
        pass

