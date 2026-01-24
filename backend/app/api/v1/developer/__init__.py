"""
開発者管理ページAPI
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .errors import router as errors_router
from .stats import router as stats_router
from .health import router as health_router

developer_router = APIRouter(prefix="/developer", tags=["developer"])

developer_router.include_router(auth_router, prefix="/auth")
developer_router.include_router(errors_router, prefix="/errors")
developer_router.include_router(stats_router, prefix="/stats")
developer_router.include_router(health_router, prefix="/health")

