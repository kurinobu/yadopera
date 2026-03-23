/**
 * 広告API（Freeプラン ゲスト画面固定フッター用）
 * 施設が Free のときのみ広告一覧を返す。
 */

import apiClient from './axios'

export interface AdItem {
  id: number
  title: string
  description?: string | null
  url?: string | null
  affiliate_url: string
  priority: number
}

export interface AdListResponse {
  ads: AdItem[]
}

export const adsApi = {
  /**
   * 広告一覧取得（公開・認証不要）
   * facility_slug または facility_id を指定。施設が Free の場合のみ広告を返す。
   */
  async getAds(params: { facility_slug?: string; facility_id?: number }): Promise<AdListResponse> {
    const query = new URLSearchParams()
    if (params.facility_slug) query.set('facility_slug', params.facility_slug)
    if (params.facility_id != null) query.set('facility_id', String(params.facility_id))
    const response = await apiClient.get<AdListResponse>('/ads', { params: Object.fromEntries(query) })
    return response.data
  }
}
