<template>
  <div :class="containerClasses">
    <div class="flex flex-col items-center justify-center">
      <!-- スピナー -->
      <div :class="spinnerClasses">
        <svg
          class="animate-spin"
          :class="spinnerSizeClasses"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      
      <!-- テキスト -->
      <p
        v-if="text"
        :class="textClasses"
      >
        {{ text }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  size?: 'sm' | 'md' | 'lg'
  fullScreen?: boolean
  overlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  fullScreen: false,
  overlay: false
})

const containerClasses = computed(() => {
  const baseClasses = 'flex items-center justify-center'
  
  if (props.fullScreen) {
    return `${baseClasses} fixed inset-0 z-50 bg-white dark:bg-gray-900 ${props.overlay ? 'bg-opacity-90 dark:bg-opacity-90' : ''}`
  }
  
  return `${baseClasses} py-8`
})

const spinnerClasses = computed(() => {
  return 'text-blue-600 dark:text-blue-400'
})

const spinnerSizeClasses = computed(() => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }
  return sizes[props.size]
})

const textClasses = computed(() => {
  const baseClasses = 'mt-4 text-sm font-medium'
  const colorClasses = 'text-gray-700 dark:text-gray-300'
  return `${baseClasses} ${colorClasses}`
})
</script>

<style scoped>
/* Component styles */
</style>

