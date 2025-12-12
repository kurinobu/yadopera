/**
 * 未解決質問API
 */

import apiClient from './axios'
import type { UnresolvedQuestion } from '@/types/faq'

export const unresolvedQuestionsApi = {
  /**
   * 未解決質問リスト取得
   */
  async getUnresolvedQuestions(): Promise<UnresolvedQuestion[]> {
    const response = await apiClient.get<UnresolvedQuestion[]>('/admin/escalations/unresolved-questions')
    return response.data
  }
}


