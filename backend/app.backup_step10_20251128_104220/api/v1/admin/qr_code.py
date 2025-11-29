"""
QRコード生成APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.qr_code import QRCodeRequest, QRCodeResponse
from app.services.qr_code_service import QRCodeService

router = APIRouter(prefix="/admin/qr-code", tags=["admin", "qr-code"])


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
        
        # レスポンス生成（IDは生成時刻ベース）
        qr_code_id = int(datetime.utcnow().timestamp())
        
        return QRCodeResponse(
            id=qr_code_id,
            facility_id=facility_id,
            location=request.location,
            custom_location_name=request.custom_location_name,
            include_session_token=request.include_session_token,
            qr_code_url=qr_code_data["qr_code_url"],
            qr_code_data=qr_code_data["qr_code_data"],
            format=qr_code_data["format"],
            created_at=datetime.utcnow()
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

