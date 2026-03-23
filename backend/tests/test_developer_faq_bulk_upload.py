"""
開発者向け FAQ CSV 一括アップロード API テスト（Phase A）
"""

import pytest
from datetime import timedelta
from unittest.mock import patch
from fastapi import status

from app.core.jwt import create_access_token
from app.models.facility import Facility
from app.models.user import User
from app.core.security import hash_password


MINIMAL_CSV = (
    "category,language_ja_question,language_ja_answer\n"
    "basic,チェックアウトは何時ですか？,11時までです。\n"
).encode("utf-8")


@pytest.fixture
def developer_token():
    """開発者 JWT（type=developer）"""
    return create_access_token(
        data={"sub": "developer", "type": "developer"},
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture
def developer_headers(developer_token):
    return {"Authorization": f"Bearer {developer_token}"}


@pytest.fixture
async def standard_facility_with_user(db_session):
    """Standard プラン・ユーザー1名"""
    facility = Facility(
        name="Dev CSV Test Hotel",
        slug="dev-csv-test-hotel",
        email="devcsv@example.com",
        plan_type="Standard",
        faq_limit=100,
        language_limit=4,
        is_active=True,
    )
    db_session.add(facility)
    await db_session.flush()
    await db_session.refresh(facility)
    user = User(
        facility_id=facility.id,
        email="devcsv-user@example.com",
        password_hash=hash_password("testpassword123"),
        full_name="Dev CSV User",
        role="staff",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return facility, user


class TestDeveloperFaqBulkUpload:
    """POST /api/v1/developer/facilities/{id}/faqs/bulk-upload"""

    @pytest.mark.asyncio
    async def test_requires_auth(self, client, standard_facility_with_user):
        facility, _ = standard_facility_with_user
        response = await client.post(
            f"/api/v1/developer/facilities/{facility.id}/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_rejects_non_developer_token(
        self, client, auth_headers, standard_facility_with_user
    ):
        """施設管理者トークンでは開発者エンドポイントを使えない"""
        facility, _ = standard_facility_with_user
        response = await client.post(
            f"/api/v1/developer/facilities/{facility.id}/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "developer" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_facility_not_found(self, client, developer_headers):
        response = await client.post(
            "/api/v1/developer/facilities/999999/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
            headers=developer_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_free_plan_forbidden(self, client, developer_headers, test_facility):
        """Free プランは CSV 一括不可（管理者 API と同趣旨）"""
        response = await client.post(
            f"/api/v1/developer/facilities/{test_facility.id}/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
            headers=developer_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_no_facility_user_bad_request(
        self, client, developer_headers, db_session
    ):
        facility = Facility(
            name="No User Hotel",
            slug="no-user-hotel",
            email="nouser@example.com",
            plan_type="Standard",
            faq_limit=100,
            is_active=True,
        )
        db_session.add(facility)
        await db_session.flush()
        await db_session.refresh(facility)

        response = await client.post(
            f"/api/v1/developer/facilities/{facility.id}/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
            headers=developer_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ユーザー" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch("app.services.faq_service.generate_embedding")
    async def test_success_201(
        self,
        mock_embedding,
        client,
        developer_headers,
        standard_facility_with_user,
    ):
        mock_embedding.return_value = [0.1] * 1536
        facility, _ = standard_facility_with_user
        response = await client.post(
            f"/api/v1/developer/facilities/{facility.id}/faqs/bulk-upload",
            files={"file": ("t.csv", MINIMAL_CSV, "text/csv")},
            data={"mode": "add"},
            headers=developer_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "success_count" in data
        assert data["success_count"] >= 1
        assert "uploaded_by" in data
