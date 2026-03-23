"""
CSV一括登録代行 申し込みAPI
施設管理者が申し込みフォームから送信した内容を運営あてメール（Brevo）で転送する。
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models.facility import Facility
from app.models.user import User
from app.services.email_service import EmailService

router = APIRouter(prefix="/admin/csv-bulk-request", tags=["admin"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = (".xlsx", ".csv", ".txt", ".md")


@router.post("", status_code=status.HTTP_200_OK)
async def post_csv_bulk_request(
    csv_facility_name: str = Form(""),
    csv_plan: str = Form(""),
    csv_desired_count: str = Form(""),
    csv_languages: str = Form(""),
    csv_email: str = Form(""),
    csv_contact_name: str = Form(""),
    csv_notes: str = Form(""),
    csv_faq_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    CSV一括登録代行の申し込みを受け付け、運営あてにメール（Brevo）で転送する。
    Standard/Premium プランの施設ユーザーのみ利用可能。添付ファイルは任意。
    """
    if not settings.admin_notification_email:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="申し込み受付は現在利用できません。",
        )

    if not current_user.facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any facility",
        )

    facility = await db.get(Facility, current_user.facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Facility not found",
        )
    if facility.plan_type not in ("Standard", "Premium"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSV一括登録代行の申し込みはStandardプランまたはPremiumプランのみ利用可能です",
        )

    file_bytes: Optional[bytes] = None
    filename: Optional[str] = None

    if csv_faq_file and csv_faq_file.filename:
        raw = await csv_faq_file.read()
        if len(raw) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="添付ファイルは10MB以内にしてください。",
            )
        ext = ""
        for a in ALLOWED_EXTENSIONS:
            if csv_faq_file.filename.lower().endswith(a):
                ext = a
                break
        if not ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="添付可能な形式は .xlsx, .csv, .txt, .md のみです。",
            )
        file_bytes = raw
        filename = csv_faq_file.filename

    form_data = {
        "csv_facility_name": csv_facility_name,
        "csv_plan": csv_plan,
        "csv_desired_count": csv_desired_count,
        "csv_languages": csv_languages,
        "csv_email": csv_email,
        "csv_contact_name": csv_contact_name,
        "csv_notes": csv_notes,
    }

    try:
        email_service = EmailService()
        await email_service.send_csv_bulk_request_email(
            form_data,
            file_bytes=file_bytes,
            filename=filename,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="申し込み受付は現在利用できません。",
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("send_csv_bulk_request_email error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="送信処理中にエラーが発生しました。しばらく経ってから再度お試しください。",
        )

    return {"message": "申し込みを受け付けました。"}
