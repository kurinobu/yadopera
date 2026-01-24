/**
 * Vue Router メイン設定
 * ゲスト側と管理画面のルートを統合
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { guestRoutes } from './guest'
import { adminRoutes } from './admin'
import { developerRoutes } from './developer'
import { useAuthStore } from '@/stores/auth'
import { useDeveloperStore } from '@/stores/developer'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'PWABoot',
    component: () => import('@/views/PWABoot.vue'),
    meta: {
      layout: undefined
    }
  },
  ...guestRoutes,
  ...adminRoutes,
  ...developerRoutes,
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
  const developerStore = useDeveloperStore()
  
  // 開発者ページの認証チェック
  const requiresDeveloperAuth = to.matched.some(record => record.meta.requiresDeveloperAuth)
  if (requiresDeveloperAuth) {
    try {
      // 開発者ストアを初期化
      developerStore.initAuth()
      
      if (!developerStore.isAuthenticated) {
        // 開発者認証が必要なページに未認証でアクセスした場合
        console.info('Developer authentication required, redirecting to login')
        return next({
          name: 'DeveloperLogin',
          query: { redirect: to.fullPath }
        })
      }
      
      // 開発者ログインページで既に認証済みの場合
      if (to.name === 'DeveloperLogin' && developerStore.isAuthenticated) {
        console.info('Developer already authenticated, redirecting to dashboard')
        return next({ name: 'DeveloperDashboard' })
      }
      
      // 開発者ページの場合は、通常の認証チェックをスキップ
      return next()
    } catch (error) {
      // 開発者認証処理でエラーが発生した場合
      console.error('Error in developer authentication guard:', error)
      
      // エラーが発生した場合はログインページにリダイレクト
      return next({
        name: 'DeveloperLogin',
        query: { redirect: to.fullPath, error: 'auth_error' }
      })
    }
  }
  
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

// グローバルナビゲーションエラーハンドラー
router.onError((error) => {
  console.error('Vue Router navigation error:', error)
  
  // ルートが見つからないエラーの場合
  if (error.message.includes('No match')) {
    console.warn('Route not found, redirecting to appropriate fallback')
    
    // 開発者ページでエラーが発生した場合はダッシュボードにリダイレクト
    if (window.location.pathname.startsWith('/developer')) {
      router.push('/developer/dashboard').catch(fallbackError => {
        console.error('Fallback navigation failed:', fallbackError)
        // 最終的なフォールバック：ログインページ
        window.location.href = '/developer/login'
      })
    } else {
      // その他の場合は404ページ
      router.push('/404').catch(fallbackError => {
        console.error('404 navigation failed:', fallbackError)
      })
    }
  }
})

// ナビゲーション後のエラーハンドラー
router.afterEach((to, from, failure) => {
  if (failure) {
    console.warn('Navigation cancelled or failed:', failure)
    
    // 開発者ページでナビゲーション失敗した場合の処理
    if (to.path.startsWith('/developer') && failure.type === 4 /* NavigationFailureType.aborted */) {
      console.info('Developer navigation aborted, attempting fallback')
      
      // ダッシュボードへのフォールバック
      setTimeout(() => {
        router.push('/developer/dashboard').catch(error => {
          console.error('Fallback navigation error:', error)
        })
      }, 100)
    }
  }
})

export default router

