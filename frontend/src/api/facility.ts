/**
 * 施設情報API
 */

import apiClient from './axios'
import type {
  FacilityPublicResponse,
  FacilitySettingsResponse,
  FacilitySettingsUpdateRequest
} from '@/types/facility'

export const facilityApi = {
  /**
   * 施設情報取得（公開）
   */
  async getFacility(slug: string, location?: string, language?: string): Promise<FacilityPublicResponse> {
    const params: Record<string, string> = {}
    if (location) params.location = location
    if (language) params.language = language
    const response = await apiClient.get<FacilityPublicResponse>(`/facility/${slug}`, { params })
    return response.data
  },

  /**
   * 施設設定取得（管理画面用）
   */
  async getFacilitySettings(): Promise<FacilitySettingsResponse> {
    const response = await apiClient.get<FacilitySettingsResponse>('/admin/facility/settings')
    return response.data
  },

  /**
   * 施設設定更新（管理画面用）
   */
  async updateFacilitySettings(data: FacilitySettingsUpdateRequest): Promise<FacilitySettingsResponse> {
    const response = await apiClient.put<FacilitySettingsResponse>('/admin/facility/settings', data)
    return response.data
  }
}


