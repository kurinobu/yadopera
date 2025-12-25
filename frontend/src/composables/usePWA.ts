/**
 * PWA Composable
 */

import { ref, onMounted, onUnmounted } from 'vue'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function usePWA() {
  const isInstallable = ref(false)
  const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
  const isInstalled = ref(false)

  function handleBeforeInstallPrompt(e: Event) {
    e.preventDefault()
    deferredPrompt.value = e as BeforeInstallPromptEvent
    isInstallable.value = true
  }

  function handleAppInstalled() {
    isInstallable.value = false
    deferredPrompt.value = null
    isInstalled.value = true
    
    // 修正案2: appinstalledイベントでも施設URLを保存
    try {
      if (typeof window !== 'undefined' && window.location) {
        const currentPath = window.location.pathname
        if (currentPath.startsWith('/f/')) {
          const facilityUrl = window.location.pathname + window.location.search
          localStorage.setItem('last_facility_url', facilityUrl)
          console.log('[PWA] appinstalledイベント: 施設URLを保存しました', facilityUrl)
        }
      }
    } catch (error) {
      console.warn('[PWA] appinstalledイベント: 施設URLの保存に失敗しました', error)
    }
  }

  function checkIfInstalled() {
    // スタンドアロンモードで実行されているか確認
    try {
      if (typeof window !== 'undefined' && window.matchMedia) {
        if (window.matchMedia('(display-mode: standalone)').matches) {
          isInstalled.value = true
          isInstallable.value = false
        }
      }
    } catch (error) {
      console.warn('Failed to check if installed:', error)
    }
  }

  onMounted(() => {
    // 既にインストールされているか確認
    checkIfInstalled()

    // beforeinstallpromptイベントをリッスン
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    // アプリがインストールされた場合
    window.addEventListener('appinstalled', handleAppInstalled)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.removeEventListener('appinstalled', handleAppInstalled)
  })

  async function install(): Promise<boolean> {
    if (!deferredPrompt.value) {
      return false
    }

    try {
      await deferredPrompt.value.prompt()
      const { outcome } = await deferredPrompt.value.userChoice
      
      if (outcome === 'accepted') {
        isInstallable.value = false
        deferredPrompt.value = null
        isInstalled.value = true
        return true
      }
      
      return false
    } catch (error) {
      console.error('PWA installation error:', error)
      return false
    }
  }

  return {
    isInstallable,
    isInstalled,
    install
  }
}

