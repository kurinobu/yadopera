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

    <!-- ヘルプボタン（全ページ共通） -->
    <HelpButton />

    <!-- ヘルプモーダル -->
    <HelpModal />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import Header from '@/components/admin/Header.vue'
import HelpButton from '@/components/help/HelpButton.vue'
import HelpModal from '@/components/help/HelpModal.vue'
import { useHelpStore } from '@/stores/help'

const isMobileMenuOpen = ref(false)
const helpStore = useHelpStore()

onMounted(async () => {
  // 初回FAQデータ読み込み
  if (helpStore.faqs.length === 0) {
    await helpStore.fetchFaqs()
  }
})
</script>

<style scoped>
/* Component styles */
</style>
