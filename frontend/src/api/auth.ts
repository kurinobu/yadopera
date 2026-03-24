/**
 * 認証API
 */

import apiClient from './axios'
import type {
  LoginRequest, RegisterRequest, LoginResponse, User,
  FacilityRegisterResponse, VerifyEmailRequest, VerifyEmailResponse,
  ResendVerificationRequest, ResendVerificationResponse,
  PasswordResetRequest, PasswordResetConfirmRequest, PasswordResetResponse
} from '@/types/auth'
import type { PasswordChangeRequest } from '@/types/facility'

export const authApi = {
  /**
   * ログイン
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data, {
      timeout: 60000
    })
    return response.data
  },

  /**
   * 施設登録
   */
  async register(data: RegisterRequest): Promise<FacilityRegisterResponse> {
    // 登録はDB確定＋Brevo送信などで数秒〜十数秒かかる。既定10秒だと本番でタイムアウトしやすい
    const response = await apiClient.post<FacilityRegisterResponse>('/auth/register', data, {
      timeout: 120000
    })
    return response.data
  },

  /**
   * メールアドレス確認
   */
  async verifyEmail(data: VerifyEmailRequest): Promise<VerifyEmailResponse> {
    const response = await apiClient.post<VerifyEmailResponse>('/auth/verify-email', data, {
      timeout: 60000
    })
    return response.data
  },

  /**
   * 確認メール再送信
   */
  async resendVerification(data: ResendVerificationRequest): Promise<ResendVerificationResponse> {
    const response = await apiClient.post<ResendVerificationResponse>(
      '/auth/resend-verification',
      data,
      { timeout: 60000 }
    )
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
   * 初回やることリストモーダルを表示済みとして記録する
   */
  async postOnboardingSeen(): Promise<{ ok: boolean }> {
    const response = await apiClient.post<{ ok: boolean }>('/auth/onboarding-seen')
    return response.data
  },

  /**
   * パスワード変更
   */
  async changePassword(data: PasswordChangeRequest): Promise<void> {
    await apiClient.put('/auth/password', data)
  },

  /**
   * パスワードリセット依頼
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<PasswordResetResponse> {
    const response = await apiClient.post<PasswordResetResponse>('/auth/password-reset', data)
    return response.data
  },

  /**
   * パスワードリセット確定
   */
  async confirmPasswordReset(data: PasswordResetConfirmRequest): Promise<PasswordResetResponse> {
    const response = await apiClient.post<PasswordResetResponse>('/auth/password-reset/confirm', data)
    return response.data
  }
}

