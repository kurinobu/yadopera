"""
キャッシュユーティリティ
Redisキャッシュのヘルパー関数
"""

import json
import logging
from typing import Optional, Any, List
from redis.asyncio import Redis
from app.redis_client import redis_client
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# デフォルトTTL（秒）
DEFAULT_TTL = 3600  # 1時間


async def get_cache(key: str) -> Optional[Any]:
    """
    キャッシュから値を取得
    
    Args:
        key: キャッシュキー
    
    Returns:
        キャッシュされた値、見つからない場合はNone
    """
    try:
        if not redis_client:
            return None
        
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache get error for key {key}: {e}")
        return None


async def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """
    キャッシュに値を設定
    
    Args:
        key: キャッシュキー
        value: キャッシュする値（JSONシリアライズ可能なオブジェクト）
        ttl: 有効期限（秒）
    
    Returns:
        成功した場合はTrue
    """
    try:
        if not redis_client:
            return False
        
        await redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)  # datetime等を文字列に変換
        )
        return True
    except Exception as e:
        logger.warning(f"Cache set error for key {key}: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """
    キャッシュを削除
    
    Args:
        key: キャッシュキー
    
    Returns:
        成功した場合はTrue
    """
    try:
        if not redis_client:
            return False
        
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error for key {key}: {e}")
        return False


async def delete_cache_pattern(pattern: str) -> int:
    """
    パターンに一致するキャッシュを削除
    
    Args:
        pattern: キャッシュキーパターン（例: "faq:*"）
    
    Returns:
        削除されたキーの数
    """
    try:
        if not redis_client:
            return 0
        
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await redis_client.delete(*keys)
        
        return len(keys)
    except Exception as e:
        logger.warning(f"Cache delete pattern error for pattern {pattern}: {e}")
        return 0


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    キャッシュキーを生成
    
    Args:
        prefix: キープレフィックス
        *args: 位置引数
        **kwargs: キーワード引数
    
    Returns:
        キャッシュキー文字列
    """
    # 引数をハッシュ化してキーに含める
    key_parts = [prefix]
    
    if args:
        key_parts.append(":".join(str(arg) for arg in args))
    
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(":".join(f"{k}={v}" for k, v in sorted_kwargs))
    
    key_string = ":".join(key_parts)
    
    # 長すぎる場合はハッシュ化
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cached(ttl: int = DEFAULT_TTL, key_prefix: str = "cache"):
    """
    関数の結果をキャッシュするデコレータ
    
    Args:
        ttl: キャッシュ有効期限（秒）
        key_prefix: キャッシュキープレフィックス
    
    Usage:
        @cached(ttl=3600, key_prefix="faq")
        async def get_faqs(facility_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # キャッシュキー生成
            cache_key_str = cache_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # キャッシュから取得を試みる
            cached_value = await get_cache(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key_str}")
                return cached_value
            
            # キャッシュミス: 関数を実行
            logger.debug(f"Cache miss: {cache_key_str}")
            result = await func(*args, **kwargs)
            
            # 結果をキャッシュ
            await set_cache(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator


