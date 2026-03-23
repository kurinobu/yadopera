"""
開発者向け FAQ CSV 一括登録 API（Phase A）
指定施設 ID に対し、施設管理者 API と同じロジックで bulk 登録する。
uploaded_by は施設に紐づくユーザーを 1 件選ぶ（代行スクリプト `bulk_upload_faq_csv_for_facility.py` と同様）。
"""

import hashlib
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_developer
from app.database import get_db
from app.models.admin_activity_log import AdminActivityLog
from app.models.facility import Facility
from app.models.user import User
from app.schemas.faq import BulkUploadResult
from app.services.csv_parser import CSVParseError
from app.services.faq_service import FAQService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facilities", tags=["developer", "faqs"])

MAX_CSV_SIZE_BYTES = 10 * 1024 * 1024  # 10MB（管理者 API と同一）


async def _write_developer_csv_audit_log(
    *,
    db: AsyncSession,
    request: Request,
    facility_id: int,
    facility_user_id: int | None,
    developer_sub: str,
    status_text: str,
    file_name: str | None,
    file_size: int | None,
    file_sha256_prefix: str | None,
    result_summary: str | None = None,
    error_message: str | None = None,
) -> None:
    """
    開発者CSV一括登録の監査ログを書き込む（失敗しても本処理へ影響を与えない）。
    """
    description_parts = [
        f"developer_sub={developer_sub}",
        f"status={status_text}",
        f"file_name={file_name or '-'}",
        f"file_size={file_size if file_size is not None else '-'}",
        f"file_sha256_prefix={file_sha256_prefix or '-'}",
    ]
    if result_summary:
        description_parts.append(f"result={result_summary}")
    if error_message:
        description_parts.append(f"error={error_message}")

    activity_log = AdminActivityLog(
        user_id=facility_user_id,
        facility_id=facility_id,
        action_type="developer_faq_bulk_upload",
        target_resource_type="facility",
        target_resource_id=facility_id,
        description="; ".join(description_parts),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    try:
        db.add(activity_log)
        await db.commit()
    except Exception:
        logger.exception("Failed to write developer CSV audit log")


@router.post(
    "/{facility_id}/faqs/bulk-upload",
    response_model=BulkUploadResult,
    status_code=status.HTTP_201_CREATED,
)
async def developer_bulk_upload_faqs(
    facility_id: int,
    http_request: Request,
    file: UploadFile = File(..., description="CSVファイル"),
    mode: str = Form("add", description="登録モード（add: 追加のみ）"),
    developer_payload: dict = Depends(get_current_developer),
    db: AsyncSession = Depends(get_db),
):
    """
    開発者専用: 指定施設に CSV から FAQ を一括登録。Standard / Premium のみ。

    - 認証: 開発者 JWT（`type=developer`）
    - `uploaded_by`: 当該 `facility_id` に紐づくユーザーを 1 件（先頭）を使用
    """
    developer_sub = str(developer_payload.get("sub", "unknown"))
    file_name = file.filename
    file_size: int | None = None
    file_sha256_prefix: str | None = None

    facility = await db.get(Facility, facility_id)
    if not facility:
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=None,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message=f"Facility not found: facility_id={facility_id}",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility not found: facility_id={facility_id}",
        )
    if facility.plan_type not in ("Standard", "Premium"):
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=None,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message="CSV一括登録はStandardプランまたはPremiumプランでのみ利用可能です",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSV一括登録はStandardプランまたはPremiumプランでのみ利用可能です",
        )

    result_user = await db.execute(
        select(User).where(User.facility_id == facility_id).limit(1)
    )
    facility_user = result_user.scalar_one_or_none()
    if not facility_user:
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=None,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message="この施設に紐づくユーザーが存在しません。一括登録には施設ユーザーが最低1名必要です。",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この施設に紐づくユーザーが存在しません。一括登録には施設ユーザーが最低1名必要です。",
        )
    facility_user_id = facility_user.id

    content = await file.read()
    file_size = len(content)
    file_sha256_prefix = hashlib.sha256(content).hexdigest()[:16]
    if len(content) > MAX_CSV_SIZE_BYTES:
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=facility_user_id,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message="ファイルサイズは10MB以内にしてください",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズは10MB以内にしてください",
        )

    faq_service = FAQService(db)
    try:
        result = await faq_service.bulk_create_faqs_from_csv(
            facility_id=facility_id,
            file_bytes=content,
            user_id=facility_user_id,
            mode=mode,
        )
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=facility_user_id,
            developer_sub=developer_sub,
            status_text="success",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            result_summary=(
                f"success_count={result.get('success_count', 0)},"
                f"failure_count={result.get('failure_count', 0)},"
                f"total_count={result.get('total_count', 0)}"
            ),
        )
        return BulkUploadResult(**result)
    except CSVParseError as e:
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=facility_user_id,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=facility_user_id,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.exception("developer_bulk_upload_faqs error")
        await _write_developer_csv_audit_log(
            db=db,
            request=http_request,
            facility_id=facility_id,
            facility_user_id=facility_user_id,
            developer_sub=developer_sub,
            status_text="failure",
            file_name=file_name,
            file_size=file_size,
            file_sha256_prefix=file_sha256_prefix,
            error_message="内部サーバーエラーが発生しました。しばらく待ってから再度お試しください。",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラーが発生しました。しばらく待ってから再度お試しください。",
        )
