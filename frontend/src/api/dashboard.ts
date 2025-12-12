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
    const response = await apiClient.get<DashboardData>('/admin/dashboard')
    return response.data
  }
}


