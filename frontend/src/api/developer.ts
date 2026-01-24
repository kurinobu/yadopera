/**
 * 開発者管理ページAPI
 */

import apiClient from './axios'
import { isDeveloperTokenExpired, logoutDeveloper } from '@/utils/developerAuth'
import type {
  SystemOverview,
  FacilitySummary,
  ErrorLogDetail,
  ErrorLogListResponse,
  SystemHealthResponse
} from '@/types/developer'

const DEVELOPER_API_BASE = '/developer'

// 開発者用のAPIクライアント（認証トークンを手動で設定）
const getDeveloperApiClient = () => {
  try {
    // ブラウザ環境でない場合はエラー
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
      throw new Error('API client not available in non-browser environment')
    }

    const token = localStorage.getItem('developer_token')
    if (!token) {
      throw new Error('Developer token not found')
    }
    
    // トークンの有効期限をチェック
    if (isDeveloperTokenExpired()) {
      console.warn('Developer token expired during API call')
      logoutDeveloper()
      throw new Error('Developer token expired')
    }
    
    // 既存のapiClientを使用し、Authorizationヘッダーを追加
    const config = {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
    
    return {
      get: (url: string, options?: any) => apiClient.get(`${DEVELOPER_API_BASE}${url}`, { ...config, ...options }),
      post: (url: string, data?: any, options?: any) => apiClient.post(`${DEVELOPER_API_BASE}${url}`, data, { ...config, ...options }),
      put: (url: string, data?: any, options?: any) => apiClient.put(`${DEVELOPER_API_BASE}${url}`, data, { ...config, ...options }),
      delete: (url: string, options?: any) => apiClient.delete(`${DEVELOPER_API_BASE}${url}`, { ...config, ...options })
    }
  } catch (error) {
    console.error('Error creating developer API client:', error)
    throw error
  }
}

export const developerApi = {
  /**
   * 開発者ログイン
   */
  async login(password: string): Promise<{ access_token: string; token_type: string; expires_in: number }> {
    const response = await apiClient.post(`${DEVELOPER_API_BASE}/auth/login`, { password })
    return response.data
  },

  /**
   * システム全体概要取得
   */
  async getOverview(): Promise<SystemOverview> {
    const client = getDeveloperApiClient()
    const response = await client.get('/stats/overview')
    return response.data
  },

  /**
   * 施設一覧と基本統計取得
   */
  async getFacilities(): Promise<{ facilities: FacilitySummary[] }> {
    const client = getDeveloperApiClient()
    const response = await client.get('/stats/facilities')
    return response.data
  },

  /**
   * エラーログ一覧取得
   */
  async getErrors(params: {
    page?: number
    per_page?: number
    level?: string
    facility_id?: number
    start_date?: string
    end_date?: string
  }): Promise<ErrorLogListResponse> {
    const client = getDeveloperApiClient()
    const response = await client.get('/errors/list', { params })
    return response.data
  },

  /**
   * エラーログ詳細取得
   */
  async getErrorDetail(errorId: number): Promise<ErrorLogDetail> {
    const client = getDeveloperApiClient()
    const response = await client.get(`/errors/${errorId}`)
    return response.data
  },

  /**
   * システムヘルスチェック
   */
  async getSystemHealth(): Promise<SystemHealthResponse> {
    const client = getDeveloperApiClient()
    const response = await client.get('/health/system')
    return response.data
  }
}

