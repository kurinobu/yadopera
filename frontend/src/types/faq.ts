/**
 * FAQ関連の型定義
 */

export type FAQCategory = 'basic' | 'facilities' | 'location' | 'trouble'

export interface FAQ {
  id: number
  facility_id: number
  category: FAQCategory
  language: string
  question: string
  answer: string
  priority: number  // 1-5
  is_active: boolean
  created_by?: number
  created_at: string
  updated_at: string
}

export interface FAQCreate {
  category: FAQCategory
  language: string
  question: string
  answer: string
  priority: number
}

export interface FAQUpdate {
  category?: FAQCategory
  language?: string
  question?: string
  answer?: string
  priority?: number
  is_active?: boolean
}

// 未解決質問
export interface UnresolvedQuestion {
  id: number
  message_id: number
  facility_id: number
  question: string
  language: string
  confidence_score: number  // 0.0-1.0
  created_at: string
}

// FAQ提案
export interface FaqSuggestion {
  id: number
  facility_id: number
  source_message_id: number
  suggested_question: string
  suggested_answer: string
  suggested_category: FAQCategory
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  reviewed_at?: string
  reviewed_by?: number
}

// 低評価回答
export interface LowRatedAnswer {
  message_id: number
  question: string
  answer: string
  negative_count: number
}

