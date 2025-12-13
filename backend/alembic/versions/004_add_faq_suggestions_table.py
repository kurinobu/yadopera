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
    # faq_suggestions テーブル作成（既存チェック付き）
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE faq_suggestions (
                id SERIAL NOT NULL,
                facility_id INTEGER NOT NULL,
                source_message_id INTEGER NOT NULL,
                suggested_question TEXT NOT NULL,
                suggested_answer TEXT NOT NULL,
                suggested_category VARCHAR(50) NOT NULL,
                language VARCHAR(10) DEFAULT 'en',
                status VARCHAR(20) DEFAULT 'pending',
                reviewed_at TIMESTAMP WITH TIME ZONE,
                reviewed_by INTEGER,
                created_faq_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                PRIMARY KEY (id),
                FOREIGN KEY(facility_id) REFERENCES facilities (id) ON DELETE CASCADE,
                FOREIGN KEY(source_message_id) REFERENCES messages (id) ON DELETE CASCADE,
                FOREIGN KEY(reviewed_by) REFERENCES users (id) ON DELETE SET NULL,
                FOREIGN KEY(created_faq_id) REFERENCES faqs (id) ON DELETE SET NULL
            );
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    # インデックス作成（既存チェック付き）
    op.execute("""
        DO $$ BEGIN
            CREATE INDEX idx_faq_suggestions_facility_id ON faq_suggestions(facility_id);
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE INDEX idx_faq_suggestions_status ON faq_suggestions(status);
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE INDEX idx_faq_suggestions_created_at ON faq_suggestions(created_at);
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE INDEX idx_faq_suggestions_source_message_id ON faq_suggestions(source_message_id);
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)


def downgrade() -> None:
    # インデックスを削除
    op.drop_index('idx_faq_suggestions_source_message_id', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_created_at', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_status', table_name='faq_suggestions')
    op.drop_index('idx_faq_suggestions_facility_id', table_name='faq_suggestions')
    
    # テーブルを削除
    op.drop_table('faq_suggestions')


