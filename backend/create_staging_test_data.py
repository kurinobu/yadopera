"""
ステージング環境用テストデータ作成スクリプト
ステージング環境のデータベースにテストユーザーを作成
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.security import hash_password
from app.core.config import settings

# すべてのモデルをインポート（リレーションシップ解決のため）
from app.models.facility import Facility
from app.models.user import User
from app.models.faq_suggestion import FAQSuggestion  # リレーションシップ解決のため
from sqlalchemy import select

async def create_staging_test_data():
    """ステージング環境のテストデータを作成"""
    
    # 環境変数からデータベースURLを取得
    database_url = os.getenv("DATABASE_URL") or settings.database_url
    
    if not database_url:
        print("❌ エラー: DATABASE_URLが設定されていません")
        print("ステージング環境のデータベース接続情報を設定してください")
        sys.exit(1)
    
    # データベースURLを非同期用に変換
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        if "postgresql" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)
    
    print(f"📊 データベース接続: {database_url.split('@')[1] if '@' in database_url else '***'}")
    
    # データベース接続
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 既存のテスト施設を取得または作成
            result = await session.execute(
                select(Facility).where(Facility.slug == "test-facility")
            )
            test_facility = result.scalar_one_or_none()
            
            if test_facility:
                print(f"✅ 既存のテスト施設を使用します: ID={test_facility.id}, slug={test_facility.slug}")
            else:
                # テスト施設を作成
                from datetime import time
                test_facility = Facility(
                    name="Test Facility",
                    slug="test-facility",
                    email="test@example.com",
                    phone="090-1234-5678",
                    address="Test Address, Test City",
                    wifi_ssid="TestWiFi",
                    wifi_password="testpassword123",
                    check_in_time=time(15, 0),
                    check_out_time=time(11, 0),
                    house_rules="禁煙（中庭の喫煙エリアのみ可）、門限23:00、静粛時間22:00-8:00、キッチン使用可能時間~21:00",
                    local_info="最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）、レストラン: 多数あり",
                    languages=["en", "ja"],
                    timezone="Asia/Tokyo",
                    subscription_plan="small",
                    monthly_question_limit=200,
                    staff_absence_periods=[{"start_time": "22:00", "end_time": "08:00", "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]}],
                    icon_url=None,
                    is_active=True
                )
                
                session.add(test_facility)
                await session.flush()
                await session.commit()
                
                print(f"✅ テスト施設を作成しました: ID={test_facility.id}, slug={test_facility.slug}")
            
            # 既存のテストユーザーを確認
            user_result = await session.execute(
                select(User).where(User.email == "test@example.com", User.facility_id == test_facility.id)
            )
            test_user = user_result.scalar_one_or_none()
            
            if test_user:
                # 既存のユーザーのパスワードをリセット
                print(f"⚠️ 既存のテストユーザーが見つかりました: ID={test_user.id}, email={test_user.email}")
                print("パスワードをリセットします...")
                
                try:
                    password_hash = hash_password("testpassword123")
                except Exception as e:
                    print(f"⚠️ パスワードハッシュ生成でエラーが発生しました: {e}")
                    import bcrypt
                    password_hash = bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                test_user.password_hash = password_hash
                test_user.is_active = True
                await session.commit()
                
                print(f"✅ テストユーザーのパスワードをリセットしました: ID={test_user.id}, email={test_user.email}")
            else:
                # テストユーザーを作成
                print("テストユーザーを作成します...")
                
                try:
                    password_hash = hash_password("testpassword123")
                except Exception as e:
                    print(f"⚠️ パスワードハッシュ生成でエラーが発生しました: {e}")
                    import bcrypt
                    password_hash = bcrypt.hashpw("testpassword123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                test_user = User(
                    facility_id=test_facility.id,
                    email="test@example.com",
                    password_hash=password_hash,
                    full_name="Test User",
                    role="staff",
                    is_active=True
                )
                
                session.add(test_user)
                await session.flush()
                await session.commit()
                
                print(f"✅ テストユーザーを作成しました: ID={test_user.id}, email={test_user.email}")
            
            print("\n✅ ステージング環境のテストデータ作成が完了しました！")
            print("\nテストユーザー情報:")
            print(f"  メールアドレス: test@example.com")
            print(f"  パスワード: testpassword123")
            print(f"  施設slug: test-facility")
            print(f"\n管理画面ログインURL: https://yadopera-frontend-staging.onrender.com/admin/login")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_staging_test_data())

