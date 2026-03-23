/**
 * 開発者管理ページルート定義
 */

import type { RouteRecordRaw } from 'vue-router'

export const developerRoutes: RouteRecordRaw[] = [
  {
    path: '/developer/login',
    name: 'DeveloperLogin',
    component: () => import('@/views/developer/DeveloperLogin.vue'),
    meta: {
      layout: undefined,
      requiresDeveloperAuth: false
    }
  },
  {
    path: '/developer',
    redirect: '/developer/dashboard',
    meta: {
      requiresDeveloperAuth: true
    }
  },
  {
    path: '/developer/dashboard',
    name: 'DeveloperDashboard',
    component: () => import('@/views/developer/DeveloperDashboard.vue'),
    meta: {
      layout: 'developer',  // DeveloperLayoutを使用
      requiresDeveloperAuth: true
    }
  },
  {
    path: '/developer/errors',
    name: 'DeveloperErrorLogs',
    component: () => import('@/views/developer/ErrorLogs.vue'),
    meta: {
      layout: 'developer',
      requiresDeveloperAuth: true
    }
  },
  {
    path: '/developer/errors/:errorId',
    name: 'DeveloperErrorLogDetail',
    component: () => import('@/views/developer/ErrorLogDetail.vue'),
    meta: {
      layout: 'developer',
      requiresDeveloperAuth: true
    }
  },
  {
    path: '/developer/health',
    name: 'DeveloperSystemHealth',
    component: () => import('@/views/developer/SystemHealth.vue'),
    meta: {
      layout: 'developer',
      requiresDeveloperAuth: true
    }
  }
]

