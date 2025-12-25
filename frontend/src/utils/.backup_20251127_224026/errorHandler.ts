/**
 * エラーハンドリング関数
 */

import { useRouter } from 'vue-router'
import type { AxiosError } from 'axios'

export interface AppError {
  code: string
  message: string
  details?: Record<string, any>
}

/**
 * APIエラーを処理
 */
export function handleApiError(error: unknown): AppError {
  if (isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: AppError }>
    
    // バックエンドからのエラーレスポンス
    if (axiosError.response?.data?.error) {
      return axiosError.response.data.error
    }
    
    // HTTPステータスコードに基づくエラーメッセージ
    const status = axiosError.response?.status
    switch (status) {
      case 400:
        return {
          code: 'BAD_REQUEST',
          message: 'リクエストが不正です。入力内容を確認してください。'
        }
      case 401:
        return {
          code: 'UNAUTHORIZED',
          message: '認証が必要です。ログインしてください。'
        }
      case 403:
        return {
          code: 'FORBIDDEN',
          message: 'この操作を実行する権限がありません。'
        }
      case 404:
        return {
          code: 'NOT_FOUND',
          message: 'リソースが見つかりません。'
        }
      case 429:
        return {
          code: 'RATE_LIMIT',
          message: 'リクエストが多すぎます。しばらく時間をおいてから再度お試しください。'
        }
      case 500:
        return {
          code: 'SERVER_ERROR',
          message: 'サーバーでエラーが発生しました。しばらく時間をおいてから再度お試しください。'
        }
      default:
        return {
          code: 'UNKNOWN_ERROR',
          message: 'エラーが発生しました。しばらく時間をおいてから再度お試しください。'
        }
    }
  }
  
  // その他のエラー
  if (error instanceof Error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'エラーが発生しました。'
    }
  }
  
  return {
    code: 'UNKNOWN_ERROR',
    message: '予期しないエラーが発生しました。'
  }
}

/**
 * エラーメッセージを表示
 */
export function showErrorMessage(error: AppError | string): void {
  const message = typeof error === 'string' ? error : error.message
  
  // モック: 実際の実装ではトースト通知ライブラリを使用
  // 例: vue-toastification, vue-toast-notification など
  alert(message)
}

/**
 * エラーページにリダイレクト
 */
export function redirectToErrorPage(error: AppError, router: ReturnType<typeof useRouter>): void {
  switch (error.code) {
    case 'NOT_FOUND':
      router.push({ name: 'NotFound' })
      break
    case 'SERVER_ERROR':
      router.push({ name: 'Error500' })
      break
    case 'UNAUTHORIZED':
      router.push({ name: 'AdminLogin', query: { redirect: router.currentRoute.value.fullPath } })
      break
    default:
      // その他のエラーは現在のページに留まる
      break
  }
}

/**
 * Axiosエラーかどうかを判定
 */
function isAxiosError(error: unknown): error is AxiosError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'isAxiosError' in error &&
    (error as any).isAxiosError === true
  )
}

