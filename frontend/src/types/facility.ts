/**
 * 施設関連の型定義
 */

export interface Facility {
  id: number
  name: string
  slug: string
  email: string
  phone?: string
  check_in_time: string
  check_out_time: string
  wifi_ssid?: string
  plan_type?: string  // 料金プラン（Free, Mini, Small, Standard, Premium）
  available_languages?: string[]  // 利用可能言語リスト
}

export interface TopQuestion {
  id: number
  question: string
  answer: string
  category: string
}

export interface FacilityPublicResponse {
  facility: Facility
  top_questions: TopQuestion[]
}

export interface StaffAbsencePeriod {
  start_time: string  // "HH:MM"形式
  end_time: string    // "HH:MM"形式
  days_of_week: string[]  // ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
}

export interface FacilitySettingsFacility {
  id: number
  name: string
  slug: string
  email: string
  phone?: string
  address?: string
  wifi_ssid?: string
  wifi_password?: string  // マスク表示用
  check_in_time?: string  // "HH:MM"形式
  check_out_time?: string  // "HH:MM"形式
  house_rules?: string
  local_info?: string
  prohibited_items?: string
  languages: string[]
  timezone: string
  subscription_plan: string
  monthly_question_limit: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface FacilitySettingsResponse {
  facility: FacilitySettingsFacility
  staff_absence_periods: StaffAbsencePeriod[]
  icon_url?: string | null
}

export interface FacilitySettingsUpdateRequest {
  name?: string
  email?: string
  phone?: string
  address?: string
  wifi_ssid?: string
  wifi_password?: string  // 変更時のみ
  check_in_time?: string  // "HH:MM"形式
  check_out_time?: string  // "HH:MM"形式
  house_rules?: string
  local_info?: string
  prohibited_items?: string
  staff_absence_periods?: StaffAbsencePeriod[]
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

