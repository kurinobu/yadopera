"""
事業者向けヘルプシステムAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.operator_faq_service import OperatorFaqService
from app.services.operator_help_chat_service import OperatorHelpChatService
from app.schemas.help import (
    FaqListResponse,
    FaqSearchResponse,
    FaqResponse,
    ChatRequest,
    ChatResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/help", tags=["help"])


@router.get("/faqs", response_model=FaqListResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="カテゴリフィルタ（setup, qrcode, faq_management等）"),
    language: str = Query('ja', regex='^(ja|en)$', description="言語コード"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ一覧取得
    
    - **category**: カテゴリフィルタ（setup, qrcode, faq_management等）
    - **language**: 言語コード（ja, en）
    
    認証必須。
    """
    try:
        service = OperatorFaqService(db)
        
        # FAQ取得
        faqs_data = await service.get_faqs(
            language=language,
            category=category
        )
        
        # カテゴリ一覧取得
        categories_data = await service.get_categories(language=language)
        categories = [c['category'] for c in categories_data]
        
        # レスポンス構築
        faqs = [
            FaqResponse(
                id=faq['id'],
                category=faq['category'],
                question=faq['question'],
                answer=faq['answer'],
                keywords=faq.get('keywords'),
                related_url=faq.get('related_url'),
                display_order=faq['display_order']
            )
            for faq in faqs_data
        ]
        
        return FaqListResponse(
            faqs=faqs,
            total=len(faqs),
            categories=categories
        )
    
    except Exception as e:
        logger.error(f"Get FAQs error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="FAQの取得に失敗しました")


@router.get("/search", response_model=FaqSearchResponse)
async def search_faqs(
    q: str = Query(..., min_length=2, max_length=100, description="検索クエリ"),
    language: str = Query('ja', regex='^(ja|en)$', description="言語コード"),
    limit: int = Query(10, ge=1, le=50, description="取得件数上限"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ検索
    
    - **q**: 検索クエリ（2文字以上）
    - **language**: 言語コード（ja, en）
    - **limit**: 取得件数上限（1-50）
    
    認証必須。
    """
    try:
        service = OperatorFaqService(db)
        
        # FAQ検索
        results_data = await service.search_faqs(
            query=q,
            language=language,
            limit=limit
        )
        
        # レスポンス構築
        results = [
            FaqResponse(
                id=result['id'],
                category=result['category'],
                question=result['question'],
                answer=result['answer'],
                keywords=result.get('keywords'),
                related_url=result.get('related_url'),
                display_order=result['display_order']
            )
            for result in results_data
        ]
        
        return FaqSearchResponse(
            results=results,
            total=len(results),
            query=q
        )
    
    except Exception as e:
        logger.error(f"Search FAQs error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="FAQ検索に失敗しました")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AIヘルプチャット
    
    - **message**: ユーザーメッセージ（1-500文字）
    - **language**: 言語コード（ja, en）
    
    認証必須。
    """
    try:
        service = OperatorHelpChatService(db)
        
        # チャット処理
        response_data = await service.process_message(
            message=request.message,
            language=request.language,
            operator_id=current_user.id
        )
        
        return ChatResponse(
            response=response_data['response'],
            related_faqs=response_data['related_faqs'],
            related_url=response_data['related_url'],
            timestamp=response_data['timestamp']
        )
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="チャット処理に失敗しました")

