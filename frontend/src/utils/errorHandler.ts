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
    const responseData = axiosError.response?.data as { detail?: unknown } | undefined
    const detailMessage = typeof responseData?.detail === 'string' && responseData.detail.trim() !== ''
      ? responseData.detail
      : null
    switch (status) {
      case 400:
        return {
          code: 'BAD_REQUEST',
          message: detailMessage ?? 'リクエストが不正です。入力内容を確認してください。'
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
      case 502:
      case 503:
        return {
          code: 'SERVICE_UNAVAILABLE',
          message: 'サービスが一時的に利用できません。しばらく時間をおいてから再度お試しください。'
        }
      case 504:
        return {
          code: 'TIMEOUT_ERROR',
          message: 'リクエストがタイムアウトしました。再度お試しください。'
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
  
  // エラーログ記録
  logError(error)
  
  // モック: 実際の実装ではトースト通知ライブラリを使用
  // 例: vue-toastification, vue-toast-notification など
  // 開発環境ではconsole.error、本番環境ではトースト通知
  if (import.meta.env.DEV) {
    console.error('Error:', error)
  }
  
  // ユーザー向けメッセージ表示
  alert(message)
}

/**
 * エラーログ記録
 */
export function logError(error: AppError | string | unknown): void {
  const errorData: AppError = typeof error === 'string'
    ? { code: 'UNKNOWN_ERROR', message: error }
    : isAppError(error)
    ? error
    : { code: 'UNKNOWN_ERROR', message: '予期しないエラーが発生しました。' }
  
  // エラーログを記録（開発環境のみ）
  if (import.meta.env.DEV) {
    console.error('Error logged:', {
      code: errorData.code,
      message: errorData.message,
      details: errorData.details,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    })
  }
  
  // TODO: Week 4でエラートラッキングサービス（Sentry等）に送信
  // if (import.meta.env.PROD) {
  //   // Sentry.captureException(error)
  // }
}

/**
 * AppErrorかどうかを判定
 */
function isAppError(error: unknown): error is AppError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error &&
    typeof (error as AppError).code === 'string' &&
    typeof (error as AppError).message === 'string'
  )
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

/**
 * グローバルエラーハンドラー（Vueアプリケーション全体）
 */
export function setupGlobalErrorHandler(router: ReturnType<typeof useRouter>): void {
  // 未処理のPromise拒否をキャッチ
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
    const error = handleApiError(event.reason)
    logError(error)
    
    // 重大なエラーの場合はエラーページにリダイレクト
    if (error.code === 'SERVER_ERROR' || error.code === 'NETWORK_ERROR') {
      redirectToErrorPage(error, router)
    } else {
      showErrorMessage(error)
    }
    
    // デフォルトのエラー処理を防ぐ
    event.preventDefault()
  })
  
  // 未処理のエラーをキャッチ
  window.addEventListener('error', (event: ErrorEvent) => {
    const error: AppError = {
      code: 'JAVASCRIPT_ERROR',
      message: event.message || 'JavaScriptエラーが発生しました。',
      details: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      }
    }
    
    logError(error)
    
    // 開発環境では詳細を表示
    if (import.meta.env.DEV) {
      console.error('Global error:', event)
    }
  })
}

