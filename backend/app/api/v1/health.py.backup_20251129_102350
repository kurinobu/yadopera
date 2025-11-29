"""
ヘルスチェックエンドポイント
"""

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import text
from typing import Optional

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    database: str
    redis: str = "unknown"


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(db: Optional[AsyncSession] = Depends(get_db)):
    """
    ヘルスチェックエンドポイント
    データベース接続とRedis接続を確認
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown"
    }
    
    # データベース接続確認
    try:
        if db:
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            health_status["database"] = "connected"
        else:
            health_status["database"] = "not_checked"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis接続確認（オプション）
    try:
        from app.redis_client import redis_client
        if redis_client:
            await redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "not_configured"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        # Redisエラーは致命的ではないため、ステータスは変更しない
    
    return HealthResponse(**health_status)

