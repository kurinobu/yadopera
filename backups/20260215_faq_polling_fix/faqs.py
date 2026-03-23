"""
FAQ管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, status, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.facility import Facility
from app.schemas.faq import (
    FAQRequest,
    FAQUpdateRequest,
    FAQResponse,
    FAQListResponse,
    BulkFAQCreateResponse,
    BulkUploadResult,
)
from app.services.faq_service import FAQService
from app.services.csv_parser import CSVParseError
from app.core.plan_limits import get_initial_faq_count

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
        
        # 施設情報を取得して、バックグラウンド処理が進行中かどうかを判定
        facility = await db.get(Facility, facility_id)
        is_initializing = False
        
        if facility:
            time_since_creation = datetime.now(timezone.utc) - facility.created_at
            expected_count = get_initial_faq_count(facility.subscription_plan)
            actual_count = len(faqs)
            
            # 施設作成から60秒以内で、期待値と一致しない場合は進行中とみなす
            # ステージング環境での処理時間を考慮して60秒に拡張
            if time_since_creation < timedelta(seconds=60) and actual_count < expected_count:
                is_initializing = True
            # 期待値未満の場合は常に進行中とみなす（より確実）
            elif actual_count < expected_count:
                is_initializing = True
        
        # totalはインテント単位でカウント（言語に関係なく、FAQ.idをカウント）
        return FAQListResponse(faqs=faqs, total=len(faqs), is_initializing=is_initializing)
    
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
    http_request: Request,
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
        
        # アクティビティログ記録（非同期）
        from app.models.admin_activity_log import AdminActivityLog
        question_preview = request.translations[0].question[:50] if request.translations else 'N/A'
        activity_log = AdminActivityLog(
            user_id=current_user.id,
            facility_id=facility_id,
            action_type="faq_create",
            target_resource_type="faq",
            target_resource_id=faq.id,
            description=f"FAQ作成: {question_preview}...",
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        db.add(activity_log)
        await db.commit()
        
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
    http_request: Request,
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
        
        # アクティビティログ記録（非同期）
        from app.models.admin_activity_log import AdminActivityLog
        question_preview = request.translations[0].question[:50] if request.translations and len(request.translations) > 0 else 'N/A'
        activity_log = AdminActivityLog(
            user_id=current_user.id,
            facility_id=facility_id,
            action_type="faq_update",
            target_resource_type="faq",
            target_resource_id=faq_id,
            description=f"FAQ更新: {question_preview}...",
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        db.add(activity_log)
        await db.commit()
        
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
    http_request: Request,
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
        
        # アクティビティログ記録（非同期）
        from app.models.admin_activity_log import AdminActivityLog
        activity_log = AdminActivityLog(
            user_id=current_user.id,
            facility_id=facility_id,
            action_type="faq_delete",
            target_resource_type="faq",
            target_resource_id=faq_id,
            description=f"FAQ削除: FAQ ID {faq_id}",
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent")
        )
        db.add(activity_log)
        await db.commit()
        
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


MAX_CSV_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


@router.post("/bulk-upload", response_model=BulkUploadResult, status_code=status.HTTP_201_CREATED)
async def bulk_upload_faqs(
    file: UploadFile = File(..., description="CSVファイル"),
    mode: str = Form("add", description="登録モード（add: 追加のみ）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    CSVファイルからFAQを一括登録。Standard/Premiumプランのみ利用可能。
    """
    facility_id = current_user.facility_id
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility",
        )
    facility = await db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Facility not found",
        )
    if facility.plan_type not in ("Standard", "Premium"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSV一括登録はStandardプランまたはPremiumプランでのみ利用可能です",
        )
    content = await file.read()
    if len(content) > MAX_CSV_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズは10MB以内にしてください",
        )
    faq_service = FAQService(db)
    try:
        result = await faq_service.bulk_create_faqs_from_csv(
            facility_id=facility_id,
            file_bytes=content,
            user_id=current_user.id,
            mode=mode,
        )
        return BulkUploadResult(**result)
    except CSVParseError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("bulk_upload_faqs error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました。しばらく待ってから再度お試しください。",
        )


@router.post("/bulk", response_model=BulkFAQCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_faqs(
    faq_requests: List[FAQRequest],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    FAQ一括作成（プリセット投入用、埋め込みベクトル自動生成、インテントベース構造）
    
    - **faq_requests**: FAQ作成リクエストのリスト
      - **category**: カテゴリ（basic/facilities/location/trouble）
      - **intent_key**: インテント識別キー（オプション、自動生成される場合は省略可能）
      - **translations**: 翻訳リスト（最低1つの言語が必要）
        - **language**: 言語コード（en/ja/zh-TW/fr）
        - **question**: 質問文（1-500文字）
        - **answer**: 回答文（1-2000文字）
      - **priority**: 優先度（1-5、デフォルト: 1）
      - **is_active**: 有効/無効（デフォルト: true）
    
    JWT認証必須。一括で複数FAQを作成します。作成に失敗したFAQはスキップされ、ログに記録されます。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # FAQサービスで一括作成
        faq_service = FAQService(db)
        created_faqs = await faq_service.bulk_create_faqs(
            facility_id=facility_id,
            faq_requests=faq_requests,
            user_id=current_user.id
        )
        
        return BulkFAQCreateResponse(
            created_count=len(created_faqs),
            faqs=created_faqs
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bulk FAQs: {str(e)}"
        )


