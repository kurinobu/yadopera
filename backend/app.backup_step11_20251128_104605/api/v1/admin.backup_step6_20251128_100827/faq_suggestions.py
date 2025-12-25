"""
FAQ提案APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.faq_suggestion import FAQSuggestionResponse, ApproveSuggestionRequest, FAQSuggestionListResponse
from app.services.faq_suggestion_service import FAQSuggestionService

router = APIRouter(prefix="/admin/faq-suggestions", tags=["admin", "faq-suggestions"])


@router.get("", response_model=FAQSuggestionListResponse)
async def get_faq_suggestions(
    status: Optional[str] = Query(None, description="ステータスフィルタ（pending/approved/rejected）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ提案一覧取得
    
    - **status**: ステータスフィルタ（オプション）
    
    JWT認証必須。現在のユーザーが所属する施設のFAQ提案を返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQ提案サービスでFAQ提案一覧取得
        suggestion_service = FAQSuggestionService(db)
        suggestions = await suggestion_service.get_suggestions(
            facility_id=facility_id,
            status=status
        )
        
        return FAQSuggestionListResponse(suggestions=suggestions, total=len(suggestions))
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ suggestions: {str(e)}"
        )


@router.post("/generate/{message_id}", response_model=FAQSuggestionResponse, status_code=status.HTTP_201_CREATED)
async def generate_faq_suggestion(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ提案生成（GPT-4o mini）
    
    - **message_id**: メッセージID（低評価回答または未解決質問）
    
    JWT認証必須。GPT-4o miniで回答文テンプレートとカテゴリを自動生成します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQ提案サービスでFAQ提案生成
        suggestion_service = FAQSuggestionService(db)
        suggestion = await suggestion_service.generate_suggestion(
            facility_id=facility_id,
            message_id=message_id
        )
        
        return suggestion
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating FAQ suggestion: {str(e)}"
        )


@router.post("/{suggestion_id}/approve", response_model=FAQSuggestionResponse)
async def approve_faq_suggestion(
    suggestion_id: int,
    request: ApproveSuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提案承認（FAQ作成）
    
    - **suggestion_id**: 提案ID（パスパラメータ）
    - **question**: 質問文（編集可能、オプション）
    - **answer**: 回答文（編集可能、オプション）
    - **category**: カテゴリ（編集可能、オプション）
    - **priority**: 優先度（1-5、デフォルト: 1）
    
    JWT認証必須。提案を承認してFAQを作成します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQ提案サービスで提案承認
        suggestion_service = FAQSuggestionService(db)
        suggestion = await suggestion_service.approve_suggestion(
            suggestion_id=suggestion_id,
            facility_id=facility_id,
            request=request,
            user_id=current_user.id
        )
        
        return suggestion
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving FAQ suggestion: {str(e)}"
        )


@router.post("/{suggestion_id}/reject", response_model=FAQSuggestionResponse)
async def reject_faq_suggestion(
    suggestion_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提案却下
    
    - **suggestion_id**: 提案ID（パスパラメータ）
    
    JWT認証必須。提案を却下します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQ提案サービスで提案却下
        suggestion_service = FAQSuggestionService(db)
        suggestion = await suggestion_service.reject_suggestion(
            suggestion_id=suggestion_id,
            facility_id=facility_id,
            user_id=current_user.id
        )
        
        return suggestion
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting FAQ suggestion: {str(e)}"
        )

