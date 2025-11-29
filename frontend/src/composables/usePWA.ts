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
  }

  function checkIfInstalled() {
    // スタンドアロンモードで実行されているか確認
    if (window.matchMedia('(display-mode: standalone)').matches) {
      isInstalled.value = true
      isInstallable.value = false
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

