/**
 * セッション管理Composable
 */

import { useCookies } from '@vueuse/integrations/useCookies'
import { useChatStore } from '@/stores/chat'
import { sessionApi } from '@/api/session'
// UUID生成（crypto.randomUUIDを使用、ブラウザネイティブ）
function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  // フォールバック: 簡易UUID生成
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const cookies = useCookies()
const SESSION_ID_COOKIE_NAME = 'yadopera_session_id'
const SESSION_ID_EXPIRES_DAYS = 1 // 24時間

export function useSession() {
  const chatStore = useChatStore()

  /**
   * セッションIDを取得または生成
   */
  function getOrCreateSessionId(): string {
    let sessionId = cookies.get(SESSION_ID_COOKIE_NAME)

    if (!sessionId) {
      sessionId = generateUUID()
      cookies.set(SESSION_ID_COOKIE_NAME, sessionId, {
        expires: new Date(Date.now() + SESSION_ID_EXPIRES_DAYS * 24 * 60 * 60 * 1000),
        sameSite: 'lax',
        secure: import.meta.env.PROD
      })
      chatStore.setSessionId(sessionId)
    } else {
      chatStore.setSessionId(sessionId)
    }

    return sessionId
  }

  /**
   * セッションIDを取得
   */
  function getSessionId(): string | null {
    return cookies.get(SESSION_ID_COOKIE_NAME) || chatStore.currentSessionId
  }

  /**
   * セッション統合
   */
  async function linkSession(facilityId: number, token: string): Promise<void> {
    const currentSessionId = getOrCreateSessionId()
    
    try {
      const response = await sessionApi.linkSession({
        facility_id: facilityId,
        token,
        current_session_id: currentSessionId
      })

      // 統合されたセッションIDを設定
      if (response.primary_session_id) {
        chatStore.setSessionId(response.primary_session_id)
        cookies.set(SESSION_ID_COOKIE_NAME, response.primary_session_id, {
          expires: new Date(Date.now() + SESSION_ID_EXPIRES_DAYS * 24 * 60 * 60 * 1000),
          sameSite: 'lax',
          secure: import.meta.env.PROD
        })
      }
    } catch (error) {
      throw error
    }
  }

  /**
   * トークン検証
   */
  async function verifyToken(token: string): Promise<boolean> {
    try {
      const response = await sessionApi.verifyToken(token)
      return response.valid
    } catch (error) {
      return false
    }
  }

  /**
   * セッションをクリア
   */
  function clearSession() {
    cookies.remove(SESSION_ID_COOKIE_NAME)
    chatStore.clearChat()
  }

  return {
    getOrCreateSessionId,
    getSessionId,
    linkSession,
    verifyToken,
    clearSession
  }
}

