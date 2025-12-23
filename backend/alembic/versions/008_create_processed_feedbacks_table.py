"""create processed_feedbacks table

Revision ID: 008_create_processed_feedbacks_table
Revises: 007_ignored_feedbacks
Create Date: 2025-12-16 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '008_processed_feedbacks'
down_revision: Union[str, None] = '007_ignored_feedbacks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'processed_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('faq_suggestion_id', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['faq_suggestion_id'], ['faq_suggestions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'facility_id', name='uq_processed_feedback_message_facility')
    )
    op.create_index('idx_processed_feedbacks_message_id', 'processed_feedbacks', ['message_id'])
    op.create_index('idx_processed_feedbacks_facility_id', 'processed_feedbacks', ['facility_id'])
    op.create_index('idx_processed_feedbacks_faq_suggestion_id', 'processed_feedbacks', ['faq_suggestion_id'])


def downgrade() -> None:
    op.drop_index('idx_processed_feedbacks_faq_suggestion_id', table_name='processed_feedbacks')
    op.drop_index('idx_processed_feedbacks_facility_id', table_name='processed_feedbacks')
    op.drop_index('idx_processed_feedbacks_message_id', table_name='processed_feedbacks')
    op.drop_table('processed_feedbacks')


