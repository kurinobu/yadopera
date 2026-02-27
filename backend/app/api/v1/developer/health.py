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
from app.schemas.developer import (
    SystemHealthResponse,
    HealthStatusResponse,
    PhaseEHealthResponse,
    PhaseECheckItem,
)

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


@router.get("/phase-e", response_model=PhaseEHealthResponse)
async def phase_e_health(
    developer_payload: dict = Depends(get_current_developer),
):
    """
    Phase E: 従量課金メーター連携の動作検証（ステージング等で実行用）。
    stripe_service / chat_service / billing_period / config のインポートと挙動を確認する。
    開発者認証必須。
    """
    checks: list = []
    ok_count = 0
    ng_count = 0

    # 1. stripe_service
    try:
        from app.services.stripe_service import (
            report_usage_to_meter,
            get_meter_event_name,
            is_stripe_configured,
        )
        checks.append(PhaseECheckItem(name="stripe_service_import", ok=True))
        ok_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="stripe_service_import", ok=False, message=str(e)))
        ng_count += 1
        return PhaseEHealthResponse(ok_count=ok_count, ng_count=ng_count, all_ok=False, checks=checks)

    # 2. get_meter_event_name
    try:
        name = get_meter_event_name()
        ok = bool(name and isinstance(name, str))
        checks.append(PhaseECheckItem(name="get_meter_event_name", ok=ok, message=name if ok else "empty or not str"))
        if ok:
            ok_count += 1
        else:
            ng_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="get_meter_event_name", ok=False, message=str(e)))
        ng_count += 1

    # 3. is_stripe_configured
    try:
        configured = is_stripe_configured()
        checks.append(PhaseECheckItem(name="is_stripe_configured", ok=True, message=str(configured)))
        ok_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="is_stripe_configured", ok=False, message=str(e)))
        ng_count += 1

    # 4. report_usage_to_meter("") => False
    try:
        result = report_usage_to_meter("")
        ok = result is False
        checks.append(PhaseECheckItem(name="report_usage_empty_customer", ok=ok, message=f"result={result}"))
        if ok:
            ok_count += 1
        else:
            ng_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="report_usage_empty_customer", ok=False, message=str(e)))
        ng_count += 1

    # 5. ChatService._report_usage_to_stripe_if_needed
    try:
        from app.services.chat_service import ChatService
        ok = hasattr(ChatService, "_report_usage_to_stripe_if_needed")
        checks.append(PhaseECheckItem(name="chat_service_report_method", ok=ok))
        if ok:
            ok_count += 1
        else:
            ng_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="chat_service_report_method", ok=False, message=str(e)))
        ng_count += 1

    # 6. billing_period
    try:
        from app.utils.billing_period import calculate_billing_period
        checks.append(PhaseECheckItem(name="billing_period_import", ok=True))
        ok_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="billing_period_import", ok=False, message=str(e)))
        ng_count += 1

    # 7. config stripe_meter_event_name
    try:
        from app.core.config import settings
        val = getattr(settings, "stripe_meter_event_name", None)
        checks.append(PhaseECheckItem(name="config_meter_event_name", ok=True, message=str(val)))
        ok_count += 1
    except Exception as e:
        checks.append(PhaseECheckItem(name="config_meter_event_name", ok=False, message=str(e)))
        ng_count += 1

    return PhaseEHealthResponse(
        ok_count=ok_count,
        ng_count=ng_count,
        all_ok=(ng_count == 0),
        checks=checks,
    )

