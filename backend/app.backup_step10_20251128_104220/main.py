from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    NotFoundException,
    DatabaseException,
    ServiceUnavailableException,
    AIException,
    VectorSearchException,
    EscalationException,
)
from app.database import check_db_connection, close_db
from app.redis_client import check_redis_connection, close_redis
from app.api.v1.router import api_router
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーション起動時・終了時の処理
    """
    # 起動時
    logger.info("Starting やどぺら API...")
    
    # データベース接続確認
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    
    if db_ok:
        logger.info("Database connection: OK")
    else:
        logger.warning("Database connection: FAILED")
    
    if redis_ok:
        logger.info("Redis connection: OK")
    else:
        logger.warning("Redis connection: FAILED")
    
    yield
    
    # 終了時
    logger.info("Shutting down やどぺら API...")
    await close_db()
    await close_redis()
    logger.info("やどぺら API shutdown complete")


app = FastAPI(
    title="やどぺら API",
    description="小規模宿泊施設向けAI多言語自動案内システム",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "やどぺら API v0.3",
        "status": "ok"
    }


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    データベースとRedisの接続状態を確認
    """
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    
    health_status = "ok" if (db_ok and redis_ok) else "degraded"
    
    return {
        "status": health_status,
        "database": "ok" if db_ok else "failed",
        "redis": "ok" if redis_ok else "failed",
    }


# グローバル例外ハンドラー登録
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """バリデーション例外ハンドラー"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": {
                    "field": exc.field,
                    **exc.details
                }
            }
        }
    )


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """認証例外ハンドラー"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """リソース未検出例外ハンドラー"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    """データベース例外ハンドラー"""
    logger.error(f"Database Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": exc.code,
                "message": "Database error occurred. Please try again later.",
                "details": exc.details
            }
        }
    )


@app.exception_handler(ServiceUnavailableException)
async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailableException):
    """サービス利用不可例外ハンドラー"""
    logger.error(f"Service Unavailable: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(AIException)
async def ai_exception_handler(request: Request, exc: AIException):
    """AI処理エラーハンドラー（v0.2追加）"""
    logger.error(
        f"AI Exception: {exc.message}",
        extra={
            "error_type": exc.error_type,
            "details": exc.details
        }
    )
    
    # OpenAI API障害時は503返却
    if exc.error_type in ["timeout", "rate_limit", "server_error"]:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "AI service is temporarily unavailable. Please try again later.",
                    "details": {
                        "service": "openai_api",
                        "error_type": exc.error_type,
                        **exc.details
                    }
                }
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(VectorSearchException)
async def vector_search_exception_handler(request: Request, exc: VectorSearchException):
    """pgvector検索エラーハンドラー（v0.2追加）"""
    logger.error(f"Vector Search Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": exc.code,
                "message": "Vector search failed. Please try again.",
                "details": exc.details
            }
        }
    )


@app.exception_handler(EscalationException)
async def escalation_exception_handler(request: Request, exc: EscalationException):
    """エスカレーション処理エラーハンドラー（v0.2追加）"""
    logger.error(f"Escalation Exception: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """アプリケーション基底例外ハンドラー"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """FastAPIバリデーションエラーハンドラー"""
    errors = exc.errors()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {
                    "errors": errors
                }
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """予期しないエラーハンドラー"""
    logger.critical(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {}
            }
        }
    )


# APIルーター登録（統合ルーターを使用）
app.include_router(api_router, prefix="/api/v1")

