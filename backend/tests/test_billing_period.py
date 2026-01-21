"""
請求期間計算ユーティリティのテスト
"""

import pytest
from datetime import datetime, timedelta
import pytz
from app.utils.billing_period import calculate_billing_period


class TestCalculateBillingPeriod:
    """請求期間計算のテスト"""
    
    def test_billing_period_day_1(self):
        """プラン開始日から1日目（1回目の請求期間内）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 1, 16, 15, 30, 0))  # プラン開始から1日後
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
        assert billing_start.tzinfo == jst
        assert billing_end.tzinfo == jst
    
    def test_billing_period_day_30(self):
        """プラン開始日から30日目（1回目の請求期間の最終日）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 2, 14, 23, 59, 59))  # プラン開始から30日後（1回目の請求期間の最終秒）
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
    
    def test_billing_period_day_31(self):
        """プラン開始日から31日目（2回目の請求期間の開始日）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 2, 15, 10, 0, 0))  # プラン開始から31日後（2回目の請求期間の開始時刻）
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 2回目の請求期間: 2026-02-15 10:00:00 〜 2026-03-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-03-15 09:59:59'
    
    def test_billing_period_day_60(self):
        """プラン開始日から60日目（2回目の請求期間の最終日）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 3, 15, 9, 59, 59))  # プラン開始から60日後（2回目の請求期間の最終秒）
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 2回目の請求期間: 2026-02-15 10:00:00 〜 2026-03-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-03-15 09:59:59'
    
    def test_billing_period_start_time(self):
        """請求期間の開始時刻（プラン開始日と同じ時刻）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 1, 15, 10, 0, 0))  # プラン開始日と同じ時刻
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
    
    def test_billing_period_end_time(self):
        """請求期間の終了時刻（1回目の請求期間の最終秒）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 2, 15, 9, 59, 59))  # 1回目の請求期間の最終秒
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
    
    def test_billing_period_month_end(self):
        """プラン開始日が月末の場合（1月31日）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 31, 10, 0, 0))
        now = jst.localize(datetime(2026, 2, 15, 15, 30, 0))  # プラン開始から15日後
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2026-01-31 10:00:00 〜 2026-02-28 09:59:59（2月は28日まで）
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-31 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-28 09:59:59'
    
    def test_billing_period_month_end_leap_year(self):
        """プラン開始日が月末の場合（うるう年の2月29日）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2024, 2, 29, 10, 0, 0))  # うるう年
        now = jst.localize(datetime(2024, 3, 15, 15, 30, 0))  # プラン開始から15日後
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 1回目の請求期間: 2024-02-29 10:00:00 〜 2024-03-29 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2024-02-29 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2024-03-29 09:59:59'
    
    def test_billing_period_error_before_start(self):
        """エラーハンドリング: 現在時刻がプラン開始日より前の場合"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 1, 14, 10, 0, 0))  # プラン開始日の前日
        
        with pytest.raises(ValueError) as exc_info:
            calculate_billing_period(plan_start, now)
        
        assert "Current time" in str(exc_info.value)
        assert "before plan start time" in str(exc_info.value)
    
    def test_billing_period_naive_datetime(self):
        """naive datetimeの処理（JSTとして扱う）"""
        plan_start = datetime(2026, 1, 15, 10, 0, 0)  # naive datetime
        now = datetime(2026, 1, 20, 15, 30, 0)  # naive datetime
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # JSTとして扱われる
        jst = pytz.timezone('Asia/Tokyo')
        assert billing_start.tzinfo == jst
        assert billing_end.tzinfo == jst
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
    
    def test_billing_period_utc_to_jst(self):
        """UTCからJSTへの変換"""
        utc = pytz.UTC
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = utc.localize(datetime(2026, 1, 15, 1, 0, 0))  # UTC 2026-01-15 01:00:00 = JST 2026-01-15 10:00:00
        now = utc.localize(datetime(2026, 1, 20, 6, 30, 0))  # UTC 2026-01-20 06:30:00 = JST 2026-01-20 15:30:00
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # JSTに変換される
        assert billing_start.tzinfo == jst
        assert billing_end.tzinfo == jst
        # JST基準で請求期間が計算される
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-01-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-02-15 09:59:59'
    
    def test_billing_period_multiple_cycles(self):
        """複数の請求期間にまたがるテスト（3回目の請求期間）"""
        jst = pytz.timezone('Asia/Tokyo')
        plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        now = jst.localize(datetime(2026, 4, 15, 10, 0, 0))  # プラン開始から3ヶ月後（3回目の請求期間の開始時刻）
        
        billing_start, billing_end = calculate_billing_period(plan_start, now)
        
        # 3回目の請求期間: 2026-04-15 10:00:00 〜 2026-05-15 09:59:59
        assert billing_start.strftime('%Y-%m-%d %H:%M:%S') == '2026-04-15 10:00:00'
        assert billing_end.strftime('%Y-%m-%d %H:%M:%S') == '2026-05-15 09:59:59'

