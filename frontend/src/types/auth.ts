/**
 * 認証関連の型定義
 */

export interface User {
  id: number
  email: string
  full_name: string | null
  role: 'owner' | 'staff' | 'admin'
  facility_id: number
  is_active: boolean
  email_verified: boolean  // ★追加
  /** 初回ログイン時やることリストモーダルを表示するか（施設の onboarding_modal_shown_at が NULL のとき true） */
  show_onboarding_modal?: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  facility_name: string
  subscription_plan?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface FacilityRegisterResponse {
  message: string
  email: string
  facility_name: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface VerifyEmailResponse {
  message: string
  email: string
}

export interface ResendVerificationRequest {
  email: string
}

export interface ResendVerificationResponse {
  message: string
  email: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirmRequest {
  token: string
  new_password: string
  confirm_password: string
}

export interface PasswordResetResponse {
  message: string
}

