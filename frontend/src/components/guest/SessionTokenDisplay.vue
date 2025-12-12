<template>
  <div
    v-if="token"
    class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg px-4 py-3 mb-4"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <svg
          class="w-5 h-5 text-blue-600 dark:text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
        <div>
          <p class="text-xs text-blue-700 dark:text-blue-300 font-medium mb-1">
            セッション統合トークン / Session Token
          </p>
          <p class="text-lg font-mono font-bold text-blue-900 dark:text-blue-100">
            {{ token }}
          </p>
        </div>
      </div>
      <div class="text-right">
        <p
          v-if="expiresAt"
          class="text-xs text-blue-600 dark:text-blue-400"
        >
          {{ timeRemaining }}
        </p>
        <button
          @click="handleCopy"
          class="mt-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 underline focus:outline-none"
        >
          コピー / Copy
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  token: string | null
  expiresAt?: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  copy: [token: string]
}>()

const timeRemaining = ref<string>('')
let intervalId: number | null = null

const updateTimeRemaining = () => {
  if (!props.expiresAt) {
    timeRemaining.value = ''
    return
  }

  const now = new Date().getTime()
  const expires = new Date(props.expiresAt).getTime()
  const diff = expires - now

  if (diff <= 0) {
    timeRemaining.value = '期限切れ / Expired'
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
    return
  }

  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)

  if (minutes > 0) {
    timeRemaining.value = `残り ${minutes}分 / ${minutes}min left`
  } else {
    timeRemaining.value = `残り ${seconds}秒 / ${seconds}sec left`
  }
}

onMounted(() => {
  if (props.expiresAt) {
    updateTimeRemaining()
    intervalId = window.setInterval(updateTimeRemaining, 1000)
  }
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

const handleCopy = async () => {
  if (!props.token) {
    return
  }

  try {
    await navigator.clipboard.writeText(props.token)
    emit('copy', props.token)
    // TODO: トースト通知を表示（Week 4で実装）
  } catch (error) {
    console.error('Copy failed:', error)
  }
}
</script>

<style scoped>
/* Component styles */
</style>


