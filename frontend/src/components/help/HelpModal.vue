<template>
  <Modal
    :model-value="helpStore.isModalOpen"
    @update:model-value="helpStore.closeModal"
    size="xl"
    title="ヘルプ"
  >
    <div class="flex flex-col h-[600px]">
      <!-- Tabs -->
      <div class="flex border-b border-gray-200 dark:border-gray-700 mb-4">
        <button
          @click="helpStore.setTab('faq')"
          :class="[
            'px-6 py-3 text-sm font-medium transition-colors',
            helpStore.currentTab === 'faq'
              ? 'border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          ]"
        >
          よくある質問
        </button>
        <button
          @click="helpStore.setTab('chat')"
          :class="[
            'px-6 py-3 text-sm font-medium transition-colors',
            helpStore.currentTab === 'chat'
              ? 'border-b-2 border-indigo-600 text-indigo-600 dark:text-indigo-400'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
          ]"
        >
          AIチャット
        </button>
      </div>

      <!-- FAQ Tab -->
      <div v-if="helpStore.currentTab === 'faq'" class="flex-1 overflow-y-auto">
        <div class="space-y-4">
          <!-- Search Bar -->
          <FaqSearchBar />

          <!-- Category Filter -->
          <CategoryFilter />

          <!-- FAQ List -->
          <FaqList />

          <!-- 問い合わせフォームへのリンク -->
          <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <router-link
              to="/admin/support"
              @click="helpStore.closeModal"
              class="flex items-center justify-center space-x-2 px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>お問い合わせフォームへ</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Chat Tab -->
      <div v-if="helpStore.currentTab === 'chat'" class="flex-1 overflow-hidden">
        <AiChatPanel />
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import Modal from '@/components/common/Modal.vue'
import FaqSearchBar from './FaqSearchBar.vue'
import CategoryFilter from './CategoryFilter.vue'
import FaqList from './FaqList.vue'
import AiChatPanel from './AiChatPanel.vue'
import { useHelpStore } from '@/stores/help'

const helpStore = useHelpStore()

// モーダルが開かれた時にFAQを取得
watch(() => helpStore.isModalOpen, async (isOpen) => {
  if (isOpen && helpStore.faqs.length === 0) {
    await helpStore.fetchFaqs()
  }
})
</script>

