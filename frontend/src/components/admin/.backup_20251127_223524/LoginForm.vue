<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- メールアドレス入力 -->
    <Input
      v-model="email"
      type="email"
      label="メールアドレス / Email"
      placeholder="example@email.com"
      :required="true"
      :error="errors.email"
      :disabled="isLoading"
    />

    <!-- パスワード入力 -->
    <Input
      v-model="password"
      type="password"
      label="パスワード / Password"
      placeholder="••••••••"
      :required="true"
      :error="errors.password"
      :disabled="isLoading"
    />

    <!-- エラーメッセージ -->
    <div
      v-if="errors.general"
      class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
    >
      <p class="text-sm text-red-600 dark:text-red-400">
        {{ errors.general }}
      </p>
    </div>

    <!-- ログインボタン -->
    <Button
      type="submit"
      variant="primary"
      size="lg"
      :loading="isLoading"
      :disabled="!canSubmit"
      full-width
    >
      ログイン / Login
    </Button>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { isValidEmail, isValidPassword } from '@/utils/validators'
import Input from '@/components/common/Input.vue'
import Button from '@/components/common/Button.vue'

interface Props {
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false
})

const emit = defineEmits<{
  submit: [email: string, password: string]
}>()

const email = ref('')
const password = ref('')
const errors = ref<{
  email?: string
  password?: string
  general?: string
}>({})

const canSubmit = computed(() => {
  return isValidEmail(email.value) && isValidPassword(password.value) && !props.isLoading
})

const validate = (): boolean => {
  errors.value = {}

  if (!email.value) {
    errors.value.email = 'メールアドレスを入力してください'
    return false
  }

  if (!isValidEmail(email.value)) {
    errors.value.email = '有効なメールアドレスを入力してください'
    return false
  }

  if (!password.value) {
    errors.value.password = 'パスワードを入力してください'
    return false
  }

  if (!isValidPassword(password.value)) {
    errors.value.password = 'パスワードは8文字以上で入力してください'
    return false
  }

  return true
}

const handleSubmit = () => {
  if (!validate()) {
    return
  }

  emit('submit', email.value, password.value)
}

// エラーを外部から設定できるようにする
defineExpose({
  setError: (error: string) => {
    errors.value.general = error
  },
  clearErrors: () => {
    errors.value = {}
  }
})
</script>

<style scoped>
/* Component styles */
</style>

