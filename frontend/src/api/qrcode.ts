/**
 * QRコード生成API
 */

import apiClient from './axios'
import type { QRCodeLocation, QRCodeResponse, QRCodeListResponse } from '@/types/qrcode'

export interface QRCodeRequest {
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean
  format: 'pdf' | 'png' | 'svg'
  primary_session_id?: string
}

export const qrcodeApi = {
  /**
   * QRコード生成（データベースに保存する）
   */
  async generateQRCode(data: QRCodeRequest): Promise<QRCodeResponse> {
    const response = await apiClient.post<QRCodeResponse>('/admin/qr-code', data)
    return response.data
  },

  /**
   * QRコードプレビュー生成（データベースに保存しない）
   */
  async generateQRCodePreview(data: {
    location: QRCodeLocation
    custom_location_name?: string
    format: 'pdf' | 'png' | 'svg'
  }): Promise<QRCodeResponse> {
    const response = await apiClient.post<QRCodeResponse>('/admin/qr-code/preview', {
      location: data.location,
      custom_location_name: data.custom_location_name,
      format: data.format
    })
    return response.data
  },

  /**
   * 生成済みQRコード一覧を取得
   */
  async listQRCodes(): Promise<QRCodeListResponse> {
    const response = await apiClient.get<QRCodeListResponse>('/admin/qr-codes')
    return response.data
  },

  /**
   * QRコードを削除
   */
  async deleteQRCode(id: number): Promise<void> {
    await apiClient.delete(`/admin/qr-code/${id}`)
  }
}

