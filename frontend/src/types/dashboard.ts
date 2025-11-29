/**
 * ダッシュボード関連の型定義
 */

// 週次サマリー
export interface WeeklySummary {
  period: {
    start: string
    end: string
  }
  total_questions: number
  auto_response_rate: number  // 0.0-1.0
  average_response_time_ms: number
  average_confidence: number  // 0.0-1.0
  category_breakdown: {
    basic: number
    facilities: number
    location: number
    trouble: number
  }
  top_questions: Array<{
    question: string
    count: number
  }>
  unresolved_count: number
}

// リアルタイムチャット履歴
export interface ChatHistory {
  session_id: string
  guest_language: string
  last_message: string
  ai_confidence: number  // 0.0-1.0
  created_at: string
}

// 夜間対応キュー
export interface OvernightQueue {
  id: number
  facility_id: number
  escalation_id: number
  guest_message: string
  language: string
  scheduled_notify_at: string  // 翌朝8:00
  notified_at: string | null
  resolved_at: string | null
  resolved_by: number | null
  created_at: string
}

// ゲストフィードバック統計
export interface FeedbackStats {
  positive_count: number
  negative_count: number
  positive_rate: number  // 0.0-1.0
  low_rated_answers: Array<{
    message_id: number
    question: string
    answer: string
    negative_count: number
  }>
}

// ダッシュボードデータ
export interface DashboardData {
  summary: WeeklySummary
  recent_conversations: ChatHistory[]
  overnight_queue: OvernightQueue[]
  feedback_stats: FeedbackStats
}

