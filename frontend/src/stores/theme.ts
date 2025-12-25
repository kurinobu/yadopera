/**
 * ダークモード状態管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

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
    try {
      // システム設定を確認（互換性チェックを追加）
      let prefersDark = false
      if (typeof window !== 'undefined' && window.matchMedia) {
        try {
          prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        } catch (error) {
          console.warn('matchMedia not supported, using light theme:', error)
        }
      }
      
      const storedTheme = localStorage.getItem('theme')
      
      if (storedTheme) {
        isDark.value = storedTheme === 'dark'
      } else {
        isDark.value = prefersDark
      }
      
      updateTheme()
    } catch (error) {
      // localStorageが利用できない場合（プライベートモードなど）、デフォルト設定を使用
      console.warn('Failed to access localStorage, using default theme:', error)
      let prefersDark = false
      if (typeof window !== 'undefined' && window.matchMedia) {
        try {
          prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        } catch (error) {
          console.warn('matchMedia not supported, using light theme:', error)
        }
      }
      isDark.value = prefersDark
      // updateTheme()は呼び出さない（localStorageにアクセスするため）
      if (isDark.value) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  function updateTheme() {
    try {
      if (isDark.value) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    } catch (error) {
      // localStorageが利用できない場合、クラスのみ更新
      console.warn('Failed to save theme to localStorage:', error)
      if (isDark.value) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  // システム設定の変更を監視（互換性チェックを追加）
  if (typeof window !== 'undefined' && window.matchMedia) {
    try {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        try {
          if (!localStorage.getItem('theme')) {
            setDark(e.matches)
          }
        } catch (error) {
          console.warn('Failed to update theme:', error)
        }
      })
    } catch (error) {
      console.warn('Failed to setup theme listener:', error)
    }
  }

  return {
    isDark,
    toggleDark,
    setDark,
    initTheme
  }
})


