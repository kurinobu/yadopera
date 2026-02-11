"""fix_faq_limit_and_language_limit_by_plan

Revision ID: 014
Revises: 013
Create Date: 2026-02-10

CSV一括登録機能 Phase 0: plan_limits.py と DB の整合を取る。
- faq_limit: Free=20, Mini=30, Small=50, Standard=100, Premium=NULL
- language_limit: Free=1, Mini=2, Small=3, Standard=4, Premium=NULL
"""
from alembic import op

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # faq_limit を plan_type ごとに更新（plan_limits.py と一致）
    op.execute("""
        UPDATE facilities
        SET faq_limit = CASE plan_type
            WHEN 'Free' THEN 20
            WHEN 'Mini' THEN 30
            WHEN 'Small' THEN 50
            WHEN 'Standard' THEN 100
            WHEN 'Premium' THEN NULL
            ELSE faq_limit
        END
    """)
    # language_limit を plan_type ごとに更新
    op.execute("""
        UPDATE facilities
        SET language_limit = CASE plan_type
            WHEN 'Free' THEN 1
            WHEN 'Mini' THEN 2
            WHEN 'Small' THEN 3
            WHEN 'Standard' THEN 4
            WHEN 'Premium' THEN NULL
            ELSE language_limit
        END
    """)


def downgrade() -> None:
    # 012 適用後の状態に戻す（全プラン faq_limit=20, language_limit=1、Premium のみ NULL）
    op.execute("""
        UPDATE facilities
        SET faq_limit = CASE WHEN plan_type = 'Premium' THEN NULL ELSE 20 END,
            language_limit = CASE WHEN plan_type = 'Premium' THEN NULL ELSE 1 END
    """)
