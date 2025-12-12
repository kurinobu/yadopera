/**
 * FAQ提案API
 */

import apiClient from './axios'
import type { FaqSuggestion, FAQCategory } from '@/types/faq'

export interface ApproveSuggestionRequest {
  question?: string
  answer?: string
  category?: FAQCategory
  priority?: number
}

export const faqSuggestionApi = {
  /**
   * FAQ提案一覧取得
   */
  async getSuggestions(status?: string): Promise<FaqSuggestion[]> {
    const params: Record<string, any> = {}
    if (status) params.status = status
    
    const response = await apiClient.get<{ suggestions: FaqSuggestion[]; total: number }>('/admin/faq-suggestions', { params })
    return response.data.suggestions
  },

  /**
   * FAQ提案生成（GPT-4o mini）
   */
  async generateSuggestion(messageId: number): Promise<FaqSuggestion> {
    const response = await apiClient.post<FaqSuggestion>(`/admin/faq-suggestions/generate/${messageId}`)
    return response.data
  },

  /**
   * 提案承認（FAQ作成）
   */
  async approveSuggestion(suggestionId: number, data: ApproveSuggestionRequest): Promise<FaqSuggestion> {
    const response = await apiClient.post<FaqSuggestion>(`/admin/faq-suggestions/${suggestionId}/approve`, data)
    return response.data
  },

  /**
   * 提案却下
   */
  async rejectSuggestion(suggestionId: number): Promise<FaqSuggestion> {
    const response = await apiClient.post<FaqSuggestion>(`/admin/faq-suggestions/${suggestionId}/reject`)
    return response.data
  }
}


