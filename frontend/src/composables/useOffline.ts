/**
 * オフライン検出コンポーザブル
 * navigator.onLineとonline/offlineイベントを使用してオフライン状態を検出
 */

import { ref, onMounted, onUnmounted } from 'vue'

/**
 * オフライン検出コンポーザブル
 * @returns {Object} isOffline - オフライン状態を示すリアクティブな値
 */
export function useOffline() {
  const isOffline = ref(!navigator.onLine)

  const updateOnlineStatus = () => {
    isOffline.value = !navigator.onLine
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)
  })

  return {
    isOffline
  }
}
