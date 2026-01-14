<template>
  <Teleport to="body">
    <button
      @click="handleClick"
      class="fixed bottom-6 right-6 z-50 group"
      aria-label="ヘルプ"
      title="ヘルプを表示"
    >
      <div
        class="
          flex items-center justify-center
          w-14 h-14 rounded-full
          bg-indigo-600 hover:bg-indigo-700
          text-white shadow-lg hover:shadow-xl
          transition-all duration-200
          group-hover:scale-110
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
    </button>
  </Teleport>
</template>

<script setup lang="ts">
import { useHelpStore } from '@/stores/help'

const helpStore = useHelpStore()

const handleClick = () => {
  helpStore.openModal()
}
</script>

