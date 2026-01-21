"""
請求期間計算ユーティリティ
契約開始日から現在時刻が含まれる請求期間を計算する
"""

from datetime import datetime, timedelta
from typing import Tuple
import pytz
import logging
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def calculate_billing_period(
    plan_started_at: datetime,
    now: datetime = None
) -> Tuple[datetime, datetime]:
    """
    契約開始日から現在時刻が含まれる請求期間を計算
    
    請求期間は契約開始日（plan_started_at）から30日間（1ヶ月）ごとに区切られます。
    現在時刻が含まれる請求期間の開始時刻と終了時刻を返します。
    
    Args:
        plan_started_at: プラン開始日時（timezone-awareまたはnaive）
        now: 現在時刻（timezone-aware、デフォルト: 現在時刻JST）
    
    Returns:
        Tuple[datetime, datetime]: (請求期間開始時刻, 請求期間終了時刻)（timezone-aware、JST）
    
    Raises:
        ValueError: 現在時刻がプラン開始日より前の場合
    
    Examples:
        >>> import pytz
        >>> jst = pytz.timezone('Asia/Tokyo')
        >>> plan_start = jst.localize(datetime(2026, 1, 15, 10, 0, 0))
        >>> billing_start, billing_end = calculate_billing_period(plan_start)
        >>> # 1回目の請求期間: 2026-01-15 10:00:00 〜 2026-02-15 09:59:59（JST）
        
        >>> # プラン開始日から31日後（2回目の請求期間）
        >>> now = jst.localize(datetime(2026, 2, 16, 10, 0, 0))
        >>> billing_start, billing_end = calculate_billing_period(plan_start, now)
        >>> # 2回目の請求期間: 2026-02-15 10:00:00 〜 2026-03-15 09:59:59（JST）
    """
    # 現在時刻が指定されていない場合はJSTの現在時刻を使用
    if now is None:
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)
    
    # plan_started_atがnaiveの場合はJSTとして扱う
    if plan_started_at.tzinfo is None:
        jst = pytz.timezone('Asia/Tokyo')
        plan_started_at = jst.localize(plan_started_at)
        logger.warning(
            f"plan_started_at is naive datetime, treating as JST: {plan_started_at}"
        )
    else:
        # timezone-awareの場合はJSTに変換
        jst = pytz.timezone('Asia/Tokyo')
        plan_started_at = plan_started_at.astimezone(jst)
    
    # nowもJSTに変換（念のため）
    if now.tzinfo is None:
        now = jst.localize(now)
        logger.warning(f"now is naive datetime, treating as JST: {now}")
    else:
        now = now.astimezone(jst)
    
    # 現在時刻がプラン開始日より前の場合はエラー
    if now < plan_started_at:
        raise ValueError(
            f"Current time ({now}) is before plan start time ({plan_started_at})"
        )
    
    # プラン開始日からの経過日数を計算
    elapsed = now - plan_started_at
    elapsed_days = elapsed.days
    
    # 何回目の請求期間かを計算（0回目、1回目、2回目...）
    # 請求期間は1ヶ月（約30-31日）ごとに区切られる
    # 経過日数から請求期間の回数を計算
    # 例: 経過日数が0-30日 → 0回目、31-61日 → 1回目、62-92日 → 2回目
    # 注意: 1ヶ月は28-31日と変動するため、経過日数を30で割るのではなく、
    # プラン開始日から何ヶ月経過したかを計算する
    months_elapsed = (now.year - plan_started_at.year) * 12 + (now.month - plan_started_at.month)
    
    # 同じ月内で、日付が開始日より前の場合は1ヶ月減らす
    if now.day < plan_started_at.day or (now.day == plan_started_at.day and now.hour < plan_started_at.hour):
        months_elapsed -= 1
    
    # 現在の請求期間の開始時刻を計算（プラン開始日からNヶ月後）
    # 例: plan_started_at = 2026-01-15 10:00:00、months_elapsed = 0 → 2026-01-15 10:00:00
    #     plan_started_at = 2026-01-15 10:00:00、months_elapsed = 1 → 2026-02-15 10:00:00
    billing_start = plan_started_at + relativedelta(months=months_elapsed)
    
    # 現在の請求期間の終了時刻を計算（開始時刻 + 1ヶ月 - 1秒）
    # 例: billing_start = 2026-01-15 10:00:00 → 2026-02-15 09:59:59
    billing_end = billing_start + relativedelta(months=1) - timedelta(seconds=1)
    
    logger.debug(
        f"Billing period calculated: "
        f"plan_started_at={plan_started_at}, "
        f"now={now}, "
        f"months_elapsed={months_elapsed}, "
        f"billing_start={billing_start}, "
        f"billing_end={billing_end}"
    )
    
    return billing_start, billing_end

