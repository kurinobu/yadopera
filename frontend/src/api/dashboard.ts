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
    // ダッシュボードは8系統の集計のため、キャッシュミス時に時間がかかる。デフォルト10秒ではタイムアウトするため20秒に延長（報告書 5.3.2）
    const response = await apiClient.get<DashboardData>('/admin/dashboard', {
      params: { _t: Date.now() },
      headers: { 'Cache-Control': 'no-cache' },
      timeout: 20000 // 20秒（ステージング等でDBが遅い場合でも1本目で完了するように）
    })
    return response.data
  }
}


