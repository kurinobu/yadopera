"""
データベース接続設定
PostgreSQL（pgvector拡張）への非同期接続を管理
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# データベースURLを非同期用に変換
# postgresql:// -> postgresql+asyncpg://
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not database_url.startswith("postgresql+asyncpg://"):
    # 既にasyncpg形式でない場合、追加
    if "postgresql" in database_url and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)

# 非同期エンジン作成
engine = create_async_engine(
    database_url,
    pool_size=20,  # 接続プールサイズ
    max_overflow=10,  # オーバーフロー接続数
    pool_pre_ping=True,  # 接続有効性チェック
    pool_recycle=3600,  # 1時間で接続再生成
    echo=settings.debug,  # SQLログ出力（デバッグモード時のみ）
)

# 非同期セッション作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    データベースセッション取得（依存性注入用）
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    データベース初期化（テーブル作成）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db():
    """
    データベース接続を閉じる
    """
    await engine.dispose()
    logger.info("Database connection closed")


async def check_db_connection() -> bool:
    """
    データベース接続確認
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

