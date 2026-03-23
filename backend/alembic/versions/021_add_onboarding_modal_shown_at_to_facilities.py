"""add onboarding_modal_shown_at to facilities (初回ログイン時やることリスト表示済み)

Revision ID: 021
Revises: 020
Create Date: 2026-03-12

初回ログイン時やることリスト実装 Step 1。
facilities.onboarding_modal_shown_at (TIMESTAMP WITH TIME ZONE, nullable)
NULL = まだモーダル未表示、日時 = 表示済み。
"""
from alembic import op
import sqlalchemy as sa


revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'facilities',
        sa.Column('onboarding_modal_shown_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('facilities', 'onboarding_modal_shown_at')
