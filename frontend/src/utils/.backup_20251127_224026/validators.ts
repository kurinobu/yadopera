/**
 * バリデーション関数
 */

// メールアドレスバリデーション
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// パスワードバリデーション（最低8文字）
export function isValidPassword(password: string): boolean {
  return password.length >= 8
}

// メッセージ長バリデーション
export function isValidMessage(message: string): boolean {
  const MIN_LENGTH = 1
  const MAX_LENGTH = 1000
  return message.length >= MIN_LENGTH && message.length <= MAX_LENGTH
}

// セッション統合トークンバリデーション（4桁英数字）
export function isValidSessionToken(token: string): boolean {
  const tokenRegex = /^[A-Z0-9]{4}$/
  return tokenRegex.test(token.toUpperCase())
}

// 施設IDバリデーション
export function isValidFacilityId(facilityId: string | number): boolean {
  const id = typeof facilityId === 'string' ? parseInt(facilityId, 10) : facilityId
  return !isNaN(id) && id > 0
}

