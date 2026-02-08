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
from app.core.config import settings

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

# QRコードテキストオーバーレイ用
import re  # SVG viewBox解析用

# PIL追加インポート（条件付き）
try:
    from PIL import ImageDraw, ImageFont
    PIL_DRAW_AVAILABLE = True
except ImportError:
    PIL_DRAW_AVAILABLE = False
    logger.warning("PIL ImageDraw/ImageFont not available.")


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
        base_url: Optional[str] = None
    ) -> str:
        """
        QRコードURL生成
        
        Args:
            facility_slug: 施設slug
            location: 設置場所
            custom_location_name: カスタム設置場所名（オプション）
            session_token: 会話引き継ぎコード（オプション）
            base_url: ベースURL（オプション、未指定の場合は環境変数から取得）
        
        Returns:
            str: QRコードURL
        """
        # base_urlが指定されていない場合は環境変数から取得
        if base_url is None:
            base_url = settings.frontend_url
        
        url = f"{base_url}/f/{facility_slug}?location={location}"
        
        if custom_location_name:
            url += f"&custom={custom_location_name}"
        
        if session_token:
            url += f"&token={session_token}"
        
        return url
    
    def _get_location_label(self, location: str, custom_location_name: Optional[str]) -> str:
        """
        設置場所コードから日本語表示への変換
        
        Args:
            location: 設置場所コード
            custom_location_name: カスタム設置場所名（オプション）
        
        Returns:
            str: 日本語表示の設置場所名
        """
        if location == 'custom' and custom_location_name:
            return custom_location_name
        
        location_labels = {
            'entrance': '入口',
            'room': '客室',
            'kitchen': 'キッチン',
            'lounge': 'ラウンジ',
            'custom': 'カスタム'
        }
        return location_labels.get(location, location)
    
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
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # L → H に変更（中央テキスト対応）
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_data)
            qr.make(fit=True)
            
            if format == "png":
                # QRコード画像を生成
                img = qr.make_image(fill_color="black", back_color="white")
                
                # PIL Imageに変換して中央にテキストを追加
                img = img.convert('RGB')
                
                if PIL_DRAW_AVAILABLE:
                    draw = ImageDraw.Draw(img)
                    
                    # QRコードサイズを取得
                    qr_width, qr_height = img.size
                    
                    # テキスト「YadOPERA」を中央に配置
                    text = "YadOPERA"
                    # デフォルトフォントを使用（サイズ指定）
                    try:
                        font_size = int(qr_width / 10)
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    except:
                        # フォントが見つからない場合はデフォルトフォント
                        font = ImageFont.load_default()
                    
                    # テキストのバウンディングボックスを取得
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # 中央座標を計算
                    text_x = (qr_width - text_width) / 2
                    text_y = (qr_height - text_height) / 2
                    
                    # 白背景の矩形を描画（テキストより少し大きく）
                    padding = 10
                    draw.rectangle(
                        [text_x - padding, text_y - padding, 
                         text_x + text_width + padding, text_y + text_height + padding],
                        fill=(255, 255, 255)
                    )
                    
                    # テキストを描画
                    draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
                
                # BytesIOに保存
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                qr_code_url = f"data:image/png;base64,{base64.b64encode(img_buffer.getvalue()).decode()}"
            
            elif format == "svg":
                # SVG形式のQRコードを生成
                try:
                    from qrcode.image.svg import SvgImage
                    
                    # QRコードオブジェクトを作成（エラー訂正レベルH、image_factoryを指定）
                    qr_svg = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,  # L → H に変更（中央テキスト対応）
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
                    
                    # SVGデータを文字列として読み込み
                    svg_data = svg_buffer.getvalue().decode('utf-8')
                    
                    # SVGのviewBoxを解析して中央座標を計算
                    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_data)
                    if viewbox_match:
                        # viewBox属性が存在する場合（既存の処理）
                        viewbox = viewbox_match.group(1).split()
                        width = float(viewbox[2])
                        height = float(viewbox[3])
                        center_x = width / 2
                        center_y = height / 2
                    else:
                        # viewBox属性がない場合、width/height属性から計算
                        width_match = re.search(r'width="([^"]+)"', svg_data)
                        height_match = re.search(r'height="([^"]+)"', svg_data)
                        
                        if width_match and height_match:
                            # mm単位の値を数値に変換（例: "57mm" → 57.0）
                            width_str = width_match.group(1)
                            height_str = height_match.group(1)
                            
                            # mm単位を数値に変換
                            width_mm_match = re.search(r'(\d+(?:\.\d+)?)mm', width_str)
                            height_mm_match = re.search(r'(\d+(?:\.\d+)?)mm', height_str)
                            
                            if width_mm_match and height_mm_match:
                                width = float(width_mm_match.group(1))
                                height = float(height_mm_match.group(1))
                                center_x = width / 2
                                center_y = height / 2
                            else:
                                logger.warning("SVG width/height format not recognized, skipping text overlay")
                                width = None
                                height = None
                        else:
                            logger.warning("SVG width/height attributes not found, skipping text overlay")
                            width = None
                            height = None
                    
                    # テキスト要素を追加（width/heightが取得できた場合）
                    if width is not None and height is not None:
                        # テキスト要素を追加（既存の処理）
                        font_size = width / 15
                        text = "YadOPERA"
                        
                        # 白背景の矩形（テキストの下に配置）
                        rect_width = width / 3
                        rect_height = font_size * 1.5
                        rect_x = center_x - rect_width / 2
                        rect_y = center_y - rect_height / 2
                        
                        # 座標系をmm単位に統一（SVGのwidth/height属性がmm単位のため）
                        text_element = f'''
                    <rect x="{rect_x}mm" y="{rect_y}mm" width="{rect_width}mm" height="{rect_height}mm" fill="white"/>
                    <text x="{center_x}mm" y="{center_y + font_size/3}mm" 
                          font-family="sans-serif" font-size="{font_size}mm" font-weight="bold"
                          fill="black" text-anchor="middle">{text}</text>
                '''
                        
                        # </svg>の直前にテキスト要素を挿入
                        svg_data = svg_data.replace('</svg>', text_element + '</svg>')
                    
                    # Base64エンコードしてData URL形式で返す
                    svg_bytes = svg_data.encode('utf-8')
                    qr_code_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_bytes).decode()}"
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
                    # 1. 共通のqrオブジェクトからQRコード画像を生成
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=A4)
                    
                    # PDF生成の最初に日本語フォントを登録（1回だけ実行）
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.pdfbase.ttfonts import TTFont
                    import os
                    
                    # 利用可能な日本語フォントを確認（優先順位順）
                    japanese_font_paths = [
                        "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",  # IPAゴシック（opentype）
                        "/usr/share/fonts/truetype/ipafont-gothic/ipagp.ttf",  # IPAゴシック（truetype）
                        "/usr/share/fonts/truetype/ipafont/ipagp.ttf",  # IPAゴシック（別パス）
                        "/usr/share/fonts/truetype/ipafont/ipag.ttf",  # IPAゴシック（別名）
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # DejaVu Sans（日本語非対応だが試行）
                    ]
                    
                    # フォントパスの存在確認と登録
                    japanese_font_name = None
                    for font_path in japanese_font_paths:
                        try:
                            if os.path.exists(font_path):
                                # フォント名を生成（ファイル名から拡張子を除く）
                                font_name = os.path.basename(font_path).replace('.ttf', '').replace('.ttc', '').replace('.otf', '')
                                # 既に登録されている場合はスキップ
                                if font_name not in pdfmetrics.getRegisteredFontNames():
                                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                                japanese_font_name = font_name
                                logger.info(f"Japanese font registered: {font_name} from {font_path}")
                                break
                        except Exception as e:
                            logger.warning(f"Failed to register font {font_path}: {str(e)}")
                            continue
                    
                    # フォントが登録されなかった場合のフォールバック
                    if japanese_font_name is None:
                        logger.warning("No Japanese font available. Japanese text will not display correctly.")
                        japanese_font_name = "Helvetica-Bold"  # フォールバック
                    
                    # QRコードサイズと位置計算
                    qr_size = 100 * mm  # 10cm
                    qr_x = (A4[0] - qr_size) / 2
                    qr_y = (A4[1] - qr_size) / 2  # 中央配置
                    
                    # 2. タイトル「FAQ & AI ChatBot」を描画（最上部、大きめのフォント）
                    c.setFont("Helvetica-Bold", 18)  # 12pt → 18ptに変更（視認性向上）
                    c.setFillColorRGB(0, 0, 0)  # 黒色
                    title_text = "FAQ & AI ChatBot"
                    title_width = c.stringWidth(title_text, "Helvetica-Bold", 18)  # フォントサイズを更新
                    title_x = (A4[0] - title_width) / 2  # 中央揃え
                    title_y = A4[1] - 30 * mm  # 上端から30mm下（最上部）
                    c.drawString(title_x, title_y, title_text)
                    
                    # 3. 施設名を描画（タイトルの下、適切な間隔を確保）
                    if japanese_font_name != "Helvetica-Bold":
                        c.setFont(japanese_font_name, 14)
                    else:
                        c.setFont("Helvetica-Bold", 14)
                    facility_name = facility.name
                    name_width = c.stringWidth(facility_name, japanese_font_name if japanese_font_name != "Helvetica-Bold" else "Helvetica-Bold", 14)
                    name_x = (A4[0] - name_width) / 2  # 中央揃え
                    # タイトルのフォントサイズ（18pt）をmmに変換して施設名の位置を計算
                    title_font_size_mm = 18 * 0.352778  # 1pt = 0.352778mm
                    spacing_title_name = 10 * mm  # タイトルと施設名の間隔
                    name_y = title_y - title_font_size_mm - spacing_title_name  # タイトルの下に配置
                    c.drawString(name_x, name_y, facility_name)
                    
                    # 4. QRコードを描画（中央にYadOPERAテキスト付き、ブランディング強化）
                    # 共通のqrオブジェクトから画像を生成し、YadOPERAテキストを追加
                    img_with_text = qr.make_image(fill_color="black", back_color="white")
                    img_with_text = img_with_text.convert('RGB')
                    
                    # 中央にYadOPERAテキストを追加
                    if PIL_DRAW_AVAILABLE:
                        draw = ImageDraw.Draw(img_with_text)
                        
                        qr_width, qr_height = img_with_text.size
                        text = "YadOPERA"
                        
                        try:
                            font_size = int(qr_width / 10)
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                        
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        text_x = (qr_width - text_width) / 2
                        text_y = (qr_height - text_height) / 2
                        
                        padding = 10
                        draw.rectangle(
                            [text_x - padding, text_y - padding, 
                             text_x + text_width + padding, text_y + text_height + padding],
                            fill=(255, 255, 255)
                        )
                        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
                    
                    # QRコード画像をPDFに配置
                    img_buffer_final = io.BytesIO()
                    img_with_text.save(img_buffer_final, format="PNG")
                    img_buffer_final.seek(0)
                    img_pil = Image.open(img_buffer_final)
                    c.drawImage(ImageReader(img_pil), qr_x, qr_y, width=qr_size, height=qr_size)
                    
                    # 5. 設置場所を描画（スタッフ用、小さいフォント）
                    if japanese_font_name != "Helvetica-Bold":
                        c.setFont(japanese_font_name, 8)
                    else:
                        c.setFont("Helvetica", 8)
                    c.setFillColorRGB(0.5, 0.5, 0.5)  # グレー色
                    location_label = self._get_location_label(location, custom_location_name)
                    location_text = f"設置場所: {location_label}"
                    location_x = qr_x
                    location_y = qr_y - 15 * mm
                    c.drawString(location_x, location_y, location_text)
                    
                    # 6. 生成日時を描画（スタッフ用、小さいフォント）
                    if japanese_font_name != "Helvetica-Bold":
                        c.setFont(japanese_font_name, 8)
                    else:
                        c.setFont("Helvetica", 8)
                    generated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                    datetime_text = f"生成日時: {generated_at}"
                    datetime_x = qr_x
                    datetime_y = qr_y - 25 * mm
                    c.drawString(datetime_x, datetime_y, datetime_text)
                    
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


