<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 p-4"
      @click.self="handleBackdropClick"
    >
      <div
        class="w-full max-w-md rounded-t-2xl sm:rounded-2xl bg-white dark:bg-gray-800 shadow-xl max-h-[90vh] overflow-y-auto"
        role="dialog"
        aria-labelledby="coupon-modal-title"
      >
        <div class="p-6">
          <h2 id="coupon-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {{ copy.modalTitle }}
          </h2>

          <!-- 完了表示 -->
          <div v-if="success" class="text-center py-4">
            <p class="text-green-600 dark:text-green-400 font-medium mb-4">
              {{ successMessage }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
              {{ copy.successDescription }}
            </p>
            <button
              type="button"
              class="w-full px-4 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              @click="close"
            >
              {{ copy.closeButton }}
            </button>
          </div>

          <!-- フォーム -->
          <template v-else>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ copy.introText }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500 mb-4">
              {{ copy.privacyNote }}
            </p>

            <form @submit.prevent="submit" class="space-y-4">
              <div>
                <label for="coupon-guest-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ copy.labelName }}
                </label>
                <input
                  id="coupon-guest-name"
                  v-model="guestName"
                  type="text"
                  class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  :placeholder="copy.placeholderName"
                />
              </div>
              <div>
                <label for="coupon-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ copy.labelEmail }} <span class="text-red-500">*</span>
                </label>
                <input
                  id="coupon-email"
                  v-model="email"
                  type="email"
                  required
                  class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  :placeholder="copy.placeholderEmail"
                />
              </div>
              <p v-if="error" class="text-sm text-red-600 dark:text-red-400">
                {{ error }}
              </p>
              <div class="flex gap-3 pt-2">
                <button
                  type="button"
                  class="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400"
                  :disabled="isSubmitting"
                  @click="close"
                >
                  {{ copy.cancelButton }}
                </button>
                <button
                  type="submit"
                  class="flex-1 px-4 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="isSubmitting || !email"
                >
                  {{ isSubmitting ? copy.submittingButton : copy.submitButton }}
                </button>
              </div>
            </form>
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { facilityApi } from '@/api/facility'
import { getCouponCopy } from '@/utils/couponCopy'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    facilitySlug: string
    facilityName?: string
    /** ゲストが選択した言語（表示文言に使用） */
    lang?: string
  }>(),
  { facilityName: '', lang: 'en' }
)

const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void
  (e: 'success'): void
}>()

const copy = computed(() => getCouponCopy(props.lang ?? 'en'))

const guestName = ref('')
const email = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const successMessage = ref('')

function close() {
  emit('update:isOpen', false)
}

function handleBackdropClick() {
  if (!isSubmitting.value) close()
}

async function submit() {
  if (!props.facilitySlug || !email.value) return
  error.value = null
  isSubmitting.value = true
  try {
    await facilityApi.submitLeadEntry(props.facilitySlug, {
      guest_name: guestName.value || undefined,
      email: email.value.trim()
    })
    success.value = true
    successMessage.value = copy.value.successTitle
    emit('success')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : copy.value.errorSendFailed
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (!open) {
      guestName.value = ''
      email.value = ''
      error.value = null
      success.value = false
    }
  }
)
</script>
