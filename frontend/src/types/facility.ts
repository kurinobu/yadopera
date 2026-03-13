/**
 * 施設関連の型定義
 */

/** クーポン設定（公開・有効時のみ） */
export interface FacilityCoupon {
  enabled: boolean
  discount_percent: number
  description?: string | null
  validity_months?: number | null
}

export interface Facility {
  id: number
  name: string
  slug: string
  /** ゲスト画面に表示するが OFF のときは null */
  email?: string | null
  phone?: string
  check_in_time: string
  check_out_time: string
  wifi_ssid?: string
  plan_type?: string  // 料金プラン（Free, Mini, Small, Standard, Premium）
  available_languages?: string[]  // 利用可能言語リスト
  /** クーポン有効時のみ設定（リードゲット） */
  coupon?: FacilityCoupon | null
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
  plan_type?: string  // Free, Mini, Small, Standard, Premium（CSV一括登録の表示判定用）
  monthly_question_limit: number
  is_active: boolean
  /** クーポン（リードゲット）設定 */
  coupon_enabled?: boolean
  coupon_discount_percent?: number | null
  coupon_description?: string | null
  coupon_validity_months?: number | null
  /** 公式サイトURL（クーポン送付メールで案内） */
  official_website_url?: string | null
  /** ゲスト画面にメールアドレスを表示する */
  show_email_on_guest_screen?: boolean
  /** プラン超過時の挙動（continue_billing | faq_only） */
  overage_behavior?: string
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
  /** クーポン（リードゲット）設定 */
  coupon_enabled?: boolean
  coupon_discount_percent?: number | null
  coupon_description?: string
  coupon_validity_months?: number | null
  /** 公式サイトURL（任意） */
  official_website_url?: string | null
  /** ゲスト画面にメールアドレスを表示する */
  show_email_on_guest_screen?: boolean
  /** プラン超過時の挙動（continue_billing | faq_only） */
  overage_behavior?: 'continue_billing' | 'faq_only'
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

