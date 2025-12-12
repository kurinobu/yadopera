<template>
  <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
    <div class="flex items-start space-x-3">
      <div class="flex-shrink-0">
        <svg
          class="w-6 h-6 text-red-600 dark:text-red-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <div class="flex-1">
        <h4 class="text-sm font-semibold text-red-900 dark:text-red-300 mb-2">
          緊急連絡先 / Emergency Contact
        </h4>
        <div class="space-y-2 text-sm text-red-800 dark:text-red-400">
          <div class="flex items-center space-x-2">
            <span class="font-medium">救急・消防:</span>
            <a
              href="tel:119"
              class="underline hover:no-underline font-semibold"
            >
              119
            </a>
          </div>
          <div class="flex items-center space-x-2">
            <span class="font-medium">警察:</span>
            <a
              href="tel:110"
              class="underline hover:no-underline font-semibold"
            >
              110
            </a>
          </div>
          <div v-if="facilityPhone" class="flex items-center space-x-2 mt-3 pt-3 border-t border-red-200 dark:border-red-800">
            <span class="font-medium">施設連絡先:</span>
            <a
              :href="`tel:${facilityPhone}`"
              class="underline hover:no-underline font-semibold"
            >
              {{ facilityPhone }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  facilityPhone?: string
}

defineProps<Props>()
</script>

<style scoped>
/* Component styles */
</style>


