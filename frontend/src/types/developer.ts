/**
 * 開発者管理ページ関連の型定義
 */

export interface SystemOverview {
  total_facilities: number
  active_facilities: number
  total_faqs: number
  errors_24h: {
    critical: number
    error: number
    warning: number
  }
  chats_7d: number
  escalations_7d: number
}

export interface FacilitySummary {
  id: number
  name: string
  is_active: boolean
  faq_count: number
  chats_7d: number
  errors_7d: number
  last_admin_login: string | null
}

export interface ErrorLog {
  id: number
  level: 'critical' | 'error' | 'warning'
  code: string
  message: string
  request_path?: string
  facility_name?: string
  created_at: string
}

export interface ErrorLogDetail extends ErrorLog {
  stack_trace?: string
  request_method?: string
  facility?: {
    id: number
    name: string
  }
  user?: {
    id: number
    email: string
  }
  ip_address?: string
  user_agent?: string
}

export interface PaginationInfo {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface ErrorLogListResponse {
  errors: ErrorLog[]
  pagination: PaginationInfo
}

export interface SystemHealthResponse {
  database: {
    status: string
    response_time_ms?: number
    error?: string
  }
  redis: {
    status: string
    response_time_ms?: number
    error?: string
  }
  openai_api?: {
    status: string
    response_time_ms?: number | null
    error?: string
  }
}

