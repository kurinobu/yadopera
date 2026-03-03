<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- ヘッダー -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            YadOPERA
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            新しいパスワードを設定 / Set New Password
          </p>
        </div>

        <!-- トークンなし・無効時 -->
        <div v-if="invalidToken" class="text-center space-y-6">
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <p class="text-red-800 dark:text-red-200">
              リンクが無効または期限切れです。再度リセット用メールを請求してください。
            </p>
            <p class="text-red-700 dark:text-red-300 text-sm mt-2">
              This link is invalid or has expired. Please request a new password reset email.
            </p>
          </div>
          <router-link
            to="/admin/password-reset"
            class="inline-block w-full py-2 px-4 text-center rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            パスワードリセットを請求
          </router-link>
          <router-link to="/admin/login" class="block text-sm text-blue-600 dark:text-blue-400 hover:underline mt-4">
            ログインに戻る
          </router-link>
        </div>

        <!-- 変更完了時 -->
        <div v-else-if="success" class="text-center space-y-6">
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
            <p class="text-green-800 dark:text-green-200">
              パスワードを変更しました。ログインしてください。
            </p>
            <p class="text-green-700 dark:text-green-300 text-sm mt-2">
              Password has been reset successfully. Please log in.
            </p>
          </div>
          <button
            type="button"
            @click="goToLogin"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            ログインページへ / Go to Login
          </button>
        </div>

        <!-- フォーム -->
        <form v-else @submit.prevent="handleSubmit" class="space-y-6">
          <Input
            v-model="newPassword"
            type="password"
            label="新しいパスワード / New Password"
            placeholder="8文字以上"
            :required="true"
            :error="errors.new_password"
          />
          <Input
            v-model="confirmPassword"
            type="password"
            label="新しいパスワード（確認） / Confirm Password"
            placeholder="同じパスワードを再入力"
            :required="true"
            :error="errors.confirm_password"
          />

          <div
            v-if="errorMessage"
            class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <p class="text-sm text-red-600 dark:text-red-400">
              {{ errorMessage }}
            </p>
          </div>

          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              変更中...
            </span>
            <span v-else>
              パスワードを変更
            </span>
          </button>

          <div class="text-center">
            <router-link to="/admin/login" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              ログインに戻る
            </router-link>
          </div>
        </form>

        <div class="mt-6 text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            © 2026 YadOPERA. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Input from '@/components/common/Input.vue'
import { authApi } from '@/api/auth'
import { isValidPassword } from '@/utils/validators'

const route = useRoute()
const router = useRouter()

const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const success = ref(false)
const invalidToken = ref(false)
const errorMessage = ref('')
const errors = ref<{ new_password?: string; confirm_password?: string }>({})

const isFormValid = computed(() => {
  return (
    newPassword.value.length >= 8 &&
    confirmPassword.value.length >= 8 &&
    newPassword.value === confirmPassword.value
  )
})

const goToLogin = () => {
  router.push('/admin/login')
}

const handleSubmit = async () => {
  errors.value = {}
  errorMessage.value = ''

  if (newPassword.value.length < 8) {
    errors.value.new_password = 'パスワードは8文字以上で入力してください'
    return
  }
  if (!isValidPassword(newPassword.value)) {
    errors.value.new_password = 'パスワードは8文字以上で入力してください'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errors.value.confirm_password = 'パスワードが一致しません'
    return
  }

  try {
    isLoading.value = true
    await authApi.confirmPasswordReset({
      token: token.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value
    })
    success.value = true
  } catch (err: any) {
    const status = err.response?.status
    const detail = err.response?.data?.detail
    if (status === 400) {
      invalidToken.value = true
      errorMessage.value = detail && typeof detail === 'string' ? detail : 'リンクが無効または期限切れです。'
    } else if (detail && typeof detail === 'string') {
      errorMessage.value = detail
    } else {
      errorMessage.value = 'パスワードの変更に失敗しました。しばらくしてから再度お試しください。'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const t = route.query.token as string
  if (!t || !t.trim()) {
    invalidToken.value = true
  } else {
    token.value = t.trim()
  }
})
</script>
