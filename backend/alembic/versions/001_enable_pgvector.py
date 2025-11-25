"""Enable pgvector extension

Revision ID: 001_enable_pgvector
Revises: 
Create Date: 2025-11-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_enable_pgvector'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector拡張を有効化
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # pgvector拡張を削除（注意: 既存のベクトルカラムがある場合は削除できない）
    op.execute("DROP EXTENSION IF EXISTS vector")


