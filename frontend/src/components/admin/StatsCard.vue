<template>
  <div
    :class="[
      'bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6',
      colorClass
    ]"
  >
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
          {{ title }}
        </p>
        <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
          {{ formattedValue }}
        </p>
        <p v-if="subtitle" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {{ subtitle }}
        </p>
      </div>
      <div
        v-if="icon"
        :class="[
          'flex-shrink-0 p-3 rounded-full',
          iconBgClass
        ]"
      >
        <component :is="icon" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon?: () => ReturnType<typeof h>
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

const colorClass = computed(() => {
  const classes = {
    blue: '',
    green: '',
    yellow: '',
    red: '',
    purple: '',
    gray: ''
  }
  return classes[props.color]
})

const iconBgClass = computed(() => {
  const classes = {
    blue: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400',
    yellow: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400',
    red: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400',
    purple: 'bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400',
    gray: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
  }
  return classes[props.color]
})
</script>

<style scoped>
/* Component styles */
</style>


