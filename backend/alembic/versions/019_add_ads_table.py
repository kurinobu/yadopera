"""add ads table (Freeプラン ゲスト画面固定フッター広告)

Revision ID: 019
Revises: 018
Create Date: 2026-03-04

Freeプラン広告用。ads テーブルを新規作成。
id, title, description, url, affiliate_url, priority, active, created_at, updated_at
"""
from alembic import op
import sqlalchemy as sa


revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ads',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('affiliate_url', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ads_id'), 'ads', ['id'], unique=False)
    op.create_index(op.f('ix_ads_active'), 'ads', ['active'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ads_active'), table_name='ads')
    op.drop_index(op.f('ix_ads_id'), table_name='ads')
    op.drop_table('ads')
