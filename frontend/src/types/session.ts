/**
 * セッション関連の型定義
 */

export interface SessionLinkRequest {
  facility_id: number
  token: string
  current_session_id: string
}

export interface SessionLinkResponse {
  success: boolean
  message: string
  primary_session_id: string
  linked_session_ids: string[]
}

export interface SessionTokenVerifyResponse {
  valid: boolean
  facility_id?: number
  primary_session_id?: string
  expires_at?: string
}

export interface SessionTokenGenerateRequest {
  facility_id: number
  session_id: string
}

export interface SessionTokenResponse {
  token: string
  primary_session_id: string
  linked_session_ids: string[]
  expires_at: string
  created_at: string
}

