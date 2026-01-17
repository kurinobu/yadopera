/**
 * チャットAPI
 */

import apiClient from './axios'
import type { 
  ChatRequest, ChatResponse, ChatHistoryResponse, 
  FeedbackRequest, FeedbackResponse,
  EscalationRequest, EscalationResponse
} from '@/types/chat'

export const chatApi = {
  /**
   * チャットメッセージ送信
   */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    // チャットAPI専用のタイムアウト設定（60秒）
    // AI応答生成、RAG処理、データベースクエリなど、処理時間が長くなる可能性があるため
    const response = await apiClient.post<ChatResponse>('/chat', data, {
      timeout: 60000 // 60秒
    })
    return response.data
  },

  /**
   * 会話履歴取得
   */
  async getHistory(sessionId: string, facilityId?: number): Promise<ChatHistoryResponse> {
    const params = facilityId ? { facility_id: facilityId } : {}
    // 履歴取得は比較的軽量だが、大量のメッセージがある場合は時間がかかる可能性があるため30秒
    const response = await apiClient.get<ChatHistoryResponse>(`/chat/history/${sessionId}`, {
      params,
      timeout: 30000 // 30秒
    })
    return response.data
  },

  /**
   * ゲストフィードバック送信（v0.3新規）
   */
  async sendFeedback(data: FeedbackRequest): Promise<FeedbackResponse> {
    const response = await apiClient.post<FeedbackResponse>('/chat/feedback', data)
    return response.data
  },

  /**
   * スタッフへのエスカレーション（ゲスト側、v0.3新規）
   */
  async escalateToStaff(data: EscalationRequest): Promise<EscalationResponse> {
    const response = await apiClient.post<EscalationResponse>('/chat/escalate', data)
    return response.data
  }
}

