/**
 * 認証API
 */

import apiClient from './axios'
import type { LoginRequest, LoginResponse } from '@/types/auth'

export const authApi = {
  /**
   * ログイン
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  /**
   * ログアウト
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  }
}

