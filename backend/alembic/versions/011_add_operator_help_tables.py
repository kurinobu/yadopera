"""add_operator_help_tables

Revision ID: 011
Revises: 010
Create Date: 2025-01-14 11:07:40.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    """
    宿泊事業者向けヘルプシステムテーブル作成
    operator_faqs と operator_faq_translations テーブルを追加
    """
    # operator_faqs テーブル作成
    op.create_table(
        'operator_faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, comment='カテゴリ（setup, qrcode, faq_management等）'),
        sa.Column('intent_key', sa.String(length=100), nullable=False, comment='意図識別キー（ユニーク）'),
        sa.Column('display_order', sa.Integer(), server_default='0', comment='表示順序'),
        sa.Column('is_active', sa.Boolean(), server_default='true', comment='有効フラグ'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('intent_key')
    )
    op.create_index('idx_operator_faqs_category', 'operator_faqs', ['category'])
    op.create_index('idx_operator_faqs_is_active', 'operator_faqs', ['is_active'])
    op.create_index('idx_operator_faqs_display_order', 'operator_faqs', ['display_order'])

    # operator_faq_translations テーブル作成
    op.create_table(
        'operator_faq_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False, comment='FAQ ID'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='ja', comment='言語コード（ja, en）'),
        sa.Column('question', sa.Text(), nullable=False, comment='質問文'),
        sa.Column('answer', sa.Text(), nullable=False, comment='回答文'),
        sa.Column('keywords', sa.Text(), nullable=True, comment='検索キーワード（カンマ区切り）'),
        sa.Column('related_url', sa.Text(), nullable=True, comment='関連する管理画面URL'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['faq_id'], ['operator_faqs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_operator_faq_translations_faq_id', 'operator_faq_translations', ['faq_id'])
    op.create_index('idx_operator_faq_translations_language', 'operator_faq_translations', ['language'])
    op.create_index('idx_faq_language', 'operator_faq_translations', ['faq_id', 'language'], unique=True)


def downgrade():
    """
    テーブル削除
    """
    op.drop_index('idx_faq_language', table_name='operator_faq_translations')
    op.drop_index('idx_operator_faq_translations_language', table_name='operator_faq_translations')
    op.drop_index('idx_operator_faq_translations_faq_id', table_name='operator_faq_translations')
    op.drop_table('operator_faq_translations')
    op.drop_index('idx_operator_faqs_display_order', table_name='operator_faqs')
    op.drop_index('idx_operator_faqs_is_active', table_name='operator_faqs')
    op.drop_index('idx_operator_faqs_category', table_name='operator_faqs')
    op.drop_table('operator_faqs')

