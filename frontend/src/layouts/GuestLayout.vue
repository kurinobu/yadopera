<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900" :class="{ 'pb-16': showOptionFooter }">
    <!-- ダークモード切替ボタン（右上固定、Chat画面以外で表示） -->
    <div v-if="showGlobalDarkModeToggle" class="fixed top-4 right-4 z-40">
      <DarkModeToggle />
    </div>

    <!-- メインコンテンツ -->
    <slot />

    <!-- オプション用固定フッター（クーポン・延長・延泊等、横スライド対応） -->
    <GuestOptionFooter
      v-if="facilityId"
      :facility="facility"
      :facility-slug="facilityId"
      :lang="guestLang"
    />

    <!-- PWAインストールプロンプト -->
    <PWAInstallPrompt />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DarkModeToggle from '@/components/common/DarkModeToggle.vue'
import PWAInstallPrompt from '@/components/common/PWAInstallPrompt.vue'
import GuestOptionFooter from '@/components/guest/GuestOptionFooter.vue'
import { useFacilityStore } from '@/stores/facility'
import { updateManifestLink } from '@/utils/manifestGenerator'

const route = useRoute()
const facilityStore = useFacilityStore()

const facilityId = computed(() => route.params.facilityId as string)
const facility = computed(() => facilityStore.currentFacility)
const showOptionFooter = computed(() => !!facility.value?.coupon?.enabled)
/** ゲストが選択した言語（固定フッター・モーダルの表示言語に使用） */
const guestLang = computed(() => (route.query.lang as string) || 'en')

// Chat画面ではヘッダー内にダークモード切り替えボタンがあるため、固定ボタンを非表示にする
const showGlobalDarkModeToggle = computed(() => {
  return route.name !== 'Chat'
})

// ゲスト側のルートにアクセスした際、manifestを自動更新（Safari iOS対応）
onMounted(() => {
  if (route.path.startsWith('/f/')) {
    const id = route.params.facilityId as string
    updateManifestLink(id)
  }
})
</script>

<style scoped>
/* Component styles */
</style>

