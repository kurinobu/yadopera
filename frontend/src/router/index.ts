/**
 * Vue Router メイン設定
 * ゲスト側と管理画面のルートを統合
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { guestRoutes } from './guest'
import { adminRoutes } from './admin'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
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

