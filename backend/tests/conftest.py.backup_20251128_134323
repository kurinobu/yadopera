"""
pytest設定ファイル
テスト用のフィクスチャを定義
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password


# テスト用データベースURL（メモリ内SQLite）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# テスト用エンジン作成
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
)


@pytest.fixture(scope="function")
async def db_session():
    """
    テスト用データベースセッション
    各テスト関数ごとに新しいセッションを作成
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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

