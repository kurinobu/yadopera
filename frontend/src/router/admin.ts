/**
 * 管理画面ルート定義
 */

import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/Login.vue'),
    meta: {
      layout: undefined,
      requiresAuth: false
    }
  },
  {
    path: '/admin/register',
    name: 'Register',
    component: () => import('@/views/admin/Register.vue'),
    meta: {
      layout: undefined,
      requiresAuth: false
    }
  },
  {
    path: '/admin/verify-email-pending',
    name: 'EmailVerificationPending',
    component: () => import('@/views/admin/EmailVerificationPending.vue'),
    meta: {
      layout: undefined,
      requiresAuth: false
    }
  },
  {
    path: '/admin/verify-email',
    name: 'EmailVerificationSuccess',
    component: () => import('@/views/admin/EmailVerificationSuccess.vue'),
    meta: {
      layout: undefined,
      requiresAuth: false
    }
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard',
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/faqs',
    name: 'AdminFaqs',
    component: () => import('@/views/admin/FaqManagement.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/overnight-queue',
    name: 'AdminOvernightQueue',
    component: () => import('@/views/admin/OvernightQueue.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/qr-code',
    name: 'AdminQRCode',
    component: () => import('@/views/admin/QRCodeGenerator.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/manual',
    name: 'AdminManual',
    component: () => import('@/views/admin/Manual.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/conversations/:session_id',
    name: 'ConversationDetail',
    component: () => import('@/views/admin/ConversationDetail.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/facility/settings',
    name: 'FacilitySettings',
    component: () => import('@/views/admin/FacilitySettings.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  },
  {
    path: '/admin/support',
    name: 'AdminSupport',
    component: () => import('@/views/admin/Support.vue'),
    meta: {
      layout: 'admin',
      requiresAuth: true
    }
  }
]

