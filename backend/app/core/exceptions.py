"""
カスタム例外クラス定義
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """
    アプリケーション基底例外
    """
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """
    バリデーション例外
    """
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details or {}
        )


class AuthenticationException(AppException):
    """
    認証例外
    """
    def __init__(
        self,
        message: str = "Invalid authentication credentials",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            details=details or {}
        )


class NotFoundException(AppException):
    """
    リソース未検出例外
    """
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            details=details or {}
        )


class DatabaseException(AppException):
    """
    データベース例外
    """
    def __init__(
        self,
        message: str = "Database error occurred",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details or {}
        )


class ServiceUnavailableException(AppException):
    """
    サービス利用不可例外
    """
    def __init__(
        self,
        message: str = "Service is temporarily unavailable",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if service:
            details["service"] = service
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            details=details
        )


class AIException(AppException):
    """
    AI処理例外（v0.2追加）
    OpenAI API関連エラー
    """
    def __init__(
        self,
        message: str = "AI processing error occurred",
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if error_type:
            details["error_type"] = error_type
        super().__init__(
            message=message,
            code="AI_ERROR",
            details=details
        )
        self.error_type = error_type


class VectorSearchException(AppException):
    """
    pgvector検索例外（v0.2追加）
    """
    def __init__(
        self,
        message: str = "Vector search error occurred",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="VECTOR_SEARCH_ERROR",
            details=details or {}
        )


class EscalationException(AppException):
    """
    エスカレーション処理例外（v0.2追加）
    """
    def __init__(
        self,
        message: str = "Escalation processing error occurred",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="ESCALATION_ERROR",
            details=details or {}
        )

