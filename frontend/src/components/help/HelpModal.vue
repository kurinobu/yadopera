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
import Modal from '@/components/common/Modal.vue'
import FaqSearchBar from './FaqSearchBar.vue'
import CategoryFilter from './CategoryFilter.vue'
import FaqList from './FaqList.vue'
import AiChatPanel from './AiChatPanel.vue'
import { useHelpStore } from '@/stores/help'

const helpStore = useHelpStore()
</script>

