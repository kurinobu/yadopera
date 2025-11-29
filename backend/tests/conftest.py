"""
pytest設定ファイル
テスト用のフィクスチャを定義
"""

import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password
from unittest.mock import AsyncMock, MagicMock, patch


# 環境変数でPostgreSQLテスト環境を有効化
USE_POSTGRES_TEST = os.getenv("USE_POSTGRES_TEST", "false").lower() == "true"

# 環境変数でOpenAI APIモックの使用を制御（ハイブリッドアプローチ）
# デフォルト: モックを使用（高速・低コスト）
# USE_OPENAI_MOCK=false: 実際のAPIを使用（統合テスト用）
USE_OPENAI_MOCK = os.getenv("USE_OPENAI_MOCK", "true").lower() == "true"

# テスト用データベースURL
if USE_POSTGRES_TEST:
    # PostgreSQL + pgvectorテスト環境
    # 環境変数TEST_DATABASE_URLが設定されている場合はそれを使用（ステージング環境用）
    # 設定されていない場合はローカルのPostgreSQLを使用
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://yadopera_user:yadopera_password@localhost:5433/yadopera_test"
    )
else:
    # SQLiteテスト環境（デフォルト）
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# テスト用エンジン作成
if USE_POSTGRES_TEST:
    # PostgreSQL用エンジン設定
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False,
    )
else:
    # SQLite用エンジン設定
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

# テスト用セッション作成
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def db_session():
    """
    テスト用データベースセッション
    各テスト関数ごとに新しいセッションを作成
    """
    # セットアップ: テーブル作成
    # ステージング環境（TEST_DATABASE_URLが設定されている場合）ではテーブル作成をスキップ
    # ローカル環境（TEST_DATABASE_URLが未設定）ではテーブルを作成
    if USE_POSTGRES_TEST:
        # PostgreSQL環境: pgvector拡張有効化 + テーブル作成
        async with test_engine.begin() as conn:
            # pgvector拡張有効化
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            # テーブル作成（ステージング環境では既に存在する可能性があるため、エラーを無視）
            try:
                await conn.run_sync(Base.metadata.create_all)
            except Exception:
                # テーブルが既に存在する場合は無視（ステージング環境）
                pass
    else:
        # SQLite環境: テーブル作成のみ
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # セッション作成とクリーンアップ
    session = TestSessionLocal()
    try:
        yield session
    finally:
        # セッションの明示的なクローズとロールバック
        try:
            # 未コミットのトランザクションをロールバック
            await session.rollback()
        except Exception:
            pass  # ロールバックエラーは無視（既にコミット済みまたはロールバック済みの場合）
        finally:
            try:
                await session.close()
            except Exception:
                pass  # クローズエラーは無視
    
    # テスト後のクリーンアップ: テーブル削除
    # ステージング環境（TEST_DATABASE_URLが設定されている場合）ではテーブル削除をスキップ
    # ローカル環境（TEST_DATABASE_URLが未設定）ではテーブルを削除
    if not os.getenv("TEST_DATABASE_URL"):
        # ローカル環境のみテーブル削除を実行
        try:
            if USE_POSTGRES_TEST:
                # PostgreSQL環境: テーブル削除（データベースは保持）
                async with test_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
            else:
                # SQLite環境: テーブル削除
                async with test_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass  # クリーンアップエラーは無視（テーブルが存在しない場合など）


@pytest.fixture(scope="function")
async def client(db_session):
    """
    テスト用FastAPIクライアント
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_facility(db_session: AsyncSession):
    """
    テスト用施設データ
    """
    from app.models.facility import Facility
    
    facility = Facility(
        name="Test Hotel",
        slug="test-hotel",
        email="test@example.com",
        phone="090-1234-5678",
        address="Test Address",
        is_active=True,
    )
    db_session.add(facility)
    await db_session.commit()
    await db_session.refresh(facility)
    return facility


@pytest.fixture
async def test_user(db_session: AsyncSession, test_facility):
    """
    テスト用ユーザーデータ
    """
    from app.models.user import User
    
    user = User(
        facility_id=test_facility.id,
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        full_name="Test User",
        role="staff",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# OpenAI API モックフィクスチャ（ハイブリッドアプローチ）
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """
    OpenAI APIクライアントのモックフィクスチャ
    ハイブリッドアプローチ: デフォルトでモックを使用、統合テストで実際のAPIを使用可能
    
    Returns:
        AsyncMock: OpenAI APIクライアントのモック
    """
    mock_client = AsyncMock()
    
    # デフォルトのモック動作
    mock_client.generate_response = AsyncMock(
        return_value="This is a mock AI response."
    )
    mock_client.generate_embedding = AsyncMock(
        return_value=[0.1] * 1536  # 1536次元の埋め込みベクトル
    )
    
    return mock_client


@pytest.fixture
def mock_embedding():
    """
    埋め込みベクトルのモックフィクスチャ
    
    Returns:
        List[float]: 1536次元の埋め込みベクトル
    """
    return [0.1] * 1536


@pytest.fixture
def mock_openai_patch(mock_openai_client):
    """
    OpenAI APIクライアントのパッチコンテキストマネージャー
    テストで明示的に使用する場合のフィクスチャ
    
    Usage:
        def test_something(mock_openai_patch):
            with mock_openai_patch:
                # テストコード
                pass
    """
    if not USE_OPENAI_MOCK:
        # 実際のAPIを使用する場合、パッチを返さない
        from contextlib import nullcontext
        return nullcontext()
    
    # モックを適用するモジュールのリスト
    modules_to_patch = [
        'app.ai.engine.OpenAIClient',
        'app.ai.embeddings.OpenAIClient',
        'app.ai.openai_client.OpenAIClient',
    ]
    
    # 複数のパッチを組み合わせたコンテキストマネージャー
    from contextlib import ExitStack
    
    class MultiPatch:
        def __init__(self, modules, mock_client):
            self.modules = modules
            self.mock_client = mock_client
            self.patches = []
            self.stack = ExitStack()
        
        def __enter__(self):
            for module_path in self.modules:
                try:
                    patch_obj = patch(module_path, return_value=self.mock_client)
                    self.patches.append(patch_obj)
                    self.stack.enter_context(patch_obj)
                except (ImportError, AttributeError):
                    pass
            return self
        
        def __exit__(self, *args):
            self.stack.close()
            return False
    
    return MultiPatch(modules_to_patch, mock_openai_client)

