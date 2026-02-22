/**
 * リード（クーポン取得）API（管理画面用）
 */

import apiClient from './axios'

export interface LeadItem {
  id: number
  facility_id: number
  guest_name: string | null
  email: string
  coupon_sent_at: string | null
  created_at: string
}

export interface LeadListResponse {
  leads: LeadItem[]
  total: number
}

export const leadsApi = {
  /**
   * リード一覧取得（自施設）
   */
  async getLeads(skip = 0, limit = 100): Promise<LeadListResponse> {
    const response = await apiClient.get<LeadListResponse>('/admin/leads', {
      params: { skip, limit }
    })
    return response.data
  },

  /**
   * リードCSVダウンロード（自施設）
   */
  async exportCsv(): Promise<Blob> {
    const response = await apiClient.get<Blob>('/admin/leads/export', {
      responseType: 'blob'
    })
    return response.data
  }
}
