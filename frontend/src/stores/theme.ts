/**
 * ダークモード状態管理
 */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // State
  const isDark = ref<boolean>(false)

  // Actions
  function toggleDark() {
    isDark.value = !isDark.value
    updateTheme()
  }

  function setDark(dark: boolean) {
    isDark.value = dark
    updateTheme()
  }

  function initTheme() {
    // システム設定を確認
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const storedTheme = localStorage.getItem('theme')
    
    if (storedTheme) {
      isDark.value = storedTheme === 'dark'
    } else {
      isDark.value = prefersDark
    }
    
    updateTheme()
  }

  function updateTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  // システム設定の変更を監視
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        setDark(e.matches)
      }
    })
  }

  return {
    isDark,
    toggleDark,
    setDark,
    initTheme
  }
})


