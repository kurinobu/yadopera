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

