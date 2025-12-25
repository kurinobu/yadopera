"""
FAQ管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.faq import FAQRequest, FAQUpdateRequest, FAQResponse, FAQListResponse
from app.services.faq_service import FAQService

router = APIRouter(prefix="/admin/faqs", tags=["admin", "faqs"])


@router.get("", response_model=FAQListResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="カテゴリフィルタ（basic/facilities/location/trouble）"),
    is_active: Optional[bool] = Query(None, description="有効/無効フィルタ"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ一覧取得
    
    - **category**: カテゴリフィルタ（オプション）
    - **is_active**: 有効/無効フィルタ（オプション）
    
    JWT認証必須。現在のユーザーが所属する施設のFAQを返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQサービスでFAQ一覧取得
        # FAQService.get_faqs()はインテント単位でFAQを返すため、len(faqs)で正しくカウントされる
        faq_service = FAQService(db)
        faqs = await faq_service.get_faqs(
            facility_id=facility_id,
            category=category,
            is_active=is_active
        )
        
        # totalはインテント単位でカウント（言語に関係なく、FAQ.idをカウント）
        return FAQListResponse(faqs=faqs, total=len(faqs))
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQs: {str(e)}"
        )


@router.post("", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    request: FAQRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ作成（埋め込みベクトル自動生成、インテントベース構造）
    
    - **category**: カテゴリ（basic/facilities/location/trouble）
    - **intent_key**: インテント識別キー（オプション、自動生成される場合は省略可能）
    - **translations**: 翻訳リスト（最低1つの言語が必要）
      - **language**: 言語コード（en/ja/zh-TW/fr）
      - **question**: 質問文（1-500文字）
      - **answer**: 回答文（1-2000文字）
    - **priority**: 優先度（1-5、デフォルト: 1）
    - **is_active**: 有効/無効（デフォルト: true）
    
    JWT認証必須。FAQ作成時に埋め込みベクトルが自動生成されます。
    インテント単位で1件としてカウントされます（複数言語対応しても1件）。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQサービスでFAQ作成
        faq_service = FAQService(db)
        faq = await faq_service.create_faq(
            facility_id=facility_id,
            request=request,
            user_id=current_user.id
        )
        
        return faq
    
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
            detail=f"Error creating FAQ: {str(e)}"
        )


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: int,
    request: FAQUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ更新（埋め込みベクトル自動再生成、インテントベース構造）
    
    - **faq_id**: FAQ ID（パスパラメータ）
    - **category**: カテゴリ（basic/facilities/location/trouble、オプション）
    - **intent_key**: インテント識別キー（オプション）
    - **translations**: 翻訳リスト（オプション）
      - **language**: 言語コード（en/ja/zh-TW/fr）
      - **question**: 質問文（1-500文字）
      - **answer**: 回答文（1-2000文字）
    - **priority**: 優先度（1-5、オプション）
    - **is_active**: 有効/無効（オプション）
    
    JWT認証必須。FAQ更新時に埋め込みベクトルが自動再生成されます。
    インテント単位で1件としてカウントされます（複数言語対応しても1件）。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQサービスでFAQ更新
        faq_service = FAQService(db)
        faq = await faq_service.update_faq(
            faq_id=faq_id,
            facility_id=facility_id,
            request=request,
            user_id=current_user.id
        )
        
        return faq
    
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
            detail=f"Error updating FAQ: {str(e)}"
        )


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ削除
    
    - **faq_id**: FAQ ID（パスパラメータ）
    
    JWT認証必須。FAQを削除します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQサービスでFAQ削除
        faq_service = FAQService(db)
        await faq_service.delete_faq(
            faq_id=faq_id,
            facility_id=facility_id
        )
        
        return None
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting FAQ: {str(e)}"
        )

