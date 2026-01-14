"""
ヘルプシステムAPIテスト
"""
import pytest
from fastapi import status


class TestHelpAPI:
    """ヘルプシステムAPIテスト"""

    @pytest.mark.asyncio
    async def test_get_faqs_success(self, client, auth_headers):
        """FAQ一覧取得成功テスト"""
        response = await client.get(
            "/api/v1/help/faqs",
            headers=auth_headers,
            params={"language": "ja"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "faqs" in data
        assert "total" in data
        assert "categories" in data
        assert isinstance(data["faqs"], list)
        assert isinstance(data["categories"], list)

    @pytest.mark.asyncio
    async def test_get_faqs_with_category(self, client, auth_headers):
        """カテゴリフィルタ付きFAQ一覧取得テスト"""
        response = await client.get(
            "/api/v1/help/faqs",
            headers=auth_headers,
            params={"language": "ja", "category": "setup"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "faqs" in data
        # カテゴリがsetupのFAQのみが返されることを確認
        if len(data["faqs"]) > 0:
            assert all(faq["category"] == "setup" for faq in data["faqs"])

    @pytest.mark.asyncio
    async def test_get_faqs_unauthorized(self, client):
        """認証なしでのFAQ一覧取得テスト"""
        response = await client.get(
            "/api/v1/help/faqs",
            params={"language": "ja"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_search_faqs_success(self, client, auth_headers):
        """FAQ検索成功テスト"""
        response = await client.get(
            "/api/v1/help/search",
            headers=auth_headers,
            params={"q": "アカウント", "language": "ja"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_search_faqs_short_query(self, client, auth_headers):
        """短い検索クエリテスト（2文字未満）"""
        response = await client.get(
            "/api/v1/help/search",
            headers=auth_headers,
            params={"q": "a", "language": "ja"}
        )

        # バリデーションエラーが返されることを確認
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_search_faqs_unauthorized(self, client):
        """認証なしでのFAQ検索テスト"""
        response = await client.get(
            "/api/v1/help/search",
            params={"q": "アカウント", "language": "ja"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires OpenAI API key")
    async def test_chat_success(self, client, auth_headers):
        """AIチャット成功テスト（スキップ）"""
        # OpenAI APIキーが必要なためスキップ
        # 統合テスト環境で実行する
        response = await client.post(
            "/api/v1/help/chat",
            headers=auth_headers,
            json={
                "message": "アカウント作成の方法を教えてください",
                "language": "ja"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "related_faqs" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, client, auth_headers):
        """空のメッセージでのチャットテスト"""
        response = await client.post(
            "/api/v1/help/chat",
            headers=auth_headers,
            json={
                "message": "",
                "language": "ja"
            }
        )

        # バリデーションエラーが返されることを確認
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_chat_unauthorized(self, client):
        """認証なしでのチャットテスト"""
        response = await client.post(
            "/api/v1/help/chat",
            json={
                "message": "アカウント作成の方法を教えてください",
                "language": "ja"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_faqs_english(self, client, auth_headers):
        """英語でのFAQ一覧取得テスト"""
        response = await client.get(
            "/api/v1/help/faqs",
            headers=auth_headers,
            params={"language": "en"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "faqs" in data
        # 英語のFAQが返されることを確認
        if len(data["faqs"]) > 0:
            # 質問文が英語であることを確認（簡易チェック）
            assert isinstance(data["faqs"][0]["question"], str)

