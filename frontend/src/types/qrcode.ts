/**
 * QRコード関連の型定義
 */

export type QRCodeLocation = 'entrance' | 'room' | 'kitchen' | 'lounge' | 'custom'

export interface QRCodeRequest {
  facility_id: number
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean  // v0.3新規
}

export interface QRCodeResponse {
  id: number
  facility_id: number
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean
  qr_code_url: string
  qr_code_data: string  // QRコードのデータ（URL）
  format: 'pdf' | 'png' | 'svg'
  created_at: string
}

