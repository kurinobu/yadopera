<template>
  <div class="w-full">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <textarea
        v-if="type === 'textarea'"
        :id="inputId"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :rows="rows"
        :maxlength="maxlength"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
      />
      <input
        v-else
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :maxlength="maxlength"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
      />
      <div
        v-if="error"
        class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"
      >
        <svg
          class="w-5 h-5 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </p>
    <p v-else-if="hint" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea'
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
  hint?: string
  maxlength?: number
  rows?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  rows: 4
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
}>()

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const baseClasses = 'block w-full rounded-lg border shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
  
  const stateClasses = props.error
    ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500 dark:border-red-600 dark:text-red-200 dark:placeholder-red-400'
    : 'border-gray-300 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:placeholder-gray-400'
  
  const sizeClasses = props.type === 'textarea'
    ? 'px-3 py-2 text-sm'
    : 'px-3 py-2 text-sm'
  
  return [baseClasses, stateClasses, sizeClasses].join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}
</script>

<style scoped>
/* Component styles */
</style>

