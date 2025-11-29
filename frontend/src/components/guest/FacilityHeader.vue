<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
      {{ facility?.name || 'Loading...' }}
    </h2>
    <div v-if="facility" class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
      <div v-if="facility.phone" class="flex items-center space-x-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
        <span>{{ facility.phone }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>{{ facility.email }}</span>
      </div>
      <div v-if="facility.check_in_time && facility.check_out_time" class="flex items-center space-x-4 mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center space-x-2">
          <span class="font-medium">Check-in:</span>
          <span>{{ facility.check_in_time }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="font-medium">Check-out:</span>
          <span>{{ facility.check_out_time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Facility } from '@/types/facility'

interface Props {
  facility: Facility | null
}

defineProps<Props>()
</script>

<style scoped>
/* Component styles */
</style>

