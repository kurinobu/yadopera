/**
 * Vue Router メイン設定
 * ゲスト側と管理画面のルートを統合
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { guestRoutes } from './guest'
import { adminRoutes } from './admin'
import { useAuthStore } from '@/stores/auth'
import { isValidFacilityId } from '@/utils/validators'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Root',
    component: () => import('@/views/Error404.vue'), // ダミーコンポーネント（beforeEnterでリダイレクトされるため実行されない）
    beforeEnter: (_to, _from, next) => {
      try {
        // 最後にアクセスした施設URLをlocalStorageから取得
        const lastFacilityUrl = localStorage.getItem('last_facility_url')
        
        if (lastFacilityUrl) {
          // ホワイトリスト方式: ゲスト側のルート（/f/:facilityId）のみ許可
          const allowedPattern = /^\/f\/([^\/]+)(\/.*)?$/
          const match = lastFacilityUrl.match(allowedPattern)
          
          if (match) {
            const facilityId = match[1]
            
            // 施設IDの検証
            if (isValidFacilityId(facilityId)) {
              // ゲスト側のルートのみリダイレクト
              next(lastFacilityUrl)
            } else {
              // 不正な施設IDの場合は404エラーページを表示
              console.error('PWA起動時: 不正な施設IDが検出されました。', facilityId)
              next({ name: 'NotFound' })
            }
          } else {
            // 許可されていないURLの場合は404エラーページを表示
            console.error('PWA起動時: 許可されていないURLが検出されました。', lastFacilityUrl)
            next({ name: 'NotFound' })
          }
        } else {
          // 施設URLがない場合は想定外のエラー（この状況は発生してはいけない）
          // ただし、万が一の場合に備えて404エラーページを表示
          console.error('PWA起動時: 施設URLが保存されていません。これは想定外の状況です。')
          next({ name: 'NotFound' })
        }
      } catch (error) {
        // localStorageが利用できない場合、404エラーページを表示
        console.warn('Failed to access localStorage:', error)
        next({ name: 'NotFound' })
      }
    },
    meta: {
      layout: undefined
    }
  },
  ...guestRoutes,
  ...adminRoutes,
  {
    path: '/500',
    name: 'Error500',
    component: () => import('@/views/Error500.vue'),
    meta: {
      layout: undefined
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Error404.vue'),
    meta: {
      layout: undefined
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 認証ガード
router.beforeEach(async (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  
  // ゲスト側のルート（/f/:facilityId）にアクセスした際、localStorageに施設URLを保存
  // 常に最新の施設URLを保持する（PWAインストール時にも確実に保存される）
  if (to.path.startsWith('/f/')) {
    try {
      const facilityUrl = to.fullPath
      localStorage.setItem('last_facility_url', facilityUrl)
    } catch (error) {
      // localStorageが利用できない場合（プライベートモードなど）、エラーを無視
      console.warn('Failed to save facility URL to localStorage:', error)
    }
  }
  
  // トークンが存在するが、ユーザー情報が取得されていない場合、取得を試みる
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initAuth()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      // エラーが発生した場合、ログアウト
      authStore.logout()
      
      // logout後、認証が必要なページへのアクセスなら即座にリダイレクト
      const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
      if (requiresAuth) {
        return next({
          name: 'AdminLogin',
          query: { redirect: to.fullPath }
        })
      }
      // 認証が不要なページの場合は、そのまま続行
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 認証が必要なページに未認証でアクセスした場合
    return next({
      name: 'AdminLogin',
      query: { redirect: to.fullPath }
    })
  }
  
  // ログインページで既に認証済みの場合
  if (to.name === 'AdminLogin' && authStore.isAuthenticated) {
    return next({ name: 'AdminDashboard' })
  }
  
  // その他は通常通り遷移
  next()
})

export default router

