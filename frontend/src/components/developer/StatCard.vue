<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ title }}</p>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{{ formattedValue }}</p>
        <p v-if="subtitle" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ subtitle }}</p>
      </div>
      <div v-if="icon" class="text-4xl opacity-20">
        <component :is="icon" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number | string
  subtitle?: string
  icon?: any
}

const props = defineProps<Props>()

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})
</script>

<style scoped>
/* Component styles */
</style>

