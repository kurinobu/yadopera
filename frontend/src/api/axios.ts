/**
 * Axios設定
 * リクエスト/レスポンスインターセプターでJWTトークン追加とエラーハンドリング
 */

import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { handleApiError } from '@/utils/errorHandler'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Axiosインスタンス作成
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // 30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// リトライ設定
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1秒

// リクエストインターセプター: JWTトークン追加
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    const token = authStore.token

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター: エラーハンドリング
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()

    if (error.response) {
      const { status } = error.response

      // 401 Unauthorized: トークン無効または期限切れ
      if (status === 401) {
        authStore.logout()
        // TODO: ログイン画面にリダイレクト（Week 4で実装）
      }

      // エラーを処理して返す
      const appError = handleApiError(error)
      return Promise.reject(appError)
    }

    // ネットワークエラーやタイムアウト
    if (error.request) {
      // タイムアウトエラーの判定
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        return Promise.reject({
          code: 'TIMEOUT_ERROR',
          message: 'リクエストがタイムアウトしました。接続を確認して再度お試しください。'
        })
      }
      
      // ネットワークエラー
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'ネットワークエラーが発生しました。接続を確認してください。',
        details: {
          url: error.config?.url,
          method: error.config?.method
        }
      })
    }

    // その他のエラー
    return Promise.reject(handleApiError(error))
  }
)

export default apiClient

