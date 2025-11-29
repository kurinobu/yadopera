/**
 * セッション統合トークンAPI
 */

import apiClient from './axios'
import type { SessionLinkRequest, SessionLinkResponse, SessionTokenVerifyResponse } from '@/types/session'

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
  }
}

