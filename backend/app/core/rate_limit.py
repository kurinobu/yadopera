"""
APIレート制限
"""

from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# メモリベースの簡易レート制限（本番ではRedis推奨）
_resend_attempts: Dict[str, datetime] = {}


def check_resend_rate_limit(email: str, cooldown_seconds: int = 60):
    """
    メール再送信のレート制限チェック
    
    Args:
        email: メールアドレス
        cooldown_seconds: クールダウン秒数（デフォルト60秒）
    
    Raises:
        HTTPException: レート制限超過時
    """
    now = datetime.utcnow()
    last_attempt = _resend_attempts.get(email)
    
    if last_attempt and (now - last_attempt).total_seconds() < cooldown_seconds:
        remaining = cooldown_seconds - int((now - last_attempt).total_seconds())
        logger.warning(
            f"Rate limit exceeded: email={email}, remaining={remaining}s"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {remaining} seconds before resending."
        )
    
    _resend_attempts[email] = now
    logger.info(f"Rate limit check passed: email={email}")


def cleanup_old_attempts(max_age_minutes: int = 60):
    """
    古いレート制限記録を削除（メモリ節約）
    
    Args:
        max_age_minutes: 削除対象の経過時間（分）
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=max_age_minutes)
    
    old_keys = [
        email for email, timestamp in _resend_attempts.items()
        if timestamp < cutoff
    ]
    
    for email in old_keys:
        del _resend_attempts[email]
    
    if old_keys:
        logger.info(f"Cleaned up {len(old_keys)} old rate limit records")

