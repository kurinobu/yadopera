"""Add facility settings fields

Revision ID: 005_add_facility_settings_fields
Revises: 004_add_faq_suggestions_table
Create Date: 2025-12-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005_add_facility_settings_fields'
down_revision: Union[str, None] = '004_add_faq_suggestions_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # facilities テーブルに staff_absence_periods と icon_url を追加（既存チェック付き）
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE facilities ADD COLUMN staff_absence_periods JSONB DEFAULT '[]';
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE facilities ADD COLUMN icon_url VARCHAR(255);
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """)


def downgrade() -> None:
    # カラムを削除
    op.drop_column('facilities', 'icon_url')
    op.drop_column('facilities', 'staff_absence_periods')


