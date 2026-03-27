"""align_free_faq_limit_to_30

Revision ID: 023
Revises: 022
Create Date: 2026-03-27

A2: FreeプランのFAQ上限を30件へ統一する。
plan_limits.py / auth_service.get_plan_defaults とDB実値を一致させる。
"""

from alembic import op

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE facilities
        SET faq_limit = 30
        WHERE plan_type = 'Free'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE facilities
        SET faq_limit = 20
        WHERE plan_type = 'Free'
        """
    )

