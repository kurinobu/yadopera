"""
QRコード関連スキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QRCodeRequest(BaseModel):
    """QRコード生成リクエスト"""
    location: str = Field(..., description="設置場所（entrance/room/kitchen/lounge/custom）")
    custom_location_name: Optional[str] = Field(None, description="カスタム設置場所名（location=customの場合）")
    include_session_token: bool = Field(default=False, description="会話引き継ぎコード埋め込み（v0.3新規）")
    format: str = Field(default="png", description="出力形式（pdf/png/svg）")
    primary_session_id: Optional[str] = Field(None, description="プライマリセッションID（include_session_token=Trueの場合）")

    class Config:
        json_schema_extra = {
            "example": {
                "location": "entrance",
                "include_session_token": False,
                "format": "png"
            }
        }


class QRCodeResponse(BaseModel):
    """QRコード生成レスポンス"""
    id: int = Field(..., description="QRコードID")
    facility_id: int = Field(..., description="施設ID")
    location: str = Field(..., description="設置場所")
    custom_location_name: Optional[str] = Field(None, description="カスタム設置場所名")
    include_session_token: bool = Field(..., description="会話引き継ぎコード埋め込み有無")
    qr_code_url: str = Field(..., description="QRコード画像URL（Base64エンコードまたはファイルパス）")
    qr_code_data: str = Field(..., description="QRコードに埋め込まれたURL")
    format: str = Field(..., description="出力形式")
    created_at: datetime = Field(..., description="作成日時")

    class Config:
        from_attributes = True


class QRCodeListResponse(BaseModel):
    """生成済みQRコード一覧レスポンス"""
    qr_codes: List[QRCodeResponse] = Field(..., description="生成済みQRコード一覧")
    total: int = Field(..., description="総数")

    class Config:
        from_attributes = True

