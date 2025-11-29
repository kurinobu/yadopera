/**
 * FAQ管理API
 */

import apiClient from './axios'
import type { FAQ, FAQCreate, FAQUpdate } from '@/types/faq'

export const faqApi = {
  /**
   * FAQ一覧取得
   */
  async getFaqs(category?: string, isActive?: boolean): Promise<FAQ[]> {
    const params: Record<string, any> = {}
    if (category) params.category = category
    if (isActive !== undefined) params.is_active = isActive
    
    const response = await apiClient.get<{ faqs: FAQ[]; total: number }>('/admin/faqs', { params })
    return response.data.faqs
  },

  /**
   * FAQ作成
   */
  async createFaq(data: FAQCreate): Promise<FAQ> {
    const response = await apiClient.post<FAQ>('/admin/faqs', data)
    return response.data
  },

  /**
   * FAQ更新
   */
  async updateFaq(faqId: number, data: FAQUpdate): Promise<FAQ> {
    const response = await apiClient.put<FAQ>(`/admin/faqs/${faqId}`, data)
    return response.data
  },

  /**
   * FAQ削除
   */
  async deleteFaq(faqId: number): Promise<void> {
    await apiClient.delete(`/admin/faqs/${faqId}`)
  }
}

