"""
セキュリティ関連ユーティリティ
パスワードハッシュ化・検証
"""

from passlib.context import CryptContext
from passlib.hash import bcrypt

# bcryptコンテキスト作成（ラウンド数12）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """
    パスワードハッシュ化（bcrypt）
    
    Args:
        password: 平文パスワード
        
    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワード検証
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード
        
    Returns:
        検証結果（True: 一致、False: 不一致）
    """
    # bcryptは72バイトを超えるパスワードを処理できないため、72バイトに切り詰める
    # パスワードをUTF-8エンコードしてバイト数で判定
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # 72バイトに切り詰める（bcryptの仕様に準拠）
        truncated_password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(truncated_password, hashed_password)
    
    return pwd_context.verify(plain_password, hashed_password)

