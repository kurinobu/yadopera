from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # OpenAI
    openai_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    
    # App
    environment: str = "development"
    debug: bool = True
    
    # Frontend URL (QRコード生成用)
    frontend_url: str = "https://yadopera.com"  # デフォルトは本番環境用
    
    # CORS (comma-separated string to List[str])
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Developer Management Page (Phase 2)
    developer_password: str = ""  # 開発者ログインパスワード（環境変数から取得）
    developer_session_expire_hours: int = 24  # セッション有効期限（時間）
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS originsをリストに変換"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 環境変数から設定を読み込む
settings = Settings()

