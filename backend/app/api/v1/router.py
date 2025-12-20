"""
API v1 ルーター統合
全APIエンドポイントを統合して管理

統合されているルーター:
- auth: 認証API（ログイン、トークンリフレッシュ）
- session: 会話引き継ぎコードAPI
- facility: 施設情報API（公開）
- chat: チャットAPI（RAG統合型AI対話、会話履歴）
- admin.dashboard: ダッシュボードAPI（管理画面）
- admin.faqs: FAQ管理API（管理画面）
"""

from fastapi import APIRouter
from app.api.v1 import auth, session, facility, chat, health
from app.api.v1.admin import dashboard, faqs, faq_suggestions, overnight_queue, qr_code, escalations, feedback, facility as admin_facility

# API v1 ルーター作成
api_router = APIRouter()

# 各ルーターを統合
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(session.router, tags=["session"])
api_router.include_router(facility.router, tags=["facility"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(dashboard.router, tags=["admin"])
api_router.include_router(faqs.router, tags=["admin"])
api_router.include_router(faq_suggestions.router, tags=["admin"])
api_router.include_router(overnight_queue.router, tags=["admin"])
api_router.include_router(qr_code.router, tags=["admin"])
api_router.include_router(qr_code.router_list, tags=["admin"])
api_router.include_router(escalations.router, tags=["admin"])
api_router.include_router(feedback.router, tags=["admin"])
api_router.include_router(admin_facility.router, tags=["admin"])

