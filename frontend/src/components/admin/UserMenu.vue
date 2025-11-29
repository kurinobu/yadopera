<template>
  <div class="relative">
    <button
      @click="isOpen = !isOpen"
      class="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
    >
      <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold">
        {{ userInitial }}
      </div>
      <div class="text-left hidden md:block">
        <p class="text-sm font-medium text-gray-900 dark:text-white">
          {{ user?.full_name || 'User' }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ user?.email }}
        </p>
      </div>
      <svg
        class="w-4 h-4 text-gray-500 dark:text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- ドロップダウンメニュー -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        ref="menuRef"
        class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50"
      >
        <button
          @click="handleLogout"
          class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          ログアウト / Logout
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { user, logout } = useAuth()
const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

const userInitial = computed(() => {
  if (!user.value?.full_name) {
    return 'U'
  }
  return user.value.full_name.charAt(0).toUpperCase()
})

const handleLogout = async () => {
  isOpen.value = false
  await logout()
}

// クリックアウトサイド処理
const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Component styles */
</style>

