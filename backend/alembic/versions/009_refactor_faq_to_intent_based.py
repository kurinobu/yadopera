"""refactor FAQ to intent-based structure

Revision ID: 009_refactor_faq_to_intent_based
Revises: 008_processed_feedbacks
Create Date: 2025-12-23 09:29:09.134000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '009_refactor_faq_to_intent_based'
down_revision: Union[str, None] = '008_processed_feedbacks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    FAQをインテントベースの構造にリファクタリング
    
    1. faq_translationsテーブル作成
    2. 既存faqsテーブルのデータ移行（language, question, answer, embeddingをfaq_translationsに移動）
    3. faqsテーブルの構造変更（language, question, answer, embeddingを削除、intent_keyを追加）
    4. インデックス作成・削除
    """
    
    # Step 1: faq_translationsテーブル作成
    op.create_table(
        'faq_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('faq_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['faq_id'], ['faqs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('faq_id', 'language', name='uq_faq_translation_faq_language')
    )
    
    # embeddingカラムをvector(1536)型で追加（pgvector型は直接SQLで定義）
    op.execute("""
        ALTER TABLE faq_translations 
        ADD COLUMN embedding vector(1536)
    """)
    
    # インデックス作成
    op.create_index('idx_faq_translations_faq_id', 'faq_translations', ['faq_id'])
    op.create_index('idx_faq_translations_language', 'faq_translations', ['language'])
    
    # Step 2: 既存faqsテーブルのデータ移行
    # 既存のfaqsテーブルのデータをfaq_translationsテーブルに移動
    # 注意: intent_keyは一時的に'legacy_' + idを使用（ステップ3で適切なintent_keyを生成）
    op.execute("""
        INSERT INTO faq_translations (faq_id, language, question, answer, embedding, created_at, updated_at)
        SELECT 
            id as faq_id,
            COALESCE(language, 'en') as language,
            question,
            answer,
            embedding,
            created_at,
            updated_at
        FROM faqs
        WHERE question IS NOT NULL AND answer IS NOT NULL
    """)
    
    # pgvectorインデックス（IVFFlat: 高速近似最近傍探索）
    # 注意: データ移行後にインデックスを作成（データが存在する場合のみ）
    # データが存在しない場合はインデックス作成をスキップ
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM faq_translations WHERE embedding IS NOT NULL LIMIT 1) THEN
                CREATE INDEX IF NOT EXISTS idx_faq_translations_embedding 
                ON faq_translations 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            END IF;
        END $$;
    """)
    
    # Step 3: faqsテーブルの構造変更
    # 3.1: intent_keyカラムを追加（一時的に'legacy_' + idを使用）
    op.execute("""
        ALTER TABLE faqs 
        ADD COLUMN intent_key VARCHAR(100)
    """)
    
    # 既存データに一時的なintent_keyを設定（ステップ3で適切なintent_keyを生成）
    op.execute("""
        UPDATE faqs 
        SET intent_key = 'legacy_' || id::text
        WHERE intent_key IS NULL
    """)
    
    # intent_keyをNOT NULLに変更
    op.execute("""
        ALTER TABLE faqs 
        ALTER COLUMN intent_key SET NOT NULL
    """)
    
    # 3.2: UNIQUE制約を追加（facility_id, intent_key）
    op.create_index('idx_faqs_facility_intent', 'faqs', ['facility_id', 'intent_key'], unique=True)
    
    # 3.3: 既存のインデックスを確認（必要に応じて削除）
    # languageカラムのインデックスは削除不要（既に存在しない可能性が高い）
    # embeddingカラムのインデックスが存在する場合は削除（faq_translationsに移動済み）
    op.execute("""
        DROP INDEX IF EXISTS idx_faqs_embedding;
    """)
    
    # 3.4: language, question, answer, embeddingカラムを削除
    # 注意: データ移行が完了していることを確認してから削除
    op.drop_column('faqs', 'language')
    op.drop_column('faqs', 'question')
    op.drop_column('faqs', 'answer')
    
    # embeddingカラムを削除（vector型のため直接SQLで削除）
    op.execute("""
        ALTER TABLE faqs 
        DROP COLUMN IF EXISTS embedding
    """)


def downgrade() -> None:
    """
    リファクタリングをロールバック
    
    1. faqsテーブルにlanguage, question, answer, embeddingカラムを復元
    2. faq_translationsテーブルからデータをfaqsテーブルに戻す
    3. intent_keyカラムを削除
    4. faq_translationsテーブルを削除
    """
    
    # Step 1: faqsテーブルにカラムを復元
    op.add_column('faqs', sa.Column('language', sa.String(length=10), nullable=True, server_default='en'))
    op.add_column('faqs', sa.Column('question', sa.Text(), nullable=True))
    op.add_column('faqs', sa.Column('answer', sa.Text(), nullable=True))
    
    # embeddingカラムをvector(1536)型で復元
    op.execute("""
        ALTER TABLE faqs 
        ADD COLUMN embedding vector(1536)
    """)
    
    # Step 2: faq_translationsテーブルからデータをfaqsテーブルに戻す
    # 注意: 複数の翻訳がある場合、最初の1つだけを復元（言語ごとに別レコードとして復元できないため）
    op.execute("""
        UPDATE faqs f
        SET 
            language = ft.language,
            question = ft.question,
            answer = ft.answer,
            embedding = ft.embedding
        FROM (
            SELECT 
                faq_id,
                language,
                question,
                answer,
                embedding,
                ROW_NUMBER() OVER (PARTITION BY faq_id ORDER BY created_at ASC) as rn
            FROM faq_translations
        ) ft
        WHERE f.id = ft.faq_id AND ft.rn = 1
    """)
    
    # Step 3: intent_keyカラムとUNIQUE制約を削除
    op.drop_index('idx_faqs_facility_intent', table_name='faqs')
    op.drop_column('faqs', 'intent_key')
    
    # Step 4: faq_translationsテーブルを削除
    op.drop_index('idx_faq_translations_embedding', table_name='faq_translations')
    op.drop_index('idx_faq_translations_language', table_name='faq_translations')
    op.drop_index('idx_faq_translations_faq_id', table_name='faq_translations')
    op.drop_table('faq_translations')

