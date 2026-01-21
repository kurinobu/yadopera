"""add_facility_plan_columns

Revision ID: 012
Revises: 011
Create Date: 2025-01-14 16:11:53.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    """
    facilitiesテーブルにプラン関連カラムを追加
    - plan_type: プラン種別（Free/Mini/Small/Standard/Premium）
    - monthly_question_limit: 月間質問数上限（Miniの場合はNULL）
    - faq_limit: FAQ登録数上限（Premiumの場合はNULL）
    - language_limit: 同時利用言語数上限（Premiumの場合はNULL）
    - plan_started_at: プラン開始日時
    - plan_updated_at: プラン更新日時
    """
    # plan_typeカラム追加（既存のsubscription_planから値をコピー）
    op.add_column('facilities', 
        sa.Column('plan_type', sa.String(length=20), server_default='Free', nullable=False)
    )
    
    # 既存のsubscription_planの値をplan_typeにコピー（大文字始まりに変換）
    op.execute("""
        UPDATE facilities 
        SET plan_type = CASE 
            WHEN LOWER(subscription_plan) = 'free' THEN 'Free'
            WHEN LOWER(subscription_plan) = 'mini' THEN 'Mini'
            WHEN LOWER(subscription_plan) = 'small' THEN 'Small'
            WHEN LOWER(subscription_plan) = 'standard' THEN 'Standard'
            WHEN LOWER(subscription_plan) = 'premium' THEN 'Premium'
            ELSE 'Free'
        END
    """)
    
    # CHECK制約を追加
    op.create_check_constraint(
        'ck_facilities_plan_type',
        'facilities',
        "plan_type IN ('Free', 'Mini', 'Small', 'Standard', 'Premium')"
    )
    
    # monthly_question_limitカラム追加（既存のmonthly_question_limitがある場合はそのまま使用）
    # 既存のカラムがある場合は、新しいカラム名を追加しない（既存を活用）
    # 引き継ぎドキュメントでは新しいカラムとして記載されているが、
    # 既存のmonthly_question_limitを活用するため、コメントのみ追加
    # 既存のmonthly_question_limitのデフォルト値を30に更新（Freeプラン用）
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = 30 
        WHERE subscription_plan = 'free' AND monthly_question_limit IS NULL
    """)
    
    # faq_limitカラム追加（Premiumの場合はNULL許可）
    op.add_column('facilities',
        sa.Column('faq_limit', sa.Integer(), server_default='20', nullable=True)
    )
    
    # language_limitカラム追加（Premiumの場合はNULL許可）
    op.add_column('facilities',
        sa.Column('language_limit', sa.Integer(), server_default='1', nullable=True)
    )
    
    # plan_started_atカラム追加
    op.add_column('facilities',
        sa.Column('plan_started_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )
    
    # plan_updated_atカラム追加（nullable=True）
    op.add_column('facilities',
        sa.Column('plan_updated_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # プラン別のデフォルト値設定
    # Freeプラン: monthly_question_limit = 30
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = 30 
        WHERE plan_type = 'Free' AND monthly_question_limit IS NULL
    """)
    
    # Miniプラン: monthly_question_limit = NULL（無制限）
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = NULL 
        WHERE plan_type = 'Mini'
    """)
    
    # Smallプラン: monthly_question_limit = 200（既存のデフォルト値）
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = 200 
        WHERE plan_type = 'Small' AND monthly_question_limit IS NULL
    """)
    
    # Standardプラン: monthly_question_limit = 500
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = 500 
        WHERE plan_type = 'Standard' AND monthly_question_limit IS NULL
    """)
    
    # Premiumプラン: monthly_question_limit = 1000
    op.execute("""
        UPDATE facilities 
        SET monthly_question_limit = 1000 
        WHERE plan_type = 'Premium' AND monthly_question_limit IS NULL
    """)
    
    # Premiumプラン: faq_limit = NULL（無制限）、language_limit = NULL（無制限）
    op.execute("""
        UPDATE facilities 
        SET faq_limit = NULL, language_limit = NULL 
        WHERE plan_type = 'Premium'
    """)


def downgrade():
    """
    追加したカラムを削除
    """
    op.drop_constraint('ck_facilities_plan_type', 'facilities', type_='check')
    op.drop_column('facilities', 'plan_updated_at')
    op.drop_column('facilities', 'plan_started_at')
    op.drop_column('facilities', 'language_limit')
    op.drop_column('facilities', 'faq_limit')
    op.drop_column('facilities', 'plan_type')

