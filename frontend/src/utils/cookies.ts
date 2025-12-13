/**
 * Cookie操作関数
 * @vueuse/coreのuseCookiesを使用
 */

import { useCookies } from '@vueuse/integrations/useCookies'

const cookies = useCookies()

/**
 * Cookie値を取得
 */
export function getCookie(name: string): string | undefined {
  return cookies.get(name)
}

/**
 * Cookie値を設定
 */
export function setCookie(
  name: string,
  value: string,
  options?: {
    expires?: Date
    maxAge?: number
    path?: string
    domain?: string
    secure?: boolean
    sameSite?: 'strict' | 'lax' | 'none'
  }
): void {
  cookies.set(name, value, options)
}

/**
 * Cookie値を削除
 */
export function removeCookie(name: string, options?: { path?: string; domain?: string }): void {
  cookies.remove(name, options)
}

/**
 * Cookieが存在するか確認
 */
export function hasCookie(name: string): boolean {
  return cookies.get(name) !== undefined
}


