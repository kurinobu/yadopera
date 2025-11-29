<template>
  <button
    @click="handleEscalation"
    :disabled="disabled"
    class="inline-flex items-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
  >
    <svg
      class="w-4 h-4 mr-2"
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
    {{ buttonText }}
  </button>
</template>

<script setup lang="ts">
interface Props {
  disabled?: boolean
  buttonText?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  buttonText: 'スタッフに連絡 / Contact Staff'
})

const emit = defineEmits<{
  escalation: []
}>()

const handleEscalation = () => {
  if (!props.disabled) {
    emit('escalation')
  }
}
</script>

<style scoped>
/* Component styles */
</style>

