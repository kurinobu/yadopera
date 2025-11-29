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

