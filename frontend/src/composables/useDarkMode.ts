/**
 * ダークモードComposable
 */

import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

export function useDarkMode() {
  const themeStore = useThemeStore()

  const isDark = computed(() => themeStore.isDark)

  function toggle() {
    themeStore.toggleDark()
  }

  function setDark(dark: boolean) {
    themeStore.setDark(dark)
  }

  function init() {
    themeStore.initTheme()
  }

  return {
    isDark,
    toggle,
    setDark,
    init
  }
}

