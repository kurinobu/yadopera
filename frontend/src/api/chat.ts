/**
 * チャットAPI
 */

import apiClient from './axios'
import type { ChatRequest, ChatResponse, ChatHistoryResponse, FeedbackRequest, FeedbackResponse } from '@/types/chat'

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
  },

  /**
   * ゲストフィードバック送信（v0.3新規）
   */
  async sendFeedback(data: FeedbackRequest): Promise<FeedbackResponse> {
    const response = await apiClient.post<FeedbackResponse>('/chat/feedback', data)
    return response.data
  }
}

