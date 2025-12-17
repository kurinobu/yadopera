import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初期化処理（エラーハンドリングを追加）
try {
  const themeStore = useThemeStore()
  themeStore.initTheme()
} catch (error) {
  console.error('Failed to initialize theme:', error)
  // エラーが発生してもアプリは起動する
}

const authStore = useAuthStore()
// 認証初期化（非同期処理）
authStore.initAuth().then(() => {
  app.mount('#app')
}).catch((error) => {
  console.error('Failed to initialize auth:', error)
  // エラーが発生してもアプリは起動する
  app.mount('#app')
})


