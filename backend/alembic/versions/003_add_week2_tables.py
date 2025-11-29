"""Add Week 2 tables

Revision ID: 003_add_week2_tables
Revises: 002_initial_tables
Create Date: 2025-11-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_week2_tables'
down_revision: Union[str, None] = '002_initial_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ENUM型の作成
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE faq_category AS ENUM ('basic', 'facilities', 'location', 'trouble');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE faq_suggestion_status AS ENUM ('pending', 'approved', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # faqs テーブル作成
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # embeddingカラムをvector(1536)型で追加（pgvector型は直接SQLで定義）
    op.execute("""
        ALTER TABLE faqs 
        ADD COLUMN embedding vector(1536)
    """)
    
    op.create_index('idx_faqs_facility_id', 'faqs', ['facility_id'])
    op.create_index('idx_faqs_category', 'faqs', ['category'])
    op.create_index('idx_faqs_is_active', 'faqs', ['is_active'])
    op.create_index('idx_faqs_language', 'faqs', ['language'])
    
    # pgvectorインデックス（IVFFlat: 高速近似最近傍探索）
    # 注意: MVP期間中はインデックスなしで開始、Phase 2で最適化
    # op.execute("""
    #     CREATE INDEX idx_faqs_embedding ON faqs 
    #     USING ivfflat (embedding vector_cosine_ops)
    #     WITH (lists = 100)
    # """)

    # escalations テーブル作成
    op.create_table(
        'escalations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('ai_confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('escalation_mode', sa.String(length=50), nullable=True, server_default='normal'),
        sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_channels', postgresql.ARRAY(sa.String()), nullable=True, server_default=sa.text("ARRAY['email']")),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_escalations_facility_id', 'escalations', ['facility_id'])
    op.create_index('idx_escalations_conversation_id', 'escalations', ['conversation_id'])
    op.create_index('idx_escalations_resolved_at', 'escalations', ['resolved_at'], postgresql_where=sa.text('resolved_at IS NULL'))
    op.create_index('idx_escalations_trigger_type', 'escalations', ['trigger_type'])

    # escalation_schedules テーブル作成
    op.create_table(
        'escalation_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('time_start', sa.Time(), nullable=False),
        sa.Column('time_end', sa.Time(), nullable=False),
        sa.Column('mode', sa.String(length=50), nullable=True, server_default='normal'),
        sa.Column('threshold', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.70'),
        sa.Column('languages', postgresql.ARRAY(sa.String()), nullable=True, server_default=sa.text("ARRAY['en', 'ja']")),
        sa.Column('notify_channels', postgresql.ARRAY(sa.String()), nullable=True, server_default=sa.text("ARRAY['email']")),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_escalation_schedules_facility_id', 'escalation_schedules', ['facility_id'])
    op.create_index('idx_escalation_schedules_is_active', 'escalation_schedules', ['is_active'])

    # overnight_queue テーブル作成
    op.create_table(
        'overnight_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('escalation_id', sa.Integer(), nullable=False),
        sa.Column('guest_message', sa.Text(), nullable=False),
        sa.Column('scheduled_notify_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['escalation_id'], ['escalations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_overnight_queue_facility_id', 'overnight_queue', ['facility_id'])
    op.create_index('idx_overnight_queue_scheduled_notify_at', 'overnight_queue', ['scheduled_notify_at'])
    op.create_index('idx_overnight_queue_resolved_at', 'overnight_queue', ['resolved_at'], postgresql_where=sa.text('resolved_at IS NULL'))

    # question_patterns テーブル作成
    op.create_table(
        'question_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('total_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('resolved_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_asked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # pattern_embeddingカラムをvector(1536)型で追加（pgvector型は直接SQLで定義）
    op.execute("""
        ALTER TABLE question_patterns 
        ADD COLUMN pattern_embedding vector(1536) NOT NULL
    """)
    
    # resolution_rateをGENERATED ALWAYS ASで計算されるカラムとして追加
    op.execute("""
        ALTER TABLE question_patterns 
        ADD COLUMN resolution_rate DECIMAL(3,2) 
        GENERATED ALWAYS AS (
            CASE 
                WHEN total_count > 0 THEN resolved_count::DECIMAL / total_count
                ELSE 0.0
            END
        ) STORED
    """)
    
    op.create_index('idx_question_patterns_facility_id', 'question_patterns', ['facility_id'])
    op.create_index('idx_question_patterns_resolution_rate', 'question_patterns', ['resolution_rate'])
    
    # pgvectorインデックス（IVFFlat: 高速近似最近傍探索）
    # 注意: MVP期間中はインデックスなしで開始、Phase 2で最適化
    # op.execute("""
    #     CREATE INDEX idx_question_patterns_embedding ON question_patterns 
    #     USING ivfflat (pattern_embedding vector_cosine_ops)
    #     WITH (lists = 100)
    # """)

    # guest_feedback テーブル作成
    op.create_table(
        'guest_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('feedback_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_guest_feedback_message_id', 'guest_feedback', ['message_id'])
    op.create_index('idx_guest_feedback_facility_id', 'guest_feedback', ['facility_id'])
    op.create_index('idx_guest_feedback_type', 'guest_feedback', ['feedback_type'])
    op.create_index('idx_guest_feedback_created_at', 'guest_feedback', ['created_at'])


def downgrade() -> None:
    # テーブルを削除（依存関係の順序に注意）
    op.drop_index('idx_guest_feedback_created_at', table_name='guest_feedback')
    op.drop_index('idx_guest_feedback_type', table_name='guest_feedback')
    op.drop_index('idx_guest_feedback_facility_id', table_name='guest_feedback')
    op.drop_index('idx_guest_feedback_message_id', table_name='guest_feedback')
    op.drop_table('guest_feedback')
    
    # question_patternsのインデックス削除（コメントアウトされているため不要）
    # op.execute("DROP INDEX IF EXISTS idx_question_patterns_embedding")
    op.drop_index('idx_question_patterns_resolution_rate', table_name='question_patterns')
    op.drop_index('idx_question_patterns_facility_id', table_name='question_patterns')
    op.drop_table('question_patterns')
    
    op.drop_index('idx_overnight_queue_resolved_at', table_name='overnight_queue')
    op.drop_index('idx_overnight_queue_scheduled_notify_at', table_name='overnight_queue')
    op.drop_index('idx_overnight_queue_facility_id', table_name='overnight_queue')
    op.drop_table('overnight_queue')
    
    op.drop_index('idx_escalation_schedules_is_active', table_name='escalation_schedules')
    op.drop_index('idx_escalation_schedules_facility_id', table_name='escalation_schedules')
    op.drop_table('escalation_schedules')
    
    op.drop_index('idx_escalations_trigger_type', table_name='escalations')
    op.drop_index('idx_escalations_resolved_at', table_name='escalations')
    op.drop_index('idx_escalations_conversation_id', table_name='escalations')
    op.drop_index('idx_escalations_facility_id', table_name='escalations')
    op.drop_table('escalations')
    
    # faqsのインデックス削除（コメントアウトされているため不要）
    # op.execute("DROP INDEX IF EXISTS idx_faqs_embedding")
    op.drop_index('idx_faqs_language', table_name='faqs')
    op.drop_index('idx_faqs_is_active', table_name='faqs')
    op.drop_index('idx_faqs_category', table_name='faqs')
    op.drop_index('idx_faqs_facility_id', table_name='faqs')
    op.drop_table('faqs')
    
    # ENUM型の削除
    op.execute("DROP TYPE IF EXISTS faq_suggestion_status")
    op.execute("DROP TYPE IF EXISTS faq_category")

