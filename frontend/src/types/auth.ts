/**
 * 認証関連の型定義
 */

export interface User {
  id: number
  email: string
  full_name: string
  role: 'owner' | 'staff' | 'admin'
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

