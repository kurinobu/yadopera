/**
 * セッション統合トークンAPI
 */

import apiClient from './axios'
import type { SessionLinkRequest, SessionLinkResponse, SessionTokenVerifyResponse, SessionTokenGenerateRequest, SessionTokenResponse } from '@/types/session'

export const sessionApi = {
  /**
   * セッション統合
   */
  async linkSession(data: SessionLinkRequest): Promise<SessionLinkResponse> {
    const response = await apiClient.post<SessionLinkResponse>('/session/link', data)
    return response.data
  },

  /**
   * トークン検証
   */
  async verifyToken(token: string): Promise<SessionTokenVerifyResponse> {
    const response = await apiClient.get<SessionTokenVerifyResponse>(`/session/token/${token}`)
    return response.data
  },

  /**
   * トークン生成
   */
  async generateToken(data: SessionTokenGenerateRequest): Promise<SessionTokenResponse> {
    const response = await apiClient.post<SessionTokenResponse>('/session/generate', data)
    return response.data
  },

  /**
   * セッションIDから既存のトークンを取得
   */
  async getTokenBySessionId(sessionId: string): Promise<SessionTokenResponse> {
    const response = await apiClient.get<SessionTokenResponse>(`/session/session/${sessionId}/token`)
    return response.data
  }
}

