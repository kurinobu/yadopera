/**
 * 定数定義
 */

// API設定
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 言語設定
export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  // MVPでは英語のみ、Phase 2で追加
] as const

// セッション設定
export const SESSION_COOKIE_NAME = 'yadopera_session_id'
export const SESSION_EXPIRES_DAYS = 1 // 24時間

// チャット設定
export const MAX_MESSAGE_LENGTH = 1000
export const MIN_MESSAGE_LENGTH = 1

// エスカレーション設定
export const ESCALATION_THRESHOLD_NORMAL = 0.7
export const ESCALATION_THRESHOLD_EARLY = 0.85

// タイムゾーン設定
export const DEFAULT_TIMEZONE = 'Asia/Tokyo'

// 夜間対応時間帯
export const NIGHT_START_HOUR = 22
export const NIGHT_END_HOUR = 8

// QRコード設置場所
export const QR_LOCATIONS = [
  { value: 'entrance', label: '入口' },
  { value: 'room', label: '客室' },
  { value: 'kitchen', label: 'キッチン' },
  { value: 'lounge', label: 'ラウンジ' },
  { value: 'custom', label: 'カスタム' }
] as const

