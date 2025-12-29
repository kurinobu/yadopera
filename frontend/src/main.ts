import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'

// アプリ起動時に動的manifestを初期化
// 初期状態では'/'をstart_urlに設定
// updateManifestLink(null)  // 削除: DOM ready後にApp.vueで実行

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初期化処理（すべて非同期で実行）
async function initializeApp() {
  try {
    const themeStore = useThemeStore()
    themeStore.initTheme()
  } catch (error) {
    console.error('Failed to initialize theme:', error)
    // エラーが発生してもアプリは起動する
  }

  try {
    const authStore = useAuthStore()
    await authStore.initAuth()
  } catch (error) {
    console.error('Failed to initialize auth:', error)
    // エラーが発生してもアプリは起動する
  }

  // すべての初期化処理が完了したら、アプリをマウント
  app.mount('#app')
}

// タイムアウトを設定し、一定時間経過後は強制的にアプリをマウント
const mountTimeout = setTimeout(() => {
  console.warn('App initialization timeout, mounting app anyway')
  app.mount('#app')
}, 2000) // 2秒後にタイムアウト

initializeApp()
  .then(() => {
    clearTimeout(mountTimeout)
  })
  .catch((error) => {
    clearTimeout(mountTimeout)
    console.error('Failed to initialize app:', error)
    // エラーが発生してもアプリは起動する
    app.mount('#app')
  })


