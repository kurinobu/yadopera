"""Add faq_suggestions table

Revision ID: 004_add_faq_suggestions_table
Revises: 003_add_week2_tables
Create Date: 2025-12-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_faq_suggestions_table'
down_revision: Union[str, None] = '003_add_week2_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # faq_suggestions テーブル作成
    op.create_table(
        'faq_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('source_message_id', sa.Integer(), nullable=False),
        sa.Column('suggested_question', sa.Text(), nullable=False),
        sa.Column('suggested_answer', sa.Text(), nullable=False),
        sa.Column('suggested_category', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('created_faq_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_faq_id'], ['faqs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_faq_suggestions_facility_id', 'faq_suggestions', ['facility_id'])
    op.create_index('idx_faq_suggestions_status', 'faq_suggestions', ['status'])
    op.create_index('idx_faq_suggestions_created_at', 'faq_suggestions', ['created_at'])
    op.create_index('idx_faq_suggestions_source_message_id', 'faq_suggestions', ['source_message_id'])


def downgrade() -> None:
    # インデックスを削除
    op.drop_index('idx_faq_suggestions_source_message_id', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_created_at', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_status', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_facility_id', table_name='faq_suggestions')
    
    # テーブルを削除
    op.drop_table('faq_suggestions')


