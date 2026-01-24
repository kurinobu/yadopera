"""
システムヘルスAPIエンドポイント
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone
from app.database import get_db, AsyncSessionLocal
from app.api.deps import get_current_developer
from app.schemas.developer import SystemHealthResponse, HealthStatusResponse

router = APIRouter()


@router.get("/system", response_model=SystemHealthResponse)
async def system_health(
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db)
):
    """
    システムヘルスチェック
    
    データベース、Redis、OpenAI APIの接続状態とレスポンスタイムを確認します。
    
    開発者認証必須。
    """
    health_status = {}
    
    # データベースチェック（非同期）
    try:
        start = time.time()
        result = await db.execute(text("SELECT 1"))
        result.scalar()  # 結果を取得（await不要：scalar()は同期的メソッド）
        db_time = (time.time() - start) * 1000
        health_status["database"] = HealthStatusResponse(
            status="ok",
            response_time_ms=round(db_time, 2)
        )
    except Exception as e:
        health_status["database"] = HealthStatusResponse(
            status="error",
            error=str(e)
        )
    
    # Redisチェック（非同期）
    try:
        from app.redis_client import redis_client
        start = time.time()
        await redis_client.ping()
        redis_time = (time.time() - start) * 1000
        health_status["redis"] = HealthStatusResponse(
            status="ok",
            response_time_ms=round(redis_time, 2)
        )
    except Exception as e:
        health_status["redis"] = HealthStatusResponse(
            status="error",
            error=str(e)
        )
    
    # OpenAI APIチェック（オプション、簡易チェック）
    # 実際のAPI呼び出しは行わず、設定の有無のみ確認
    try:
        from app.core.config import settings
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            # APIキーが設定されている場合はOKとみなす
            # 実際のAPI呼び出しはコストがかかるため、設定確認のみ
            health_status["openai_api"] = HealthStatusResponse(
                status="ok",
                response_time_ms=None
            )
        else:
            health_status["openai_api"] = HealthStatusResponse(
                status="not_configured",
                error="OpenAI API key not configured"
            )
    except Exception as e:
        health_status["openai_api"] = HealthStatusResponse(
            status="error",
            error=str(e)
        )
    
    return SystemHealthResponse(
        database=health_status["database"],
        redis=health_status["redis"],
        openai_api=health_status.get("openai_api")
    )

