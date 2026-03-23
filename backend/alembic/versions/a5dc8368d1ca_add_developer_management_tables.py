"""add_developer_management_tables

Revision ID: a5dc8368d1ca
Revises: 097d9c387a86
Create Date: 2026-01-24 00:44:12.110011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a5dc8368d1ca'
down_revision: Union[str, None] = '097d9c387a86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    開発者管理ページ用テーブル作成（MVP: error_logsのみ）
    - error_logs: エラーログ記録テーブル
    """
    # error_logs テーブル作成
    op.create_table(
        'error_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('error_level', sa.String(length=20), nullable=False, comment='エラーレベル（error, warning, critical）'),
        sa.Column('error_code', sa.String(length=50), nullable=False, comment='エラーコード（UNAUTHORIZED, INTERNAL_ERROR等）'),
        sa.Column('error_message', sa.Text(), nullable=False, comment='エラーメッセージ'),
        sa.Column('stack_trace', sa.Text(), nullable=True, comment='スタックトレース'),
        sa.Column('request_path', sa.String(length=500), nullable=True, comment='リクエストパス'),
        sa.Column('request_method', sa.String(length=10), nullable=True, comment='HTTPメソッド'),
        sa.Column('facility_id', sa.Integer(), nullable=True, comment='施設ID'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='ユーザーID'),
        sa.Column('ip_address', postgresql.INET(), nullable=True, comment='IPアドレス'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='User-Agent'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # インデックス作成
    op.create_index('idx_error_logs_level', 'error_logs', ['error_level'])
    op.create_index('idx_error_logs_facility', 'error_logs', ['facility_id'])
    op.create_index('idx_error_logs_created', 'error_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    """
    テーブル削除
    """
    op.drop_index('idx_error_logs_created', table_name='error_logs')
    op.drop_index('idx_error_logs_facility', table_name='error_logs')
    op.drop_index('idx_error_logs_level', table_name='error_logs')
    op.drop_table('error_logs')
