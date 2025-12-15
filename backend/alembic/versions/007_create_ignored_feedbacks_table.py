"""create ignored_feedbacks table

Revision ID: 007_create_ignored_feedbacks_table
Revises: 006_add_qr_codes_table
Create Date: 2025-12-14 14:23:19.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007_ignored_feedbacks'
down_revision: Union[str, None] = '006_add_qr_codes_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ignored_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('ignored_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ignored_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ignored_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'facility_id', name='uq_ignored_feedback_message_facility')
    )
    op.create_index('idx_ignored_feedbacks_message_id', 'ignored_feedbacks', ['message_id'])
    op.create_index('idx_ignored_feedbacks_facility_id', 'ignored_feedbacks', ['facility_id'])


def downgrade() -> None:
    op.drop_index('idx_ignored_feedbacks_facility_id', table_name='ignored_feedbacks')
    op.drop_index('idx_ignored_feedbacks_message_id', table_name='ignored_feedbacks')
    op.drop_table('ignored_feedbacks')
