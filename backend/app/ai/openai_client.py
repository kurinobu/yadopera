"""
OpenAI API クライアント
"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime
from openai import OpenAI, OpenAIError, APITimeoutError, RateLimitError, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from app.core.config import settings
from app.ai.fallback import get_fallback_message

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    OpenAI APIクライアント（v0.3詳細化）
    - GPT-4o mini: 回答生成
    - text-embedding-3-small: 埋め込み生成
    - エラーハンドリング（タイムアウト、レート制限、API障害）
    - フォールバックメッセージ（多言語対応）
    """
    
    # タイムアウト設定（秒）
    TIMEOUT = 10.0
    
    def __init__(self):
        """
        OpenAIクライアント初期化
        """
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_chat = "gpt-4o-mini-2024-07-18"
        self.model_embedding = "text-embedding-3-small"
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(min=1, max=120),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.7,
        language: str = "en"
    ) -> str:
        """
        AI応答生成（リトライロジック付き、v0.3詳細化）
        - GPT-4o miniを使用
        - レート制限エラー時に自動リトライ（最大5回）
        - 指数バックオフアルゴリズムを使用（1秒～120秒、ランダム要素付き）
        - ゲストの選択言語に応じたフォールバックメッセージ返却
        
        Args:
            prompt: プロンプト
            max_tokens: 最大トークン数（デフォルト: 200）
            temperature: 温度パラメータ（デフォルト: 0.7）
            language: 言語コード（フォールバックメッセージ用）
        
        Returns:
            AI生成回答、またはフォールバックメッセージ
        """
        try:
            # OpenAI APIは同期なので、asyncio.to_threadで非同期実行
            # asyncio.wait_forでタイムアウトを実装
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model_chat,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=self.TIMEOUT
            )
            return response.choices[0].message.content
        
        except asyncio.TimeoutError as e:
            # asyncio.wait_forによるタイムアウト
            logger.error(
                "OpenAI API timeout (asyncio)",
                extra={
                    "error_type": "OpenAI_API_timeout",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
        
        except APITimeoutError as e:
            # OpenAI SDKのタイムアウトエラー
            logger.error(
                "OpenAI API timeout",
                extra={
                    "error_type": "OpenAI_API_timeout",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
        
        except RateLimitError as e:
            # レート制限エラー（リトライ後も失敗した場合）
            logger.error(
                "OpenAI API rate limit (max retries reached)",
                extra={
                    "error_type": "OpenAI_API_rate_limit",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
        
        except APIError as e:
            # APIエラー（サーバーエラー等）
            logger.error(
                "OpenAI API error",
                exc_info=True,
                extra={
                    "error_type": "OpenAI_API_server_error",
                    "error_message": str(e),
                    "error_code": getattr(e, 'code', None),
                    "error_status": getattr(e, 'status_code', None),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
        
        except OpenAIError as e:
            # その他のOpenAIエラー
            logger.error(
                "OpenAI API error",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "error_code": getattr(e, 'code', None),
                    "error_status": getattr(e, 'status_code', None),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
        
        except Exception as e:
            # 予期しないエラー
            logger.critical(
                f"Unexpected error in AI generation: {e}",
                exc_info=True,
                extra={
                    "error_type": "UnexpectedError",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return get_fallback_message(language)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(min=1, max=120),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def generate_embedding(
        self,
        text: str
    ) -> List[float]:
        """
        埋め込みベクトル生成（リトライロジック付き、v0.3詳細化）
        - text-embedding-3-smallを使用
        - レート制限エラー時に自動リトライ（最大5回）
        - 指数バックオフアルゴリズムを使用（1秒～120秒、ランダム要素付き）
        - 出力: 1536次元ベクトル
        
        Args:
            text: 埋め込み生成対象のテキスト
        
        Returns:
            埋め込みベクトル（1536次元）、エラー時は空リスト
        """
        try:
            # OpenAI APIは同期なので、asyncio.to_threadで非同期実行
            # asyncio.wait_forでタイムアウトを実装
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.embeddings.create,
                    model=self.model_embedding,
                    input=text
                ),
                timeout=self.TIMEOUT
            )
            return response.data[0].embedding
        
        except asyncio.TimeoutError as e:
            # asyncio.wait_forによるタイムアウト
            logger.error(
                "OpenAI Embeddings API timeout (asyncio)",
                extra={
                    "error_type": "OpenAI_Embeddings_API_timeout",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []
        
        except APITimeoutError as e:
            # OpenAI SDKのタイムアウトエラー
            logger.error(
                "OpenAI Embeddings API timeout",
                extra={
                    "error_type": "OpenAI_Embeddings_API_timeout",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []
        
        except RateLimitError as e:
            # レート制限エラー（リトライ後も失敗した場合）
            logger.error(
                "OpenAI Embeddings API rate limit (max retries reached)",
                extra={
                    "error_type": "OpenAI_Embeddings_API_rate_limit",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []
        
        except APIError as e:
            # APIエラー（サーバーエラー等）
            logger.error(
                "OpenAI Embeddings API error",
                exc_info=True,
                extra={
                    "error_type": "OpenAI_Embeddings_API_server_error",
                    "error_message": str(e),
                    "error_code": getattr(e, 'code', None),
                    "error_status": getattr(e, 'status_code', None),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []
        
        except OpenAIError as e:
            # その他のOpenAIエラー
            logger.error(
                "OpenAI Embeddings API error",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "error_code": getattr(e, 'code', None),
                    "error_status": getattr(e, 'status_code', None),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []
        
        except Exception as e:
            # 予期しないエラー
            logger.critical(
                f"Unexpected error in embedding generation: {e}",
                exc_info=True,
                extra={
                    "error_type": "UnexpectedError",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return []

