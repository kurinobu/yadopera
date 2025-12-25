/**
 * チャットAPI
 */

import apiClient from './axios'
import type { ChatRequest, ChatResponse, ChatHistoryResponse } from '@/types/chat'

export const chatApi = {
  /**
   * チャットメッセージ送信
   */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/chat', data)
    return response.data
  },

  /**
   * 会話履歴取得
   */
  async getHistory(sessionId: string, facilityId?: number): Promise<ChatHistoryResponse> {
    const params = facilityId ? { facility_id: facilityId } : {}
    const response = await apiClient.get<ChatHistoryResponse>(`/chat/history/${sessionId}`, { params })
    return response.data
  }
}

