"""
QRコード生成サービス
"""

import logging
import io
import base64
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.facility import Facility
from app.services.session_token_service import SessionTokenService

logger = logging.getLogger(__name__)

try:
    import qrcode
    from qrcode.image.pil import PilImage
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("qrcode library not available. QR code generation will be limited.")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("reportlab/PIL not available. PDF generation will be limited.")


class QRCodeService:
    """
    QRコード生成サービス
    - 設置場所別URL生成
    - 会話引き継ぎコード埋め込みオプション対応
    - PDF/PNG/SVG形式生成
    """
    
    def __init__(self, db: AsyncSession):
        """
        QRコードサービス初期化
        
        Args:
            db: データベースセッション
        """
        self.db = db
        self.session_token_service = SessionTokenService()
    
    def _generate_url(
        self,
        facility_slug: str,
        location: str,
        custom_location_name: Optional[str] = None,
        session_token: Optional[str] = None,
        base_url: str = "https://yadopera.com"
    ) -> str:
        """
        QRコードURL生成
        
        Args:
            facility_slug: 施設slug
            location: 設置場所
            custom_location_name: カスタム設置場所名（オプション）
            session_token: 会話引き継ぎコード（オプション）
            base_url: ベースURL
        
        Returns:
            str: QRコードURL
        """
        url = f"{base_url}/f/{facility_slug}?location={location}"
        
        if custom_location_name:
            url += f"&custom={custom_location_name}"
        
        if session_token:
            url += f"&token={session_token}"
        
        return url
    
    async def generate_qr_code(
        self,
        facility_id: int,
        location: str,
        custom_location_name: Optional[str] = None,
        include_session_token: bool = False,
        format: str = "png",
        primary_session_id: Optional[str] = None
    ) -> dict:
        """
        QRコード生成
        
        Args:
            facility_id: 施設ID
            location: 設置場所
            custom_location_name: カスタム設置場所名（オプション）
            include_session_token: 会話引き継ぎコード埋め込み（v0.3新規）
            format: 出力形式（pdf/png/svg）
            primary_session_id: プライマリセッションID（include_session_token=Trueの場合）
        
        Returns:
            dict: QRコード情報（qr_code_url, qr_code_data, format）
        
        Raises:
            ValueError: 施設が見つからない場合、または無効な形式の場合
        """
        # 施設を取得
        facility = await self.db.get(Facility, facility_id)
        if not facility:
            raise ValueError(f"Facility not found: facility_id={facility_id}")
        
        # 会話引き継ぎコード生成（オプション）
        session_token = None
        if include_session_token:
            if not primary_session_id:
                raise ValueError("primary_session_id is required when include_session_token is True")
            
            try:
                session_token = await self.session_token_service.generate_token(
                    facility_id=facility_id,
                    primary_session_id=primary_session_id,
                    db=self.db
                )
            except Exception as e:
                logger.error(f"Error generating session token: {str(e)}")
                raise ValueError(f"Failed to generate session token: {str(e)}")
        
        # QRコードURL生成
        qr_code_data = self._generate_url(
            facility_slug=facility.slug,
            location=location,
            custom_location_name=custom_location_name,
            session_token=session_token
        )
        
        # QRコード画像生成
        if not QRCODE_AVAILABLE:
            # フォールバック: 外部サービスを使用
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_code_data}"
        else:
            # qrcodeライブラリを使用
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_data)
            qr.make(fit=True)
            
            if format == "png":
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                qr_code_url = f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode()}"
            
            elif format == "svg":
                # SVG形式のQRコードを生成
                try:
                    from qrcode.image.svg import SvgImage
                    
                    # QRコードオブジェクトを作成（image_factoryを指定）
                    qr_svg = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                        image_factory=SvgImage
                    )
                    qr_svg.add_data(qr_code_data)
                    qr_svg.make(fit=True)
                    
                    # SVG形式で画像を生成
                    img_svg = qr_svg.make_image(fill_color="black", back_color="white")
                    
                    # SVGデータをBytesIOに保存
                    svg_buffer = io.BytesIO()
                    img_svg.save(svg_buffer)
                    svg_buffer.seek(0)
                    
                    # Base64エンコードしてData URL形式で返す
                    qr_code_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_buffer.getvalue()).decode()}"
                except ImportError as e:
                    # SvgImageが利用できない場合のフォールバック
                    logger.warning(f"SvgImage not available: {str(e)}. Falling back to external API.")
                    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_code_data}&format=svg"
                except Exception as e:
                    # その他のエラーの場合のフォールバック
                    logger.error(f"Error generating SVG QR code: {str(e)}. Falling back to external API.")
                    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_code_data}&format=svg"
            
            elif format == "pdf":
                if PDF_AVAILABLE:
                    # PDF生成
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=A4)
                    
                    # QRコードを中央に配置（10cm × 10cm）
                    qr_size = 100 * mm  # 10cm
                    x = (A4[0] - qr_size) / 2
                    y = (A4[1] - qr_size) / 2
                    
                    img_pil = Image.open(img_buffer)
                    c.drawImage(ImageReader(img_pil), x, y, width=qr_size, height=qr_size)
                    c.save()
                    
                    pdf_buffer.seek(0)
                    qr_code_url = f"data:application/pdf;base64,{base64.b64encode(pdf_buffer.getvalue()).decode()}"
                else:
                    # フォールバック: PNGを返す
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    qr_code_url = f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode()}"
                    format = "png"  # フォールバック形式
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info(
            f"QR code generated: facility_id={facility_id}, location={location}, format={format}",
            extra={
                "facility_id": facility_id,
                "location": location,
                "format": format,
                "include_session_token": include_session_token
            }
        )
        
        return {
            "qr_code_url": qr_code_url,
            "qr_code_data": qr_code_data,
            "format": format
        }


