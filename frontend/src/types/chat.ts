/**
 * チャット関連の型定義
 */

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  ai_confidence?: number
  matched_faq_ids?: number[]
  created_at: string
}

export interface Conversation {
  id: number
  session_id: string
  facility_id: number
  guest_language: string
  location?: string
  started_at: string
  last_activity_at: string
  ended_at?: string
  is_escalated: boolean
  total_messages: number
}

export interface ChatRequest {
  facility_id: number
  message: string
  language?: string
  location?: string
  session_id?: string
}

export interface ChatResponse {
  message: ChatMessage
  session_id: string
  ai_confidence?: number
  is_escalated: boolean
  escalation_id?: number
}

export interface ChatHistoryResponse {
  session_id: string
  facility_id: number
  language: string
  location?: string
  started_at: string
  last_activity_at: string
  messages: ChatMessage[]
}

export interface FeedbackRequest {
  message_id: number
  feedback_type: 'positive' | 'negative'
}

export interface FeedbackResponse {
  id: number
  message_id: number
  feedback_type: 'positive' | 'negative'
  created_at: string
}

export interface EscalationRequest {
  facility_id: number
  session_id: string
}

export interface EscalationResponse {
  success: boolean
  escalation_id: number
  message: string
}

