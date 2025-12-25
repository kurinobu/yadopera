<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-2"
  >
    <div
      v-if="shouldShow"
      class="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4"
    >
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg
            class="w-6 h-6 text-blue-600 dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-1">
            アプリをインストール
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
            やどぺらをホーム画面に追加して、オフラインでも利用できます。
          </p>
          <div class="flex space-x-2">
            <button
              @click="handleInstall"
              :disabled="isInstalling"
              class="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ isInstalling ? 'インストール中...' : 'インストール' }}
            </button>
            <button
              @click="dismiss"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              後で
            </button>
          </div>
        </div>
        <button
          @click="dismiss"
          class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none"
          aria-label="閉じる"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePWA } from '@/composables/usePWA'

const { isInstallable, isInstalled, install } = usePWA()
const isInstalling = ref(false)
const isDismissed = ref(false)

// localStorageから非表示状態を確認
const DISMISSED_KEY = 'pwa_install_dismissed'
const dismissed = localStorage.getItem(DISMISSED_KEY)
if (dismissed) {
  isDismissed.value = true
}

const handleInstall = async () => {
  isInstalling.value = true
  try {
    const success = await install()
    if (success) {
      isDismissed.value = true
    }
  } catch (error) {
    console.error('Installation failed:', error)
  } finally {
    isInstalling.value = false
  }
}

const dismiss = () => {
  isDismissed.value = true
  localStorage.setItem(DISMISSED_KEY, 'true')
}

// 非表示状態を反映
const shouldShow = computed(() => {
  return isInstallable.value && !isInstalled.value && !isDismissed.value
})
</script>

<style scoped>
/* Component styles */
</style>

