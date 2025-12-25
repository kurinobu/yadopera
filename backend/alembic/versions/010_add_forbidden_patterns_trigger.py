"""add_forbidden_patterns_trigger

Revision ID: 010
Revises: 009
Create Date: 2025-12-23 01:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009_refactor_faq_to_intent_based'
branch_labels = None
depends_on = None


def upgrade():
    """
    禁止用語検出トリガー関数を追加
    check-in関連のテストデータ混入を防ぐため、データベースレベルで制約を追加
    """
    
    # トリガー関数の作成（テスト施設のみチェック）
    op.execute("""
        CREATE OR REPLACE FUNCTION check_forbidden_patterns()
        RETURNS TRIGGER AS $$
        DECLARE
            forbidden_patterns TEXT[] := ARRAY[
                'check-in', 'チェックイン', 'checkin',
                'Check-in', 'Check-In', 'CHECK-IN',
                'check in', 'Check In', 'CHECK IN'
            ];
            content_lower TEXT;
            pattern TEXT;
            is_test_facility BOOLEAN := FALSE;
        BEGIN
            -- messagesテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'messages' THEN
                SELECT EXISTS (
                    SELECT 1 FROM conversations c
                    JOIN facilities f ON c.facility_id = f.id
                    WHERE c.id = NEW.conversation_id
                    AND f.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(NEW.content);
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            -- 「checkout」「checking」などは除外
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.content, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            -- faq_translationsテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'faq_translations' THEN
                SELECT EXISTS (
                    SELECT 1 FROM faqs f
                    JOIN facilities fac ON f.facility_id = fac.id
                    WHERE f.id = NEW.faq_id
                    AND fac.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(NEW.question || ' ' || COALESCE(NEW.answer, ''));
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.question, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            -- faq_suggestionsテーブルの場合: テスト施設かどうかをチェック
            IF TG_TABLE_NAME = 'faq_suggestions' THEN
                SELECT EXISTS (
                    SELECT 1 FROM facilities f
                    WHERE f.id = NEW.facility_id
                    AND f.slug = 'test-facility'
                ) INTO is_test_facility;
                
                IF is_test_facility THEN
                    content_lower := LOWER(COALESCE(NEW.suggested_question, ''));
                    FOREACH pattern IN ARRAY forbidden_patterns LOOP
                        IF content_lower LIKE '%' || LOWER(pattern) || '%' THEN
                            IF content_lower NOT LIKE '%checkout%' 
                               AND content_lower NOT LIKE '%checking%' THEN
                                RAISE EXCEPTION '禁止用語が検出されました: % (パターン: %). このアプリはチェックイン済みのゲストが使用するため、チェックイン時間を聞く質問は現実的でない', NEW.suggested_question, pattern;
                            END IF;
                        END IF;
                    END LOOP;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # messagesテーブルのトリガー（全メッセージに対して実行、関数内でテスト施設のみチェック）
    op.execute("""
        CREATE TRIGGER check_forbidden_patterns_messages
            BEFORE INSERT OR UPDATE ON messages
            FOR EACH ROW
            EXECUTE FUNCTION check_forbidden_patterns();
    """)
    
    # faq_translationsテーブルのトリガー（全翻訳に対して実行、関数内でテスト施設のみチェック）
    op.execute("""
        CREATE TRIGGER check_forbidden_patterns_faq_translations
            BEFORE INSERT OR UPDATE ON faq_translations
            FOR EACH ROW
            EXECUTE FUNCTION check_forbidden_patterns();
    """)
    
    # faq_suggestionsテーブルのトリガー（全提案に対して実行、関数内でテスト施設のみチェック）
    op.execute("""
        CREATE TRIGGER check_forbidden_patterns_faq_suggestions
            BEFORE INSERT OR UPDATE ON faq_suggestions
            FOR EACH ROW
            EXECUTE FUNCTION check_forbidden_patterns();
    """)


def downgrade():
    """トリガーと関数を削除"""
    op.execute("DROP TRIGGER IF EXISTS check_forbidden_patterns_messages ON messages;")
    op.execute("DROP TRIGGER IF EXISTS check_forbidden_patterns_faq_translations ON faq_translations;")
    op.execute("DROP TRIGGER IF EXISTS check_forbidden_patterns_faq_suggestions ON faq_suggestions;")
    op.execute("DROP FUNCTION IF EXISTS check_forbidden_patterns();")

