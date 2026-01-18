from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.router import api_router
from app.database import check_db_connection
from app.services.operator_faq_service import OperatorFaqService
from app.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションライフサイクル管理
    起動時と終了時の処理を定義
    """
    # 起動時処理
    logger.info("Starting up YadOPERA API...")
    
    # データベース接続確認
    try:
        db_connected = await check_db_connection()
        if not db_connected:
            logger.warning("Database connection check failed, skipping FAQ data update")
        else:
            logger.info("Database connection confirmed")
            
            # FAQデータ更新処理
            try:
                logger.info("Updating operator FAQ data...")
                from scripts.update_operator_faqs import update_operator_faqs
                await update_operator_faqs()
                logger.info("Operator FAQ data update completed")
                
                # キャッシュクリア
                try:
                    async with AsyncSessionLocal() as db:
                        faq_service = OperatorFaqService(db)
                        cleared_count = await faq_service.clear_faq_cache()
                        logger.info(f"Cleared {cleared_count} FAQ cache keys")
                except Exception as cache_error:
                    logger.warning(f"Failed to clear FAQ cache: {cache_error}")
                    
            except Exception as e:
                logger.error(f"Failed to update operator FAQ data: {e}", exc_info=True)
                # エラーが発生してもアプリケーションは起動する
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        # エラーが発生してもアプリケーションは起動する
    
    yield
    
    # 終了時処理
    logger.info("Shutting down YadOPERA API...")


app = FastAPI(
    title="YadOPERA API",
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
        "message": "YadOPERA API v0.3",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


# エラーハンドラー: HTTPException（アーキテクチャ設計書の標準エラーフォーマットに準拠）
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPExceptionエラーハンドラー
    アーキテクチャ設計書の標準エラーフォーマットに準拠
    """
    # エラーコードのマッピング
    error_code_map = {
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
        status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
    }
    
    error_code = error_code_map.get(exc.status_code, "INTERNAL_ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "details": {}
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    バリデーションエラーハンドラー
    アーキテクチャ設計書の標準エラーフォーマットに準拠
    """
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
    """
    予期しないエラーハンドラー
    アーキテクチャ設計書の標準エラーフォーマットに準拠
    """
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


# APIルーター登録
app.include_router(api_router, prefix="/api/v1")

