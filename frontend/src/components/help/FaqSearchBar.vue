<template>
  <div class="relative">
    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="
          w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600
          bg-white dark:bg-gray-800 text-gray-900 dark:text-white
          focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
          transition-all
        "
        @input="handleInput"
      />
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
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
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useHelpStore } from '@/stores/help'

interface Props {
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'FAQを検索...',
})

const helpStore = useHelpStore()
const searchQuery = ref('')

// デバウンス処理
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(searchQuery, (newValue) => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    if (newValue.trim().length >= 2) {
      helpStore.searchFaqs(newValue)
    } else {
      helpStore.searchResults = []
      helpStore.searchQuery = ''
    }
  }, 300)
})

const handleInput = () => {
  // watchで処理される
}

const clearSearch = () => {
  searchQuery.value = ''
  helpStore.searchResults = []
  helpStore.searchQuery = ''
}
</script>

