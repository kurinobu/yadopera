"""add coupon settings and guest_leads table (lead-get option)

Revision ID: 015
Revises: 014
Create Date: 2026-02-21

リードゲットオプション（決済なしクーポン）:
- facilities にクーポン設定カラムを追加
- guest_leads テーブルを新規作成
"""
from alembic import op
import sqlalchemy as sa


revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # facilities: クーポン設定カラム
    op.add_column(
        'facilities',
        sa.Column('coupon_enabled', sa.Boolean(), server_default='false', nullable=False)
    )
    op.add_column(
        'facilities',
        sa.Column('coupon_discount_percent', sa.Integer(), nullable=True)
    )
    op.add_column(
        'facilities',
        sa.Column('coupon_description', sa.Text(), nullable=True)
    )
    op.add_column(
        'facilities',
        sa.Column('coupon_validity_months', sa.Integer(), nullable=True)
    )

    # guest_leads テーブル作成
    op.create_table(
        'guest_leads',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('facility_id', sa.Integer(), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('guest_name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('coupon_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_guest_leads_facility_id_created_at', 'guest_leads', ['facility_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_guest_leads_facility_id_created_at', table_name='guest_leads')
    op.drop_table('guest_leads')

    op.drop_column('facilities', 'coupon_validity_months')
    op.drop_column('facilities', 'coupon_description')
    op.drop_column('facilities', 'coupon_discount_percent')
    op.drop_column('facilities', 'coupon_enabled')
