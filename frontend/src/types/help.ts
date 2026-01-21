/**
 * ヘルプシステム型定義
 */

/**
 * FAQカテゴリ
 */
export type FaqCategory = 
  | 'setup'
  | 'qrcode'
  | 'faq_management'
  | 'ai_logic'
  | 'logs'
  | 'troubleshooting'
  | 'billing'
  | 'security';

/**
 * FAQ項目
 */
export interface Faq {
  id: number;
  category: FaqCategory;
  question: string;
  answer: string;
  keywords?: string;
  related_url?: string;
  display_order: number;
  relevance_score?: number;
}

/**
 * FAQリストレスポンス
 */
export interface FaqListResponse {
  faqs: Faq[];
  total: number;
  categories: string[];
}

/**
 * FAQ検索レスポンス
 */
export interface FaqSearchResponse {
  results: Faq[];
  total: number;
  query: string;
}

/**
 * チャットメッセージタイプ
 */
export type MessageRole = 'user' | 'assistant';

/**
 * チャットメッセージ
 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  related_faqs?: number[];
  related_url?: string;
}

/**
 * チャットリクエスト
 */
export interface ChatRequest {
  message: string;
  language: string;
}

/**
 * チャットレスポンス
 */
export interface ChatResponse {
  response: string;
  related_faqs: number[];
  related_url?: string;
  timestamp: string;
}

/**
 * ヘルプモーダルタブ
 */
export type HelpTab = 'faq' | 'chat';

/**
 * カテゴリ情報
 */
export interface CategoryInfo {
  category: FaqCategory;
  count: number;
  label: string;
}

