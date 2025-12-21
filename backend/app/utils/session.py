"""
セッション管理ユーティリティ
セッション有効期限の判定を行う
"""

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation
from app.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


async def is_session_valid(
    session_id: str,
    db: AsyncSession
) -> bool:
    """
    セッションが有効かチェック（防止策1: started_atベースの固定有効期限）
    
    Args:
        session_id: セッションID
        db: データベースセッション
    
    Returns:
        bool: セッションが有効な場合True、無効な場合False
    """
    # 1. Redisキャッシュ確認（高速化）
    cache_key = f"session:{session_id}"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return True
    except Exception as e:
        logger.warning(f"Redis cache check failed: {e}")
        # Redisエラー時はデータベースで確認を続行
    
    # 2. データベース確認
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if conversation is None:
        return False
    
    # 3. started_atから24時間以内かチェック（固定有効期限）
    now = datetime.utcnow()
    session_expires_at = conversation.started_at + timedelta(hours=24)
    
    if now > session_expires_at:
        # セッション無効化（ended_atを設定）
        conversation.ended_at = now
        await db.commit()
        logger.info(f"Session expired: session_id={session_id}, started_at={conversation.started_at}, expires_at={session_expires_at}")
        return False
    
    # 4. Redisにキャッシュ（残り有効期限をTTLとして設定）
    remaining_seconds = int((session_expires_at - now).total_seconds())
    if remaining_seconds > 0:
        try:
            await redis_client.setex(
                cache_key,
                remaining_seconds,
                "1"
            )
        except Exception as e:
            logger.warning(f"Redis cache set failed: {e}")
            # Redisエラー時は続行（データベースで判定可能）
    
    return True

