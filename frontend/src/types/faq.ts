/**
 * FAQ関連の型定義（インテントベース構造）
 */

export type FAQCategory = 'basic' | 'facilities' | 'location' | 'trouble'

/**
 * FAQ翻訳（言語ごとの質問・回答）
 */
export interface FAQTranslation {
  id: number
  faq_id: number
  language: string  // 'en', 'ja', 'zh-TW', 'fr'
  question: string
  answer: string
  created_at: string
  updated_at: string
}

/**
 * FAQ（インテントベース構造）
 * 言語ごとの質問・回答はtranslationsに含まれる
 */
export interface FAQ {
  id: number
  facility_id: number
  category: FAQCategory
  intent_key: string  // インテント識別キー（例: 'basic_checkout_time'）
  translations: FAQTranslation[]  // 翻訳リスト（最低1つの言語が必要）
  priority: number  // 1-5
  is_active: boolean
  created_by?: number
  created_at: string
  updated_at: string
}

/**
 * FAQ翻訳作成リクエスト
 */
export interface FAQTranslationCreate {
  language: string  // 'en', 'ja', 'zh-TW', 'fr'
  question: string  // 1-500文字
  answer: string  // 1-2000文字
}

/**
 * FAQ作成リクエスト（インテントベース構造）
 */
export interface FAQCreate {
  category: FAQCategory
  intent_key?: string  // オプション（自動生成される場合は省略可能）
  translations: FAQTranslationCreate[]  // 最低1つの言語が必要
  priority: number  // 1-5、デフォルト: 1
  is_active?: boolean  // デフォルト: true
}

/**
 * FAQ更新リクエスト（インテントベース構造）
 */
export interface FAQUpdate {
  category?: FAQCategory
  intent_key?: string
  translations?: FAQTranslationCreate[]  // オプション
  priority?: number  // 1-5
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


