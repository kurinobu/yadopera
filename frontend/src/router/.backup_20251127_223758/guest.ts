/**
 * ゲスト側ルート定義
 */

import type { RouteRecordRaw } from 'vue-router'

export const guestRoutes: RouteRecordRaw[] = [
  {
    path: '/f/:facilityId',
    name: 'LanguageSelect',
    component: () => import('@/views/guest/LanguageSelect.vue'),
    meta: {
      layout: 'guest'
    }
  },
  {
    path: '/f/:facilityId/welcome',
    name: 'Welcome',
    component: () => import('@/views/guest/Welcome.vue'),
    meta: {
      layout: 'guest'
    }
  },
  {
    path: '/f/:facilityId/chat',
    name: 'Chat',
    component: () => import('@/views/guest/Chat.vue'),
    meta: {
      layout: 'guest'
    }
  }
]

