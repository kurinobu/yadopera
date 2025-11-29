/**
 * QRコード生成API
 */

import apiClient from './axios'
import type { QRCodeLocation, QRCodeResponse } from '@/types/qrcode'

export interface QRCodeRequest {
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean
  format: 'pdf' | 'png' | 'svg'
  primary_session_id?: string
}

export const qrcodeApi = {
  /**
   * QRコード生成
   */
  async generateQRCode(data: QRCodeRequest): Promise<QRCodeResponse> {
    const response = await apiClient.post<QRCodeResponse>('/admin/qr-code', data)
    return response.data
  }
}

