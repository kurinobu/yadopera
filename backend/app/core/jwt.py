"""
JWTトークン生成・検証
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークン生成
    
    Args:
        data: トークンに含めるデータ（例: {"sub": user_id, "email": email}）
        expires_delta: 有効期限（指定しない場合は設定値を使用）
        
    Returns:
        JWTトークン文字列
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWTトークンデコード
    
    Args:
        token: JWTトークン文字列
        
    Returns:
        デコードされたペイロード（失敗時はNone）
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> bool:
    """
    JWTトークン検証
    
    Args:
        token: JWTトークン文字列
        
    Returns:
        検証結果（True: 有効、False: 無効）
    """
    payload = decode_token(token)
    if payload is None:
        return False
    
    # 有効期限チェック（jwt.decode()が自動的にチェックするが、明示的に確認）
    exp = payload.get("exp")
    if exp is None:
        return False
    
    # expはUnixタイムスタンプ（秒単位）
    from datetime import timezone
    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
    if datetime.now(timezone.utc) > exp_datetime:
        return False
    
    return True

