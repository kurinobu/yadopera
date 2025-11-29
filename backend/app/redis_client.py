"""
Redis接続設定
Redisへの非同期接続を管理
"""

from redis.asyncio import ConnectionPool, Redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis接続プール作成
pool = ConnectionPool.from_url(
    settings.redis_url,
    max_connections=10,  # 最大接続数
    decode_responses=True,  # レスポンスを自動デコード
)

# Redisクライアント作成
redis_client = Redis(connection_pool=pool)


async def get_redis() -> Redis:
    """
    Redisクライアント取得（依存性注入用）
    """
    return redis_client


async def check_redis_connection() -> bool:
    """
    Redis接続確認
    """
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection check failed: {e}")
        return False


async def close_redis():
    """
    Redis接続を閉じる
    """
    await redis_client.close()
    await pool.disconnect()
    logger.info("Redis connection closed")

