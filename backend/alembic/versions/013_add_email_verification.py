"""add email verification

Revision ID: 013
Revises: 012
Create Date: 2026-01-27 14:20:54.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '96b7b4fa4d3b'  # 現在のhead（add_admin_activity_logs_and_faq_view_logs_tables）
branch_labels = None
depends_on = None


def upgrade() -> None:
    # email_verified カラム追加（デフォルト: False）
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), 
                                      nullable=False, server_default='false'))
    
    # verification_token カラム追加
    op.add_column('users', sa.Column('verification_token', sa.String(255), 
                                      nullable=True))
    
    # verification_token_expires カラム追加
    op.add_column('users', sa.Column('verification_token_expires', 
                                      sa.DateTime(timezone=True), nullable=True))
    
    # verification_token インデックス作成（部分インデックス）
    op.execute("""
        CREATE INDEX idx_users_verification_token 
        ON users(verification_token) 
        WHERE verification_token IS NOT NULL
    """)
    
    # 🔴 修正: 既存の「有効な」ユーザーのみをメール確認済みとして扱う
    # is_active=False のユーザー（削除済み、停止中など）は除外
    op.execute("""
        UPDATE users 
        SET email_verified = true 
        WHERE id IS NOT NULL 
          AND is_active = true
    """)


def downgrade() -> None:
    # インデックス削除
    op.drop_index('idx_users_verification_token', table_name='users')
    
    # カラム削除
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'email_verified')

