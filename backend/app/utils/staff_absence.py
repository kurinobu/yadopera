"""
スタッフ不在時間帯判定ユーティリティ
"""

from typing import List, Dict, Optional
from datetime import datetime, time, timedelta
import pytz


def is_in_staff_absence_period(
    current_time: datetime,
    current_weekday: str,
    staff_absence_periods: List[Dict]
) -> bool:
    """
    現在時刻がスタッフ不在時間帯に該当するか判定
    
    Args:
        current_time: 現在時刻（施設のタイムゾーン）
        current_weekday: 現在の曜日（'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'）
        staff_absence_periods: スタッフ不在時間帯のリスト
    
    Returns:
        bool: スタッフ不在時間帯に該当する場合True
    """
    if not staff_absence_periods:
        # 未設定の場合はFalseを返す（エスカレーションは直接スタッフに通知）
        return False
    
    for period in staff_absence_periods:
        # 曜日のチェック
        days_of_week = period.get("days_of_week", [])
        if days_of_week and current_weekday not in days_of_week:
            continue
        
        start_time_str = period.get("start_time")
        end_time_str = period.get("end_time")
        
        if not start_time_str or not end_time_str:
            continue
        
        try:
            # 時刻をパース
            start_hour, start_minute = map(int, start_time_str.split(":"))
            end_hour, end_minute = map(int, end_time_str.split(":"))
            
            start_time = time(start_hour, start_minute)
            end_time = time(end_hour, end_minute)
            current_time_only = current_time.time()
            
            # 日を跨ぐ時間帯の判定（例: 22:00-8:00）
            if start_time > end_time:
                # 日を跨ぐ場合
                if current_time_only >= start_time or current_time_only < end_time:
                    return True
            else:
                # 同日内の場合
                if start_time <= current_time_only < end_time:
                    return True
        except (ValueError, AttributeError):
            # パースエラーの場合はスキップ
            continue
    
    return False


def get_next_notification_time(
    current_time: datetime,
    current_weekday: str,
    staff_absence_periods: List[Dict]
) -> datetime:
    """
    次の通知時刻を計算
    
    Args:
        current_time: 現在時刻（施設のタイムゾーン）
        current_weekday: 現在の曜日（'mon', 'tue', ...）
        staff_absence_periods: スタッフ不在時間帯のリスト
    
    Returns:
        datetime: 次の通知時刻（施設のタイムゾーン）
    """
    # 現在のスタッフ不在時間帯を取得
    current_period = None
    for period in staff_absence_periods:
        days_of_week = period.get("days_of_week", [])
        if days_of_week and current_weekday not in days_of_week:
            continue
        
        start_time_str = period.get("start_time")
        end_time_str = period.get("end_time")
        
        if start_time_str and end_time_str:
            current_period = period
            break
    
    if not current_period:
        # デフォルト: 翌朝8:00（後方互換性のため）
        if current_time.hour < 8:
            # 0:00-8:00 → 当日8:00
            return current_time.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            # 8:00-23:59 → 翌日8:00
            return (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    end_time_str = current_period.get("end_time")
    if not end_time_str:
        # デフォルト: 翌朝8:00
        return (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    try:
        end_hour, end_minute = map(int, end_time_str.split(":"))
    except (ValueError, AttributeError):
        # パースエラーの場合はデフォルト
        return (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 日を跨ぐ時間帯の場合
    start_time_str = current_period.get("start_time")
    if start_time_str:
        try:
            start_hour, start_minute = map(int, start_time_str.split(":"))
            start_time = time(start_hour, start_minute)
            end_time = time(end_hour, end_minute)
            
            if start_time > end_time:
                # 日を跨ぐ場合（例: 22:00-8:00）
                if current_time.hour < end_hour or (current_time.hour == end_hour and current_time.minute < end_minute):
                    # 当日の終了時刻
                    return current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                else:
                    # 翌日の終了時刻
                    return (current_time + timedelta(days=1)).replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        except (ValueError, AttributeError):
            # パースエラーの場合はデフォルト
            pass
    
    # 同日内の場合
    if current_time.hour < end_hour or (current_time.hour == end_hour and current_time.minute < end_minute):
        # 当日の終了時刻
        return current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    else:
        # 翌日の終了時刻
        return (current_time + timedelta(days=1)).replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)


def format_staff_absence_periods_display(
    staff_absence_periods: List[Dict]
) -> str:
    """
    スタッフ不在時間帯を表示用の文字列にフォーマット
    
    Args:
        staff_absence_periods: スタッフ不在時間帯のリスト
    
    Returns:
        str: 表示用の文字列（例: "22:00-8:00"）
    """
    if not staff_absence_periods:
        return "22:00-8:00"  # デフォルト
    
    # 最初の時間帯を使用
    period = staff_absence_periods[0]
    start_time = period.get("start_time", "22:00")
    end_time = period.get("end_time", "8:00")
    
    return f"{start_time}-{end_time}"

