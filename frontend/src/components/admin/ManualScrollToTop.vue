<template>
  <Teleport to="body">
    <Transition name="fade">
      <button
        v-show="visible"
        type="button"
        class="fixed bottom-6 left-6 z-50 group"
        aria-label="トップへ戻る"
        title="トップへ戻る"
        @click="scrollToTop"
      >
        <div
          class="
            flex items-center justify-center
            w-14 h-14 rounded-full
            bg-gray-600 hover:bg-gray-700
            dark:bg-gray-600 dark:hover:bg-gray-500
            text-white shadow-lg hover:shadow-xl
            transition-all duration-200
            group-hover:scale-110
          "
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </svg>
        </div>
      </button>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const SCROLL_THRESHOLD_PX = 300

const visible = ref(false)

let scrollContainer: HTMLElement | Window | null = null

function getScrollContainer(): HTMLElement | Window {
  const el = document.querySelector<HTMLElement>('[data-admin-main]')
  return el ?? window
}

function getScrollTop(): number {
  if (!scrollContainer) return 0
  if (scrollContainer === window) {
    return window.scrollY ?? document.documentElement.scrollTop
  }
  return (scrollContainer as HTMLElement).scrollTop
}

function updateVisible(): void {
  visible.value = getScrollTop() >= SCROLL_THRESHOLD_PX
}

function scrollToTop(): void {
  if (!scrollContainer) return
  if (scrollContainer === window) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    ;(scrollContainer as HTMLElement).scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function onScroll(): void {
  updateVisible()
}

onMounted(() => {
  scrollContainer = getScrollContainer()
  updateVisible()
  if (scrollContainer === window) {
    window.addEventListener('scroll', onScroll, { passive: true })
  } else {
    ;(scrollContainer as HTMLElement).addEventListener('scroll', onScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (scrollContainer === window) {
    window.removeEventListener('scroll', onScroll)
  } else if (scrollContainer) {
    ;(scrollContainer as HTMLElement).removeEventListener('scroll', onScroll)
  }
  scrollContainer = null
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
