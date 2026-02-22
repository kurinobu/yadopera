<template>
  <div
    v-if="showFooter"
    class="fixed bottom-0 left-0 right-0 z-30 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 safe-area-pb"
  >
    <div class="overflow-x-auto scrollbar-hide">
      <div class="flex gap-3 px-4 py-3 min-w-max">
        <!-- クーポンCTA（有効時のみ） -->
        <button
          v-if="showCoupon"
          type="button"
          class="flex-shrink-0 px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-colors"
          @click="openCouponModal"
        >
          🎁 {{ copy.couponButton }}
        </button>
        <!-- 後続オプション（延長・延泊等）はここに同じ並びで追加し、横幅不足時は横スライド -->
      </div>
    </div>
    <CouponEntryModal
      :is-open="couponModalOpen"
      :facility-slug="facilitySlug"
      :facility-name="facilityName"
      :lang="lang"
      @update:is-open="couponModalOpen = $event"
      @success="onCouponSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CouponEntryModal from './CouponEntryModal.vue'
import { getCouponCopy } from '@/utils/couponCopy'
import type { Facility } from '@/types/facility'

const props = withDefaults(
  defineProps<{
    facility: Facility | null
    facilitySlug: string
    /** ゲストが選択した言語（クーポンボタン・モーダル表示に使用） */
    lang?: string
  }>(),
  { lang: 'en' }
)

const couponModalOpen = ref(false)

const showCoupon = computed(() => {
  return props.facility?.coupon?.enabled === true
})

const showFooter = computed(() => {
  return showCoupon.value
})

const facilityName = computed(() => props.facility?.name ?? '')
const copy = computed(() => getCouponCopy(props.lang ?? 'en'))

function openCouponModal() {
  couponModalOpen.value = true
}

function onCouponSuccess() {
  // 必要ならトースト等を表示
}
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
/* スマホのセーフエリア（ホームインジケータ）対応 */
.safe-area-pb {
  padding-bottom: env(safe-area-inset-bottom, 0);
}
</style>
