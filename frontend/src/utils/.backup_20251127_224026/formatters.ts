/**
 * フォーマット関数
 */

// 日時フォーマット
export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(d)
}

// 日付フォーマット
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(d)
}

// 時刻フォーマット
export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(d)
}

// 相対時間フォーマット（例: "5分前"）
export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) {
    return 'たった今'
  } else if (minutes < 60) {
    return `${minutes}分前`
  } else if (hours < 24) {
    return `${hours}時間前`
  } else if (days < 7) {
    return `${days}日前`
  } else {
    return formatDate(d)
  }
}

// 信頼度スコアフォーマット（0.0-1.0 → 0-100%）
export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`
}

// パーセンテージフォーマット（0.0-1.0 → 0-100%）
export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`
}

