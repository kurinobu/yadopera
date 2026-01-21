"""add_prohibited_items_to_facilities

Revision ID: 097d9c387a86
Revises: 012
Create Date: 2026-01-20 07:06:15.060823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '097d9c387a86'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    館内ルール・周辺情報・禁止事項の実装
    - prohibited_itemsカラムを追加
    - 既存データの館内ルール・周辺情報を500文字に切り詰める
    """
    # 禁止事項カラムを追加
    op.add_column('facilities', sa.Column('prohibited_items', sa.Text(), nullable=True))
    
    # 既存データの館内ルール・周辺情報を500文字に切り詰める
    # PostgreSQLではSUBSTRING関数を使用
    op.execute("""
        UPDATE facilities 
        SET house_rules = SUBSTRING(house_rules, 1, 500) 
        WHERE LENGTH(house_rules) > 500
    """)
    op.execute("""
        UPDATE facilities 
        SET local_info = SUBSTRING(local_info, 1, 500) 
        WHERE LENGTH(local_info) > 500
    """)


def downgrade() -> None:
    """
    禁止事項カラムを削除
    """
    op.drop_column('facilities', 'prohibited_items')


