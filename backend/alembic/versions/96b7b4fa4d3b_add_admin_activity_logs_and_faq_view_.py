"""add_admin_activity_logs_and_faq_view_logs_tables

Revision ID: 96b7b4fa4d3b
Revises: a5dc8368d1ca
Create Date: 2026-01-24 10:12:28.556870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '96b7b4fa4d3b'
down_revision: Union[str, None] = 'a5dc8368d1ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    ログ収集機能用テーブル作成
    - admin_activity_logs: 管理者アクティビティログ
    - faq_view_logs: FAQ閲覧ログ
    """
    # admin_activity_logs テーブル作成
    op.create_table(
        'admin_activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='ユーザーID'),
        sa.Column('facility_id', sa.Integer(), nullable=True, comment='施設ID'),
        sa.Column('action_type', sa.String(length=50), nullable=False, comment='アクションタイプ（login, faq_create, faq_update, faq_delete等）'),
        sa.Column('target_resource_type', sa.String(length=50), nullable=True, comment='対象リソースタイプ（faq, user, facility等）'),
        sa.Column('target_resource_id', sa.Integer(), nullable=True, comment='対象リソースID'),
        sa.Column('description', sa.Text(), nullable=True, comment='説明'),
        sa.Column('ip_address', postgresql.INET(), nullable=True, comment='IPアドレス'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='User-Agent'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='作成日時'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # インデックス作成
    op.create_index('idx_activity_logs_user', 'admin_activity_logs', ['user_id'])
    op.create_index('idx_activity_logs_facility', 'admin_activity_logs', ['facility_id'])
    op.create_index('idx_activity_logs_action', 'admin_activity_logs', ['action_type'])
    op.create_index('idx_activity_logs_created', 'admin_activity_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # faq_view_logs テーブル作成
    op.create_table(
        'faq_view_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False, comment='FAQ ID'),
        sa.Column('facility_id', sa.Integer(), nullable=False, comment='施設ID'),
        sa.Column('conversation_id', sa.Integer(), nullable=True, comment='会話ID'),
        sa.Column('message_id', sa.Integer(), nullable=True, comment='メッセージID'),
        sa.Column('guest_language', sa.String(length=10), nullable=True, comment='ゲスト言語'),
        sa.Column('viewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='閲覧日時'),
        sa.ForeignKeyConstraint(['faq_id'], ['faqs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # インデックス作成
    op.create_index('idx_faq_view_logs_faq', 'faq_view_logs', ['faq_id'])
    op.create_index('idx_faq_view_logs_facility', 'faq_view_logs', ['facility_id'])
    op.create_index('idx_faq_view_logs_viewed', 'faq_view_logs', ['viewed_at'], postgresql_ops={'viewed_at': 'DESC'})


def downgrade() -> None:
    """
    テーブル削除
    """
    op.drop_index('idx_faq_view_logs_viewed', table_name='faq_view_logs')
    op.drop_index('idx_faq_view_logs_facility', table_name='faq_view_logs')
    op.drop_index('idx_faq_view_logs_faq', table_name='faq_view_logs')
    op.drop_table('faq_view_logs')
    
    op.drop_index('idx_activity_logs_created', table_name='admin_activity_logs')
    op.drop_index('idx_activity_logs_action', table_name='admin_activity_logs')
    op.drop_index('idx_activity_logs_facility', table_name='admin_activity_logs')
    op.drop_index('idx_activity_logs_user', table_name='admin_activity_logs')
    op.drop_table('admin_activity_logs')
