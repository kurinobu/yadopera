<template>
  <button
    @click="handleClick"
    :class="cardClasses"
    :disabled="disabled"
  >
    <div class="flex flex-col items-center space-y-2">
      <span class="text-4xl">{{ language.flag }}</span>
      <span class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ language.name }}
      </span>
      <span class="text-sm text-gray-600 dark:text-gray-400">
        {{ language.code.toUpperCase() }}
      </span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { SUPPORTED_LANGUAGES } from '@/utils/constants'

type Language = typeof SUPPORTED_LANGUAGES[number]

interface Props {
  language: Language
  selected?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  disabled: false
})

const emit = defineEmits<{
  click: [language: Language]
}>()

const cardClasses = computed(() => {
  const baseClasses = 'w-full p-6 rounded-lg border-2 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  if (props.selected) {
    return `${baseClasses} border-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-500 focus:ring-blue-500`
  }
  
  return `${baseClasses} border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-600 dark:hover:bg-blue-900/20 focus:ring-blue-500`
})

const handleClick = () => {
  if (!props.disabled) {
    emit('click', props.language)
  }
}
</script>

<style scoped>
/* Component styles */
</style>


