"""
QRコード生成APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.qr_code import QRCode
from app.schemas.qr_code import QRCodeRequest, QRCodeResponse, QRCodeListResponse
from app.services.qr_code_service import QRCodeService

router = APIRouter(prefix="/admin/qr-code", tags=["admin", "qr-code"])
router_list = APIRouter(prefix="/admin/qr-codes", tags=["admin", "qr-code"])


@router.post("", response_model=QRCodeResponse)
async def generate_qr_code(
    request: QRCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    QRコード生成
    
    - **location**: 設置場所（entrance/room/kitchen/lounge/custom）
    - **custom_location_name**: カスタム設置場所名（location=customの場合）
    - **include_session_token**: セッション統合トークン埋め込み（v0.3新規）
    - **format**: 出力形式（pdf/png/svg、デフォルト: png）
    - **primary_session_id**: プライマリセッションID（include_session_token=Trueの場合）
    
    JWT認証必須。施設専用QRコードを生成します。
    PDF/PNG/SVG形式でダウンロード可能（A4印刷用サイズ）。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # セッション統合トークン埋め込みの場合、primary_session_idが必要
        if request.include_session_token and not request.primary_session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="primary_session_id is required when include_session_token is True"
            )
        
        # QRコードサービスでQRコード生成
        qr_code_service = QRCodeService(db)
        qr_code_data = await qr_code_service.generate_qr_code(
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            include_session_token=request.include_session_token,
            format=request.format,
            primary_session_id=request.primary_session_id
        )
        
        # データベースに保存
        qr_code_model = QRCode(
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            qr_code_url=qr_code_data["qr_code_url"],
            qr_code_data=qr_code_data["qr_code_data"],
            format=request.format
        )
        db.add(qr_code_model)
        await db.commit()
        await db.refresh(qr_code_model)
        
        return QRCodeResponse(
            id=qr_code_model.id,
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            include_session_token=request.include_session_token,
            qr_code_url=qr_code_data["qr_code_url"],
            qr_code_data=qr_code_data["qr_code_data"],
            format=qr_code_data["format"],
            created_at=qr_code_model.created_at
        )
    
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
            detail=f"Error generating QR code: {str(e)}"
        )


@router.post("/preview", response_model=QRCodeResponse)
async def generate_qr_code_preview(
    request: QRCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    QRコードプレビュー生成（データベースに保存しない）
    
    - **location**: 設置場所（entrance/room/kitchen/lounge/custom）
    - **custom_location_name**: カスタム設置場所名（location=customの場合）
    - **format**: 出力形式（pdf/png/svg、デフォルト: png）
    
    JWT認証必須。プレビュー表示用のQRコードを生成します。
    データベースに保存されません。
    """
    try:
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # QRコードサービスでQRコード生成
        qr_code_service = QRCodeService(db)
        qr_code_data = await qr_code_service.generate_qr_code(
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            include_session_token=False,  # プレビューでは常にFalse
            format=request.format,
            primary_session_id=None
        )
        
        # データベースに保存しない（プレビュー用）
        # IDは生成時刻ベース（一時的なID）
        qr_code_id = int(datetime.utcnow().timestamp())
        
        return QRCodeResponse(
            id=qr_code_id,
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            include_session_token=False,
            qr_code_url=qr_code_data["qr_code_url"],
            qr_code_data=qr_code_data["qr_code_data"],
            format=qr_code_data["format"],
            created_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code preview: {str(e)}"
        )


@router_list.get("", response_model=QRCodeListResponse)
async def list_qr_codes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    生成済みQRコード一覧を取得
    """
    try:
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        result = await db.execute(
            select(QRCode)
            .where(QRCode.facility_id == facility_id)
            .order_by(QRCode.created_at.desc())
        )
        qr_codes = result.scalars().all()
        
        return QRCodeListResponse(
            qr_codes=[
                QRCodeResponse(
                    id=qr.id,
                    facility_id=qr.facility_id,
                    location=qr.location,
                    custom_location_name=qr.custom_location_name,
                    include_session_token=False,  # 削除されたため常にFalse
                    qr_code_url=qr.qr_code_url,
                    qr_code_data=qr.qr_code_data,
                    format=qr.format,
                    created_at=qr.created_at
                )
                for qr in qr_codes
            ],
            total=len(qr_codes)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching QR codes: {str(e)}"
        )


@router.delete("/{qr_code_id}")
async def delete_qr_code(
    qr_code_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    QRコードを削除
    """
    try:
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        result = await db.execute(
            select(QRCode)
            .where(QRCode.id == qr_code_id)
            .where(QRCode.facility_id == facility_id)
        )
        qr_code = result.scalar_one_or_none()
        
        if not qr_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR code not found"
            )
        
        await db.delete(qr_code)
        await db.commit()
        
        return {"message": "QR code deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting QR code: {str(e)}"
        )

