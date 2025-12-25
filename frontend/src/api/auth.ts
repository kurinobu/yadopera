/**
 * 認証API
 */

import apiClient from './axios'
import type { LoginRequest, LoginResponse, User } from '@/types/auth'
import type { PasswordChangeRequest } from '@/types/facility'

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
  },

  /**
   * 現在のユーザー情報取得
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  /**
   * パスワード変更
   */
  async changePassword(data: PasswordChangeRequest): Promise<void> {
    await apiClient.put('/auth/password', data)
  }
}

