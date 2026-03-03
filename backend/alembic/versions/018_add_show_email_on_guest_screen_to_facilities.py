"""add show_email_on_guest_screen to facilities (ゲスト画面にメール表示する/しないスイッチ)

Revision ID: 018
Revises: 017
Create Date: 2026-03-02

施設設定「ゲスト画面にメールアドレスを表示する」ON/OFF 用。
facilities.show_email_on_guest_screen (Boolean, NOT NULL, default True)
既存施設は True で後方互換。
"""
from alembic import op
import sqlalchemy as sa


revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'facilities',
        sa.Column('show_email_on_guest_screen', sa.Boolean(), server_default=sa.text('true'), nullable=False)
    )


def downgrade() -> None:
    op.drop_column('facilities', 'show_email_on_guest_screen')
