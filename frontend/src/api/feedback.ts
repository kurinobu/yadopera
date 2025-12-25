/**
 * フィードバックAPI
 */

import apiClient from './axios'
import type { LowRatedAnswer } from '@/types/faq'

interface FeedbackApi {
  /**
   * 低評価回答リスト取得（2回以上低評価がついた回答）
   */
  getNegativeFeedbacks(): Promise<LowRatedAnswer[]>
  
  /**
   * 低評価回答を無視
   */
  ignoreNegativeFeedback(messageId: number): Promise<void>
}

export const feedbackApi: FeedbackApi = {
  /**
   * 低評価回答リスト取得（2回以上低評価がついた回答）
   */
  async getNegativeFeedbacks(): Promise<LowRatedAnswer[]> {
    const response = await apiClient.get<LowRatedAnswer[]>('/admin/feedback/negative')
    return response.data
  },

  /**
   * 低評価回答を無視
   */
  async ignoreNegativeFeedback(messageId: number): Promise<void> {
    await apiClient.post(`/admin/feedback/${messageId}/ignore`)
  }
}


