<template>
  <header class="sticky top-0 z-20 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
    <div class="flex items-center justify-between">
      <!-- モバイルメニューボタン -->
      <button
        @click="$emit('open-mobile-menu')"
        class="md:hidden p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="メニューを開く"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <!-- ページタイトル -->
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ title }}
      </h2>

      <!-- 右側メニュー -->
      <div class="flex items-center space-x-3">
        <DarkModeToggle />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DarkModeToggle from '@/components/common/DarkModeToggle.vue'

defineEmits<{
  'open-mobile-menu': []
}>()

const route = useRoute()

// ページタイトルをルート名から取得
const title = computed(() => {
  const titles: Record<string, string> = {
    AdminDashboard: 'ダッシュボード',
    AdminFaqs: 'FAQ管理',
    AdminOvernightQueue: 'スタッフ不在時間帯対応キュー',
    AdminQRCode: 'QRコード発行'
  }
  return titles[route.name as string] || '管理画面'
})
</script>

<style scoped>
/* Component styles */
</style>

