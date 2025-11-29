<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- ダークモード切替ボタン（右上固定） -->
    <div class="fixed top-4 right-4 z-40">
      <DarkModeToggle />
    </div>

    <!-- メインコンテンツ -->
    <slot />

    <!-- PWAインストールプロンプト -->
    <PWAInstallPrompt />
  </div>
</template>

<script setup lang="ts">
import DarkModeToggle from '@/components/common/DarkModeToggle.vue'
import PWAInstallPrompt from '@/components/common/PWAInstallPrompt.vue'
</script>

<style scoped>
/* Component styles */
</style>

