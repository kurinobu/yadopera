/**
 * フィードバックAPI
 */

import apiClient from './axios'
import type { LowRatedAnswer } from '@/types/faq'

export const feedbackApi = {
  /**
   * 低評価回答リスト取得（2回以上低評価がついた回答）
   */
  async getNegativeFeedbacks(): Promise<LowRatedAnswer[]> {
    const response = await apiClient.get<LowRatedAnswer[]>('/admin/feedback/negative')
    return response.data
  }
}


