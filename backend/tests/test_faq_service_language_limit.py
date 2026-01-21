"""
FAQサービスの言語数制限バリデーションテスト
"""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.facility import Facility
from app.models.faq import FAQ
from app.models.faq_translation import FAQTranslation
from app.models.user import User
from app.services.faq_service import FAQService
from app.schemas.faq import FAQRequest, FAQUpdateRequest, FAQTranslationRequest


class TestFAQServiceLanguageLimit:
    """FAQサービスの言語数制限バリデーションテスト"""
    
    @pytest.fixture
    async def test_facility_free(self, db_session: AsyncSession):
        """Freeプランのテスト用施設（言語数制限: 1）"""
        facility = Facility(
            name="Test Hotel Free",
            slug="test-hotel-free",
            email="test-free@example.com",
            plan_type="Free",
            language_limit=1,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_mini(self, db_session: AsyncSession):
        """Miniプランのテスト用施設（言語数制限: 2）"""
        facility = Facility(
            name="Test Hotel Mini",
            slug="test-hotel-mini",
            email="test-mini@example.com",
            plan_type="Mini",
            language_limit=2,
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    @pytest.fixture
    async def test_facility_premium(self, db_session: AsyncSession):
        """Premiumプランのテスト用施設（言語数制限: 無制限）"""
        facility = Facility(
            name="Test Hotel Premium",
            slug="test-hotel-premium",
            email="test-premium@example.com",
            plan_type="Premium",
            language_limit=None,  # 無制限
            is_active=True
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)
        return facility
    
    async def _create_test_user(self, db_session: AsyncSession, facility_id: int, email: str):
        """テスト用ユーザーを作成するヘルパー関数"""
        from app.core.security import hash_password
        user = User(
            facility_id=facility_id,
            email=email,
            password_hash=hash_password("testpassword123"),
            full_name="Test User",
            role="staff",
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user
    
    @pytest.fixture
    async def existing_faq_ja(self, db_session: AsyncSession, test_facility_free):
        """既存のFAQ（日本語）を作成"""
        faq = FAQ(
            facility_id=test_facility_free.id,
            category="basic",
            intent_key="basic_test",
            priority=5,
            is_active=True,
            created_by=1
        )
        db_session.add(faq)
        await db_session.flush()
        
        translation = FAQTranslation(
            faq_id=faq.id,
            language="ja",
            question="テスト質問",
            answer="テスト回答",
            embedding=None
        )
        db_session.add(translation)
        await db_session.flush()
        await db_session.commit()
        await db_session.refresh(faq)
        return faq
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_create_faq_within_limit(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_free
    ):
        """テスト1: 言語制限に達していない場合の新規登録 - 成功"""
        mock_generate_embedding.return_value = [0.1] * 1536
        
        user = await self._create_test_user(db_session, test_facility_free.id, "test-user-1@example.com")
        
        service = FAQService(db_session)
        request = FAQRequest(
            category="basic",
            translations=[
                FAQTranslationRequest(language="ja", question="テスト質問", answer="テスト回答")
            ],
            priority=5
        )
        
        result = await service.create_faq(
            facility_id=test_facility_free.id,
            request=request,
            user_id=user.id
        )
        
        assert result is not None
        assert result.category == "basic"
        assert len(result.translations) == 1
        assert result.translations[0].language == "ja"
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_create_faq_existing_language(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_free,
        existing_faq_ja
    ):
        """テスト2: 言語制限に達している場合の新規登録（既存言語を使用） - 成功"""
        mock_generate_embedding.return_value = [0.1] * 1536
        
        user = await self._create_test_user(db_session, test_facility_free.id, "test-user-2@example.com")
        
        service = FAQService(db_session)
        request = FAQRequest(
            category="basic",
            translations=[
                FAQTranslationRequest(language="ja", question="別の質問", answer="別の回答")
            ],
            priority=5
        )
        
        # 既存の言語（ja）を使用しているため、制限に達していても成功する
        result = await service.create_faq(
            facility_id=test_facility_free.id,
            request=request,
            user_id=user.id
        )
        
        assert result is not None
        assert result.category == "basic"
        assert len(result.translations) == 1
        assert result.translations[0].language == "ja"
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_create_faq_exceeds_limit_new_language(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_free,
        existing_faq_ja
    ):
        """テスト3: 言語制限に達している場合の新規登録（新しい言語を追加） - エラー"""
        mock_generate_embedding.return_value = [0.1] * 1536
        
        user = await self._create_test_user(db_session, test_facility_free.id, "test-user-3@example.com")
        
        service = FAQService(db_session)
        request = FAQRequest(
            category="basic",
            translations=[
                FAQTranslationRequest(language="en", question="Test question", answer="Test answer")
            ],
            priority=5
        )
        
        # 新しい言語（en）を追加しようとすると、制限に達しているためエラー
        with pytest.raises(ValueError) as exc_info:
            await service.create_faq(
                facility_id=test_facility_free.id,
                request=request,
                user_id=user.id
            )
        
        assert "言語数制限に達しています" in str(exc_info.value)
        assert "1言語" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_create_faq_premium_unlimited(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_premium
    ):
        """テスト4: Premiumプラン（無制限）の場合の新規登録 - 成功"""
        user = await self._create_test_user(db_session, test_facility_premium.id, "test-user-premium@example.com")
        
        mock_generate_embedding.return_value = [0.1] * 1536
        
        service = FAQService(db_session)
        request = FAQRequest(
            category="basic",
            translations=[
                FAQTranslationRequest(language="ja", question="テスト質問", answer="テスト回答"),
                FAQTranslationRequest(language="en", question="Test question", answer="Test answer"),
                FAQTranslationRequest(language="zh-TW", question="測試問題", answer="測試答案"),
                FAQTranslationRequest(language="fr", question="Question test", answer="Réponse test")
            ],
            priority=5
        )
        
        # Premiumプランは無制限なので、複数言語でも成功する
        result = await service.create_faq(
            facility_id=test_facility_premium.id,
            request=request,
            user_id=user.id
        )
        
        assert result is not None
        assert len(result.translations) == 4
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_update_faq_within_limit_new_language(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_mini
    ):
        """テスト5: 言語制限に達していない場合の更新（新しい言語を追加） - 成功"""
        # Miniプランの施設用のFAQを作成
        faq = FAQ(
            facility_id=test_facility_mini.id,
            category="basic",
            intent_key="basic_test_mini",
            priority=5,
            is_active=True,
            created_by=1
        )
        db_session.add(faq)
        await db_session.flush()
        
        translation = FAQTranslation(
            faq_id=faq.id,
            language="ja",
            question="テスト質問",
            answer="テスト回答",
            embedding=None
        )
        db_session.add(translation)
        await db_session.flush()
        await db_session.commit()
        
        mock_generate_embedding.return_value = [0.1] * 1536
        
        service = FAQService(db_session)
        request = FAQUpdateRequest(
            translations=[
                FAQTranslationRequest(language="ja", question="テスト質問更新", answer="テスト回答更新"),
                FAQTranslationRequest(language="en", question="Test question", answer="Test answer")
            ]
        )
        
        # Miniプランは2言語まで許可されているため、新しい言語（en）を追加できる
        result = await service.update_faq(
            faq_id=faq.id,
            facility_id=test_facility_mini.id,
            request=request,
            user_id=1
        )
        
        assert result is not None
        assert len(result.translations) == 2
        languages = {trans.language for trans in result.translations}
        assert "ja" in languages
        assert "en" in languages
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_update_faq_existing_language_update(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_free,
        existing_faq_ja
    ):
        """テスト6: 言語制限に達している場合の更新（既存言語を更新） - 成功"""
        mock_generate_embedding.return_value = [0.1] * 1536
        
        service = FAQService(db_session)
        request = FAQUpdateRequest(
            translations=[
                FAQTranslationRequest(language="ja", question="更新された質問", answer="更新された回答")
            ]
        )
        
        # 既存の言語（ja）を更新するだけなので、制限に達していても成功する
        result = await service.update_faq(
            faq_id=existing_faq_ja.id,
            facility_id=test_facility_free.id,
            request=request,
            user_id=1
        )
        
        assert result is not None
        assert len(result.translations) == 1
        assert result.translations[0].language == "ja"
        assert result.translations[0].question == "更新された質問"
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_update_faq_exceeds_limit_new_language(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_free,
        existing_faq_ja
    ):
        """テスト7: 言語制限に達している場合の更新（新しい言語を追加） - エラー"""
        mock_generate_embedding.return_value = [0.1] * 1536
        
        service = FAQService(db_session)
        request = FAQUpdateRequest(
            translations=[
                FAQTranslationRequest(language="ja", question="テスト質問", answer="テスト回答"),
                FAQTranslationRequest(language="en", question="Test question", answer="Test answer")
            ]
        )
        
        # 新しい言語（en）を追加しようとすると、制限に達しているためエラー
        with pytest.raises(ValueError) as exc_info:
            await service.update_faq(
                faq_id=existing_faq_ja.id,
                facility_id=test_facility_free.id,
                request=request,
                user_id=1
            )
        
        assert "言語数制限に達しています" in str(exc_info.value)
        assert "1言語" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('app.services.faq_service.generate_embedding')
    async def test_update_faq_premium_unlimited(
        self,
        mock_generate_embedding,
        db_session: AsyncSession,
        test_facility_premium
    ):
        """テスト8: Premiumプラン（無制限）の場合の更新（新しい言語を追加） - 成功"""
        # Premiumプランの施設用のFAQを作成
        faq = FAQ(
            facility_id=test_facility_premium.id,
            category="basic",
            intent_key="basic_test_premium",
            priority=5,
            is_active=True,
            created_by=1
        )
        db_session.add(faq)
        await db_session.flush()
        
        translation = FAQTranslation(
            faq_id=faq.id,
            language="ja",
            question="テスト質問",
            answer="テスト回答",
            embedding=None
        )
        db_session.add(translation)
        await db_session.flush()
        await db_session.commit()
        
        mock_generate_embedding.return_value = [0.1] * 1536
        
        service = FAQService(db_session)
        request = FAQUpdateRequest(
            translations=[
                FAQTranslationRequest(language="ja", question="テスト質問", answer="テスト回答"),
                FAQTranslationRequest(language="en", question="Test question", answer="Test answer"),
                FAQTranslationRequest(language="zh-TW", question="測試問題", answer="測試答案")
            ]
        )
        
        # Premiumプランは無制限なので、複数言語を追加しても成功する
        result = await service.update_faq(
            faq_id=faq.id,
            facility_id=test_facility_premium.id,
            request=request,
            user_id=1
        )
        
        assert result is not None
        assert len(result.translations) == 3
        languages = {trans.language for trans in result.translations}
        assert "ja" in languages
        assert "en" in languages
        assert "zh-TW" in languages

