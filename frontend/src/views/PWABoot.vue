<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">読み込み中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { isValidFacilityId } from '@/utils/validators'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(() => {
  // 競合干渉対策1: 管理者が認証済みの場合は/admin/dashboardにリダイレクト
  if (authStore.isAuthenticated) {
    router.replace({ name: 'AdminDashboard' })
    return
  }
  
  // フォールバック: localStorageから取得してリダイレクト
  try {
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
          router.replace(lastFacilityUrl)
          return
        }
      }
    }
  } catch (error) {
    console.warn('[PWA] localStorageへのアクセスに失敗しました:', error)
  }
  
  // フォールバック: 現在のルートが/f/:facilityIdの場合、そのまま続行
  if (route.path.startsWith('/f/')) {
    const facilityId = route.params.facilityId as string
    if (isValidFacilityId(facilityId)) {
      // 既に正しいルートにいる場合、何もしない
      return
    }
  }
  
  // localStorageにlast_facility_urlが存在しない場合、404エラーページを表示
  // ゲストはQRコードで読み取った施設独自のURLにアクセスするべき
  router.replace({ name: 'NotFound' })
})
</script>

