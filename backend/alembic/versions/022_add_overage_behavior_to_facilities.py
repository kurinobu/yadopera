"""add overage_behavior to facilities (プラン超過時の挙動・管理者選択制)

Revision ID: 022
Revises: 021
Create Date: 2026-03-13

プラン超過時の挙動（管理者選択制）実装 Step 1。
facilities.overage_behavior: 'continue_billing' | 'faq_only'
デフォルト 'continue_billing'。Free プランは 'faq_only' に更新。
"""
from alembic import op
import sqlalchemy as sa


revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "facilities",
        sa.Column(
            "overage_behavior",
            sa.String(20),
            nullable=False,
            server_default="continue_billing",
        ),
    )
    # Free プランは超過後 FAQ のみとするデフォルトに合わせる
    op.execute(
        """
        UPDATE facilities
        SET overage_behavior = 'faq_only'
        WHERE plan_type = 'Free'
        """
    )


def downgrade() -> None:
    op.drop_column("facilities", "overage_behavior")
