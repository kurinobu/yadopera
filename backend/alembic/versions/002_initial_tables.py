"""Create initial tables

Revision ID: 002_initial_tables
Revises: 001_enable_pgvector
Create Date: 2025-11-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_initial_tables'
down_revision: Union[str, None] = '001_enable_pgvector'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # facilities テーブル作成
    op.create_table(
        'facilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('wifi_ssid', sa.String(length=100), nullable=True),
        sa.Column('wifi_password', sa.String(length=100), nullable=True),
        sa.Column('check_in_time', sa.Time(), nullable=True, server_default='15:00:00'),
        sa.Column('check_out_time', sa.Time(), nullable=True, server_default='11:00:00'),
        sa.Column('house_rules', sa.Text(), nullable=True),
        sa.Column('local_info', sa.Text(), nullable=True),
        sa.Column('languages', postgresql.ARRAY(sa.String()), nullable=True, server_default=sa.text("ARRAY['en']")),
        sa.Column('timezone', sa.String(length=50), nullable=True, server_default='Asia/Tokyo'),
        sa.Column('subscription_plan', sa.String(length=50), nullable=True, server_default='small'),
        sa.Column('monthly_question_limit', sa.Integer(), nullable=True, server_default='200'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_facilities_slug', 'facilities', ['slug'], unique=True)
    op.create_index('idx_facilities_is_active', 'facilities', ['is_active'])

    # users テーブル作成
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True, server_default='staff'),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_facility_id', 'users', ['facility_id'])
    # 条件付きインデックス（password_reset_tokenがNULLでない場合のみ）
    op.execute("""
        CREATE INDEX idx_users_password_reset_token 
        ON users(password_reset_token) 
        WHERE password_reset_token IS NOT NULL
    """)

    # conversations テーブル作成
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('guest_language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('location', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_escalated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('total_messages', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('auto_resolved', sa.Boolean(), nullable=True, server_default='false'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_facility_id', 'conversations', ['facility_id'])
    op.create_index('idx_conversations_session_id', 'conversations', ['session_id'], unique=True)
    op.create_index('idx_conversations_last_activity', 'conversations', ['last_activity_at'])
    op.create_index('idx_conversations_is_escalated', 'conversations', ['is_escalated'])

    # messages テーブル作成
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ai_confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('matched_faq_ids', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    # 条件付きインデックス（ai_confidenceがNULLでない場合のみ）
    op.execute("""
        CREATE INDEX idx_messages_ai_confidence 
        ON messages(ai_confidence) 
        WHERE ai_confidence IS NOT NULL
    """)

    # session_tokens テーブル作成
    op.create_table(
        'session_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=10), nullable=False),
        sa.Column('primary_session_id', sa.String(length=100), nullable=False),
        sa.Column('linked_session_ids', postgresql.ARRAY(postgresql.TEXT()), nullable=True, server_default=sa.text("ARRAY[]::TEXT[]")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_session_tokens_token', 'session_tokens', ['token'], unique=True)
    op.create_index('idx_session_tokens_facility_id', 'session_tokens', ['facility_id'])
    op.create_index('idx_session_tokens_expires_at', 'session_tokens', ['expires_at'])
    op.create_index('idx_session_tokens_primary_session_id', 'session_tokens', ['primary_session_id'])
    
    # session_tokens.primary_session_id の外部キー制約（conversations.session_idを参照）
    # 注意: session_idは主キーではないため、手動で外部キー制約を追加
    op.execute("""
        ALTER TABLE session_tokens 
        ADD CONSTRAINT fk_session_tokens_primary_session_id 
        FOREIGN KEY (primary_session_id) 
        REFERENCES conversations(session_id) 
        ON DELETE CASCADE
    """)


def downgrade() -> None:
    # 外部キー制約を削除
    op.execute("""
        ALTER TABLE session_tokens 
        DROP CONSTRAINT IF EXISTS fk_session_tokens_primary_session_id
    """)
    
    # テーブルを削除（依存関係の順序に注意）
    op.drop_index('idx_session_tokens_primary_session_id', table_name='session_tokens')
    op.drop_index('idx_session_tokens_expires_at', table_name='session_tokens')
    op.drop_index('idx_session_tokens_facility_id', table_name='session_tokens')
    op.drop_index('idx_session_tokens_token', table_name='session_tokens')
    op.drop_table('session_tokens')
    
    op.drop_index('idx_messages_ai_confidence', table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('idx_conversations_is_escalated', table_name='conversations')
    op.drop_index('idx_conversations_last_activity', table_name='conversations')
    op.drop_index('idx_conversations_session_id', table_name='conversations')
    op.drop_index('idx_conversations_facility_id', table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('idx_users_password_reset_token', table_name='users')
    op.drop_index('idx_users_facility_id', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    
    op.drop_index('idx_facilities_is_active', table_name='facilities')
    op.drop_index('idx_facilities_slug', table_name='facilities')
    op.drop_table('facilities')

