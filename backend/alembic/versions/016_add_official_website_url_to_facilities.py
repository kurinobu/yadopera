"""add official_website_url to facilities (coupon feature)

Revision ID: 016
Revises: 015
Create Date: 2026-02-21

クーポン機能「公式サイトURL」追加:
- facilities に official_website_url を追加（クーポン送付メールで案内用）
"""
from alembic import op
import sqlalchemy as sa


revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'facilities',
        sa.Column('official_website_url', sa.String(500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('facilities', 'official_website_url')
