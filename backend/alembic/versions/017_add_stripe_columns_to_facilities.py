"""add Stripe columns to facilities (Phase 4 Phase B)

Revision ID: 017
Revises: 016
Create Date: 2026-02-25

Phase B: Stripe 連携用に facilities に以下を追加
- stripe_customer_id: Stripe Customer ID（nullable, unique）
- stripe_subscription_id: 現在のサブスクリプション ID（nullable）
- subscription_status: active / canceled / past_due / unpaid 等（Stripe と同期）
- cancel_at_period_end: 期間末解約フラグ（default False）
"""
from alembic import op
import sqlalchemy as sa


revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'facilities',
        sa.Column('stripe_customer_id', sa.String(255), nullable=True)
    )
    op.add_column(
        'facilities',
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True)
    )
    op.add_column(
        'facilities',
        sa.Column('subscription_status', sa.String(50), nullable=True)
    )
    op.add_column(
        'facilities',
        sa.Column('cancel_at_period_end', sa.Boolean(), server_default=sa.text('false'), nullable=False)
    )
    op.create_index(
        'ix_facilities_stripe_customer_id',
        'facilities',
        ['stripe_customer_id'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_facilities_stripe_customer_id', table_name='facilities')
    op.drop_column('facilities', 'cancel_at_period_end')
    op.drop_column('facilities', 'subscription_status')
    op.drop_column('facilities', 'stripe_subscription_id')
    op.drop_column('facilities', 'stripe_customer_id')
