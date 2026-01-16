"""
ステージング環境のデータベース状態確認スクリプト
operator_faqsテーブルの存在とデータの有無を確認
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def check_staging_database():
    """
    ステージング環境のデータベース状態を確認
    """
    print("=" * 60)
    print("ステージング環境データベース状態確認")
    print("=" * 60)
    
    # データベースURL取得
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    
    if not database_url:
        print("❌ エラー: DATABASE_URLが設定されていません")
        print("環境変数DATABASE_URLを設定するか、Railwayダッシュボードから接続情報を取得してください")
        sys.exit(1)
    
    # asyncpg用にURLを変換
    if database_url.startswith("postgresql://"):
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql+asyncpg://"):
        async_database_url = database_url
    else:
        async_database_url = database_url
    
    # 接続情報をマスクして表示
    if "@" in async_database_url:
        masked_url = async_database_url.split("@")[1]
        print(f"📊 データベース接続: {masked_url}")
    else:
        print(f"📊 データベース接続: {async_database_url[:50]}...")
    
    try:
        # エンジン作成
        engine = create_async_engine(async_database_url, echo=False)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with AsyncSessionLocal() as session:
            print("\n" + "=" * 60)
            print("1. テーブル存在確認")
            print("=" * 60)
            
            # operator_faqsテーブルの存在確認
            check_table_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'operator_faqs'
                );
            """)
            
            result = await session.execute(check_table_query)
            operator_faqs_exists = result.scalar()
            
            if operator_faqs_exists:
                print("✅ operator_faqsテーブル: 存在")
            else:
                print("❌ operator_faqsテーブル: 存在しない")
            
            # operator_faq_translationsテーブルの存在確認
            check_table_query2 = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'operator_faq_translations'
                );
            """)
            
            result2 = await session.execute(check_table_query2)
            operator_faq_translations_exists = result2.scalar()
            
            if operator_faq_translations_exists:
                print("✅ operator_faq_translationsテーブル: 存在")
            else:
                print("❌ operator_faq_translationsテーブル: 存在しない")
            
            print("\n" + "=" * 60)
            print("2. データ存在確認")
            print("=" * 60)
            
            if operator_faqs_exists:
                # operator_faqsのデータ数確認
                count_query = text("SELECT COUNT(*) FROM operator_faqs")
                result = await session.execute(count_query)
                faq_count = result.scalar()
                print(f"📊 operator_faqs: {faq_count}件")
                
                # カテゴリ別集計
                category_query = text("""
                    SELECT category, COUNT(*) as count
                    FROM operator_faqs
                    WHERE is_active = true
                    GROUP BY category
                    ORDER BY category;
                """)
                result = await session.execute(category_query)
                categories = result.all()
                
                if categories:
                    print("\nカテゴリ別FAQ数:")
                    for row in categories:
                        print(f"  - {row.category}: {row.count}件")
                else:
                    print("⚠️  アクティブなFAQがありません")
            else:
                print("⚠️  operator_faqsテーブルが存在しないため、データ確認をスキップ")
            
            if operator_faq_translations_exists:
                # operator_faq_translationsのデータ数確認
                count_query = text("SELECT COUNT(*) FROM operator_faq_translations")
                result = await session.execute(count_query)
                translation_count = result.scalar()
                print(f"📊 operator_faq_translations: {translation_count}件")
                
                # 言語別集計
                language_query = text("""
                    SELECT language, COUNT(*) as count
                    FROM operator_faq_translations
                    GROUP BY language
                    ORDER BY language;
                """)
                result = await session.execute(language_query)
                languages = result.all()
                
                if languages:
                    print("\n言語別翻訳数:")
                    for row in languages:
                        print(f"  - {row.language}: {row.count}件")
            else:
                print("⚠️  operator_faq_translationsテーブルが存在しないため、データ確認をスキップ")
            
            print("\n" + "=" * 60)
            print("3. Alembicマイグレーション状態確認")
            print("=" * 60)
            
            # alembic_versionテーブルの存在確認
            check_alembic_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """)
            
            result = await session.execute(check_alembic_query)
            alembic_version_exists = result.scalar()
            
            if alembic_version_exists:
                # 現在のリビジョンを確認
                version_query = text("SELECT version_num FROM alembic_version")
                result = await session.execute(version_query)
                current_version = result.scalar()
                print(f"📊 現在のマイグレーションリビジョン: {current_version}")
                
                # 011リビジョンが適用されているか確認
                if current_version and current_version >= '011':
                    print("✅ マイグレーション011（operator_help_tables追加）: 適用済み")
                else:
                    print("❌ マイグレーション011（operator_help_tables追加）: 未適用")
                    print(f"   現在のリビジョン: {current_version}")
                    print("   必要なリビジョン: 011")
            else:
                print("⚠️  alembic_versionテーブルが存在しません")
            
            print("\n" + "=" * 60)
            print("4. サマリー")
            print("=" * 60)
            
            if operator_faqs_exists and operator_faq_translations_exists:
                if faq_count > 0 and translation_count > 0:
                    print("✅ データベース状態: 正常（テーブル存在、データ投入済み）")
                    print(f"   - FAQ数: {faq_count}件")
                    print(f"   - 翻訳数: {translation_count}件")
                elif faq_count == 0:
                    print("⚠️  データベース状態: テーブルは存在するが、データが投入されていません")
                    print("   初期データ投入スクリプトを実行してください:")
                    print("   python backend/scripts/insert_operator_faqs.py")
                else:
                    print("⚠️  データベース状態: テーブルは存在するが、データが不完全です")
            else:
                print("❌ データベース状態: テーブルが存在しません")
                print("   マイグレーションを実行してください:")
                print("   alembic upgrade head")
            
            print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_staging_database())

