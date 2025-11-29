/**
 * 夜間対応キューAPI
 */

import apiClient from './axios'
import type { OvernightQueue } from '@/types/dashboard'

export interface OvernightQueueListResponse {
  queues: OvernightQueue[]
  total: number
  pending_count: number
  resolved_count: number
}

export interface ProcessNotificationsResponse {
  processed_count: number
  total_count: number
}

export const overnightQueueApi = {
  /**
   * 夜間対応キュー取得
   */
  async getOvernightQueue(includeResolved?: boolean): Promise<OvernightQueueListResponse> {
    const params: Record<string, any> = {}
    if (includeResolved !== undefined) params.include_resolved = includeResolved
    
    const response = await apiClient.get<OvernightQueueListResponse>('/admin/overnight-queue', { params })
    return response.data
  },

  /**
   * 手動実行処理（MVP期間中）
   */
  async processNotifications(): Promise<ProcessNotificationsResponse> {
    const response = await apiClient.post<ProcessNotificationsResponse>('/admin/overnight-queue/process')
    return response.data
  }
}

