<template>
  <Modal
    :model-value="isOpen"
    @update:model-value="$emit('update:isOpen', $event)"
    title="会話引き継ぎ / Link Conversation"
    size="sm"
  >
    <div class="space-y-4">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        他のデバイスで表示されている4桁の会話引き継ぎコードを入力してください。
        <br />
        Enter the 4-digit conversation code shown on your other device.
      </p>

      <Input
        v-model="tokenInput"
        type="text"
        placeholder="例: A1B2"
        :maxlength="4"
        :error="error"
        :disabled="isVerifying"
        @input="handleInput"
        @keyup.enter="handleSubmit"
      />

      <div class="flex items-center justify-end space-x-3">
        <Button
          variant="outline"
          @click="handleCancel"
          :disabled="isVerifying"
        >
          キャンセル / Cancel
        </Button>
        <Button
          variant="primary"
          @click="handleSubmit"
          :loading="isVerifying"
          :disabled="!canSubmit"
        >
          統合 / Link
        </Button>
      </div>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { isValidSessionToken } from '@/utils/validators'
import Modal from '@/components/common/Modal.vue'
import Input from '@/components/common/Input.vue'
import Button from '@/components/common/Button.vue'

interface Props {
  isOpen: boolean
  facilityId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  link: [token: string]
}>()

const tokenInput = ref('')
const error = ref<string | undefined>(undefined)
const isVerifying = ref(false)

const canSubmit = computed(() => {
  return isValidSessionToken(tokenInput.value) && !isVerifying.value
})

const handleInput = () => {
  // 大文字に変換
  tokenInput.value = tokenInput.value.toUpperCase()
  error.value = undefined
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    return
  }

  const token = tokenInput.value.trim().toUpperCase()

  if (!isValidSessionToken(token)) {
    error.value = '無効なトークンです / Invalid token'
    return
  }

  try {
    isVerifying.value = true
    error.value = undefined

    emit('link', token)
    
    // 成功時はモーダルを閉じる
    tokenInput.value = ''
    emit('update:isOpen', false)
  } catch (err: any) {
    error.value = err.message || 'トークンの検証に失敗しました / Token verification failed'
  } finally {
    isVerifying.value = false
  }
}

const handleCancel = () => {
  tokenInput.value = ''
  error.value = undefined
  emit('update:isOpen', false)
}
</script>

<style scoped>
/* Component styles */
</style>


