<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- サイドバー -->
    <Sidebar
      :is-mobile-menu-open="isMobileMenuOpen"
      @close-mobile-menu="isMobileMenuOpen = false"
    />

    <!-- メインコンテンツ -->
    <div class="flex-1 flex flex-col overflow-hidden md:ml-64">
      <!-- ヘッダー -->
      <Header @open-mobile-menu="isMobileMenuOpen = true" />

      <!-- ページコンテンツ -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import Header from '@/components/admin/Header.vue'

const isMobileMenuOpen = ref(false)
</script>

<style scoped>
/* Component styles */
</style>


