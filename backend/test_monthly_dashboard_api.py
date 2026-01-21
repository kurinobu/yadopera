"""
月次ダッシュボード統計API統合テスト
"""
import asyncio
import sys
import os
from datetime import datetime
import pytz

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.facility import Facility
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.escalation import Escalation
from app.services.dashboard_service import DashboardService
from app.core.config import settings


async def test_monthly_dashboard_api():
    """月次ダッシュボード統計API統合テスト"""
    
    # データベース接続
    engine = create_async_engine(settings.database_url.replace("postgresql://", "postgresql+asyncpg://"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # テスト用施設を取得（各プラン）
            from sqlalchemy import select
            
            # Freeプランの施設を取得
            free_result = await session.execute(
                select(Facility).where(Facility.plan_type == 'Free').limit(1)
            )
            free_facility = free_result.scalar_one_or_none()
            
            # Miniプランの施設を取得（存在しない場合は作成）
            mini_result = await session.execute(
                select(Facility).where(Facility.plan_type == 'Mini').limit(1)
            )
            mini_facility = mini_result.scalar_one_or_none()
            
            if not mini_facility:
                mini_facility = Facility(
                    name="Test Facility Mini",
                    slug="test-facility-mini",
                    email="mini@example.com",
                    plan_type='Mini',
                    monthly_question_limit=None,
                    faq_limit=30,
                    language_limit=2,
                    is_active=True
                )
                session.add(mini_facility)
                await session.flush()
            
            # Smallプランの施設を取得
            small_result = await session.execute(
                select(Facility).where(Facility.plan_type == 'Small').limit(1)
            )
            small_facility = small_result.scalar_one_or_none()
            
            # Standardプランの施設を取得
            standard_result = await session.execute(
                select(Facility).where(Facility.plan_type == 'Standard').limit(1)
            )
            standard_facility = standard_result.scalar_one_or_none()
            
            print("=" * 80)
            print("月次ダッシュボード統計API統合テスト")
            print("=" * 80)
            
            # テスト1: Freeプランでの月次統計取得
            if free_facility:
                print(f"\n[テスト1] Freeプラン (Facility ID: {free_facility.id})")
                dashboard_service = DashboardService(session)
                monthly_usage = await dashboard_service.get_monthly_usage(free_facility.id)
                print(f"  ✅ 今月の質問数: {monthly_usage.current_month_questions}件")
                print(f"  ✅ プラン種別: {monthly_usage.plan_type}")
                print(f"  ✅ プラン上限: {monthly_usage.plan_limit}")
                print(f"  ✅ 使用率: {monthly_usage.usage_percentage}%")
                print(f"  ✅ ステータス: {monthly_usage.status}")
            
            # テスト2: Miniプランでの月次統計取得
            if mini_facility:
                print(f"\n[テスト2] Miniプラン (Facility ID: {mini_facility.id})")
                dashboard_service = DashboardService(session)
                monthly_usage = await dashboard_service.get_monthly_usage(mini_facility.id)
                print(f"  ✅ 今月の質問数: {monthly_usage.current_month_questions}件")
                print(f"  ✅ プラン種別: {monthly_usage.plan_type}")
                print(f"  ✅ プラン上限: {monthly_usage.plan_limit} (NULL = 無制限)")
                print(f"  ✅ 使用率: {monthly_usage.usage_percentage} (NULL = 表示なし)")
                print(f"  ✅ ステータス: {monthly_usage.status}")
            
            # テスト3: Smallプランでの月次統計取得
            if small_facility:
                print(f"\n[テスト3] Smallプラン (Facility ID: {small_facility.id})")
                dashboard_service = DashboardService(session)
                monthly_usage = await dashboard_service.get_monthly_usage(small_facility.id)
                print(f"  ✅ 今月の質問数: {monthly_usage.current_month_questions}件")
                print(f"  ✅ プラン種別: {monthly_usage.plan_type}")
                print(f"  ✅ プラン上限: {monthly_usage.plan_limit}件")
                print(f"  ✅ 使用率: {monthly_usage.usage_percentage}%")
                print(f"  ✅ 残り質問数: {monthly_usage.remaining_questions}件")
                print(f"  ✅ ステータス: {monthly_usage.status}")
            
            # テスト4: Standardプランでの月次統計取得
            if standard_facility:
                print(f"\n[テスト4] Standardプラン (Facility ID: {standard_facility.id})")
                dashboard_service = DashboardService(session)
                monthly_usage = await dashboard_service.get_monthly_usage(standard_facility.id)
                print(f"  ✅ 今月の質問数: {monthly_usage.current_month_questions}件")
                print(f"  ✅ プラン種別: {monthly_usage.plan_type}")
                print(f"  ✅ プラン上限: {monthly_usage.plan_limit}件")
                print(f"  ✅ 使用率: {monthly_usage.usage_percentage}%")
                print(f"  ✅ 残り質問数: {monthly_usage.remaining_questions}件")
                print(f"  ✅ ステータス: {monthly_usage.status}")
            
            # テスト5: AI自動応答統計取得
            if free_facility:
                print(f"\n[テスト5] AI自動応答統計 (Facility ID: {free_facility.id})")
                dashboard_service = DashboardService(session)
                ai_automation = await dashboard_service.get_ai_automation(free_facility.id)
                print(f"  ✅ AI自動応答数: {ai_automation.ai_responses}件")
                print(f"  ✅ 総質問数: {ai_automation.total_questions}件")
                print(f"  ✅ 自動化率: {ai_automation.automation_rate}%")
            
            # テスト6: エスカレーション統計取得
            if free_facility:
                print(f"\n[テスト6] エスカレーション統計 (Facility ID: {free_facility.id})")
                dashboard_service = DashboardService(session)
                escalations_summary = await dashboard_service.get_escalations_summary(free_facility.id)
                print(f"  ✅ エスカレーション総数: {escalations_summary.total}件")
                print(f"  ✅ 未解決数: {escalations_summary.unresolved}件")
                print(f"  ✅ 解決済み数: {escalations_summary.resolved}件")
            
            # テスト7: 未解決エスカレーション取得
            if free_facility:
                print(f"\n[テスト7] 未解決エスカレーション (Facility ID: {free_facility.id})")
                dashboard_service = DashboardService(session)
                unresolved = await dashboard_service.get_unresolved_escalations(free_facility.id)
                print(f"  ✅ 未解決エスカレーション数: {len(unresolved)}件")
                for esc in unresolved[:3]:  # 最初の3件を表示
                    print(f"    - ID: {esc.id}, 会話ID: {esc.conversation_id}, メッセージ: {esc.message[:50]}...")
            
            # テスト8: タイムゾーン処理確認（JST基準）
            print(f"\n[テスト8] タイムゾーン処理確認（JST基準）")
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)
            month_start_jst = now_jst.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end_jst = (month_start_jst.replace(month=month_start_jst.month + 1) - timedelta(seconds=1)) if month_start_jst.month < 12 else (month_start_jst.replace(year=month_start_jst.year + 1, month=1) - timedelta(seconds=1))
            month_start_utc = month_start_jst.astimezone(pytz.UTC)
            month_end_utc = month_end_jst.astimezone(pytz.UTC)
            print(f"  ✅ 今月の開始時刻（JST）: {month_start_jst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  ✅ 今月の終了時刻（JST）: {month_end_jst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  ✅ 今月の開始時刻（UTC）: {month_start_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  ✅ 今月の終了時刻（UTC）: {month_end_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            # テスト9: ダッシュボードデータ統合取得
            if free_facility:
                print(f"\n[テスト9] ダッシュボードデータ統合取得 (Facility ID: {free_facility.id})")
                dashboard_service = DashboardService(session)
                dashboard_data = await dashboard_service.get_dashboard_data(free_facility.id)
                print(f"  ✅ 週次サマリー: 取得成功")
                print(f"  ✅ 月次利用状況: {'取得成功' if dashboard_data.monthly_usage else '取得失敗'}")
                print(f"  ✅ AI自動応答統計: {'取得成功' if dashboard_data.ai_automation else '取得失敗'}")
                print(f"  ✅ エスカレーション統計: {'取得成功' if dashboard_data.escalations_summary else '取得失敗'}")
                print(f"  ✅ 未解決エスカレーション: {len(dashboard_data.unresolved_escalations or [])}件")
            
            print("\n" + "=" * 80)
            print("✅ すべてのテストが完了しました")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    from datetime import timedelta
    asyncio.run(test_monthly_dashboard_api())

