/**
 * 施設情報API
 */

import apiClient from './axios'
import type { FacilityPublicResponse } from '@/types/facility'

export const facilityApi = {
  /**
   * 施設情報取得（公開）
   */
  async getFacility(slug: string, location?: string): Promise<FacilityPublicResponse> {
    const params = location ? { location } : {}
    const response = await apiClient.get<FacilityPublicResponse>(`/facility/${slug}`, { params })
    return response.data
  }
}

