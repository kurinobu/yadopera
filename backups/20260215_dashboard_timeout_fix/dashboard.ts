/**
 * ダッシュボードAPI
 */

import apiClient from './axios'
import type { DashboardData } from '@/types/dashboard'

export const dashboardApi = {
  /**
   * ダッシュボードデータ取得
   */
  async getDashboard(): Promise<DashboardData> {
    // キャッシュを確実にバイパスするため、クエリにタイムスタンプを付与
    const response = await apiClient.get<DashboardData>('/admin/dashboard', {
      params: { _t: Date.now() },
      headers: { 'Cache-Control': 'no-cache' }
    })
    return response.data
  }
}


