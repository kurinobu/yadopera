<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- ダークモード切替ボタン（右上固定、Chat画面以外で表示） -->
    <div v-if="showGlobalDarkModeToggle" class="fixed top-4 right-4 z-40">
      <DarkModeToggle />
    </div>

    <!-- メインコンテンツ -->
    <slot />

    <!-- PWAインストールプロンプト -->
    <PWAInstallPrompt />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DarkModeToggle from '@/components/common/DarkModeToggle.vue'
import PWAInstallPrompt from '@/components/common/PWAInstallPrompt.vue'
import { updateManifestLink } from '@/utils/manifestGenerator'

const route = useRoute()

// Chat画面ではヘッダー内にダークモード切り替えボタンがあるため、固定ボタンを非表示にする
const showGlobalDarkModeToggle = computed(() => {
  return route.name !== 'Chat'
})

// ゲスト側のルートにアクセスした際、manifestを自動更新（Safari iOS対応）
onMounted(() => {
  if (route.path.startsWith('/f/')) {
    const facilityId = route.params.facilityId as string
    updateManifestLink(facilityId)
  }
})
</script>

<style scoped>
/* Component styles */
</style>

