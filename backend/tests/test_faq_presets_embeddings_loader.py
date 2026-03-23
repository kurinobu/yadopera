"""
FAQプリセット埋め込みローダー単体テスト（Phase B B9）
get_preset_embedding のキー存在時・キー無し・ファイル無し（空マップ）を検証する。
"""

import pytest
from unittest.mock import patch

from app.data.faq_presets_embeddings_constants import (
    EMBEDDING_DIMENSION,
    EMBEDDINGS_JSON_PATH,
)
from app.data import faq_presets_embeddings_loader as loader_module


class TestGetPresetEmbedding:
    """get_preset_embedding の単体テスト"""

    def test_key_exists_returns_1536_dim_list(self):
        """キーが存在するとき、1536次元のfloatリストが返る（faq_presets_embeddings.json が存在する前提）"""
        if not EMBEDDINGS_JSON_PATH.exists():
            pytest.skip("faq_presets_embeddings.json not found (run B6 first)")
        result = loader_module.get_preset_embedding("basic_quiet_hours", "ja")
        assert result is not None
        assert len(result) == EMBEDDING_DIMENSION
        assert all(isinstance(x, (int, float)) for x in result)

    def test_key_missing_returns_none(self):
        """存在しないキーのとき None が返る"""
        result = loader_module.get_preset_embedding("__nonexistent_intent_key__", "ja")
        assert result is None

    def test_empty_map_returns_none(self):
        """ファイルが無い（空マップ）のとき None が返る"""
        with patch.object(loader_module, "_embeddings_map", {}):
            result = loader_module.get_preset_embedding("basic_quiet_hours", "ja")
        assert result is None


class TestCreateFaqUsesPrecomputedEmbedding:
    """create_faq で事前計算embeddingが渡された場合に generate_embedding が呼ばれないことを検証（B9）。
    Docker で全件パスさせるには USE_POSTGRES_TEST=true と TEST_DATABASE_URL=postgresql+asyncpg://...@postgres:5432/yadopera を指定して実行する。"""

    @pytest.mark.asyncio
    @patch("app.services.faq_service.generate_embedding")
    async def test_create_faq_with_precomputed_embedding_does_not_call_api(
        self, mock_generate_embedding, db_session
    ):
        """翻訳に事前計算embedding（1536次元）が含まれる場合、generate_embedding が呼ばれない"""
        from app.core.security import hash_password
        from app.models.facility import Facility
        from app.models.user import User
        from app.schemas.faq import FAQRequest, FAQTranslationRequest
        from app.services.faq_service import FAQService

        facility = Facility(
            name="Test Facility B9",
            slug="test-facility-b9",
            email="b9@example.com",
            plan_type="Mini",
            language_limit=2,
            is_active=True,
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)

        user = User(
            facility_id=facility.id,
            email="user-b9@example.com",
            password_hash=hash_password("testpass"),
            full_name="Test User B9",
            role="staff",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        precomputed = [0.1] * EMBEDDING_DIMENSION
        request = FAQRequest(
            category="basic",
            translations=[
                FAQTranslationRequest(
                    language="ja",
                    question="静かにしてください",
                    answer="22時以降は静かにご利用ください。",
                    embedding=precomputed,
                )
            ],
            priority=1,
        )

        service = FAQService(db_session)
        await service.create_faq(
            facility_id=facility.id,
            request=request,
            user_id=user.id,
        )

        mock_generate_embedding.assert_not_called()
