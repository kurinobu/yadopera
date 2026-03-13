<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        プラン・請求
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        料金プランの確認・変更、解約、請求履歴・領収書
      </p>
    </div>

    <Loading v-if="isLoading" />

    <div
      v-else-if="error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        type="button"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        @click="fetchAll"
      >
        再試行
      </button>
    </div>

    <template v-else>
      <!-- 現在のプラン・プラン一覧 -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          現在のプラン
        </h2>
        <p class="text-gray-700 dark:text-gray-300">
          <span class="font-medium">{{ currentPlanName }}</span>
          <span v-if="currentPlanType && currentPlanType !== 'Free'" class="ml-2 text-sm text-gray-500 dark:text-gray-400">
            （月額 {{ currentPlanPrice.toLocaleString() }} 円）
          </span>
        </p>
        <p v-if="!stripeConfigured" class="mt-2 text-sm text-amber-600 dark:text-amber-400">
          Stripe 未設定のため、プラン変更・解約は利用できません。
        </p>
      </div>

      <!-- プラン一覧・変更 -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          プラン一覧
        </h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">プラン</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">月額（税込）</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">月間質問数</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">FAQ数</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">言語数</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="plan in plans"
                :key="plan.plan_type"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/30"
              >
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                  {{ plan.name_ja }}
                  <span v-if="plan.plan_type === currentPlanType" class="ml-2 text-xs text-blue-600 dark:text-blue-400">（現在）</span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ plan.price_yen === 0 ? '無料' : `¥${plan.price_yen.toLocaleString()}` }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ plan.monthly_question_limit == null ? '従量' : plan.monthly_question_limit }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ plan.faq_limit == null ? '無制限' : plan.faq_limit }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ plan.language_limit == null ? '無制限' : plan.language_limit }}
                </td>
                <td class="px-4 py-3 text-sm">
                  <button
                    v-if="stripeConfigured && plan.plan_type !== currentPlanType"
                    type="button"
                    class="px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded"
                    @click="openPlanChangeModal(plan)"
                  >
                    プラン変更
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- プラン超過時の挙動（Free / Small / Standard / Premium のみ表示。Mini は非表示） -->
      <div
        v-if="showOverageBehaviorSection"
        class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
      >
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          プラン超過時の挙動
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          月間質問数がプラン上限を超えた場合の動作を選択します。
        </p>
        <div class="space-y-3">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="overageBehaviorSelection"
              type="radio"
              value="continue_billing"
              class="mt-1"
            />
            <span class="text-gray-700 dark:text-gray-300">
              <strong>通常継続（従量課金）</strong> — 超過分は ¥30/質問で請求し、AI応答を継続します。
            </span>
          </label>
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="overageBehaviorSelection"
              type="radio"
              value="faq_only"
              class="mt-1"
            />
            <span class="text-gray-700 dark:text-gray-300">
              <strong>AI停止・FAQのみ対応</strong> — 超過分は課金されず、FAQ検索結果のみで応答します。
            </span>
          </label>
        </div>
        <button
          type="button"
          class="mt-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isSavingOverage || overageBehaviorSelection === currentOverageBehavior"
          @click="saveOverageBehavior"
        >
          {{ isSavingOverage ? '保存中...' : '設定を保存' }}
        </button>
      </div>

      <!-- 解約（有料プランかつ Stripe 設定時のみ表示） -->
      <div
        v-if="stripeConfigured && currentPlanType && currentPlanType !== 'Free'"
        class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
      >
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          解約
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          サブスクリプションを解約すると、期間終了後に Free プランになります。
        </p>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500 rounded-lg transition-colors"
          @click="showCancelModal = true"
        >
          解約する
        </button>
      </div>

      <!-- 請求履歴・領収書 -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          請求履歴・領収書
        </h2>
        <div v-if="invoices.length === 0" class="py-6 text-center text-sm text-gray-500 dark:text-gray-400">
          請求履歴はありません。
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">請求日</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">金額</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ステータス</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="inv in invoices"
                :key="inv.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/30"
              >
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                  {{ formatInvoiceDate(inv.created) }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  ¥{{ (inv.amount_due / 100).toLocaleString() }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ inv.status || '—' }}
                </td>
                <td class="px-4 py-3 text-sm">
                  <button
                    type="button"
                    class="text-blue-600 dark:text-blue-400 hover:underline"
                    :disabled="receiptLoadingId === inv.id"
                    @click="openReceipt(inv.id)"
                  >
                    {{ receiptLoadingId === inv.id ? '取得中...' : '領収書を表示' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- プラン変更確認モーダル -->
    <Modal
      v-model="showPlanChangeModal"
      title="プラン変更の確認"
      size="md"
      @close="showPlanChangeModal = false"
    >
      <template v-if="targetPlan">
        <p class="text-gray-700 dark:text-gray-300">
          <strong>{{ targetPlan.name_ja }}</strong> に変更します。よろしいですか？
        </p>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          月額 {{ targetPlan.price_yen === 0 ? '無料' : `¥${targetPlan.price_yen.toLocaleString()}` }}
        </p>
      </template>
      <template #footer>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg"
          @click="showPlanChangeModal = false"
        >
          キャンセル
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isChangingPlan"
          @click="confirmPlanChange"
        >
          {{ isChangingPlan ? '変更中...' : '変更する' }}
        </button>
      </template>
    </Modal>

    <!-- 解約確認モーダル -->
    <Modal
      v-model="showCancelModal"
      title="解約の確認"
      size="md"
      @close="showCancelModal = false"
    >
      <p class="text-gray-700 dark:text-gray-300 mb-4">
        解約方法を選択してください。
      </p>
      <div class="space-y-2">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="cancelAtPeriodEnd" type="radio" :value="true" />
          <span>期間末で解約（現在の利用期間終了後に Free プランへ）</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="cancelAtPeriodEnd" type="radio" :value="false" />
          <span>即時解約</span>
        </label>
      </div>
      <template #footer>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg"
          @click="showCancelModal = false"
        >
          キャンセル
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isCancelling"
          @click="confirmCancel"
        >
          {{ isCancelling ? '処理中...' : '解約する' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Loading from '@/components/common/Loading.vue'
import Modal from '@/components/common/Modal.vue'
import { billingApi, type PlanInfo, type InvoiceItem } from '@/api/billing'
import { facilityApi } from '@/api/facility'

const isLoading = ref(false)
const error = ref<string | null>(null)
const currentPlanType = ref<string>('')
const plans = ref<PlanInfo[]>([])
const stripeConfigured = ref(false)
const currentOverageBehavior = ref<string>('continue_billing')
const overageBehaviorSelection = ref<string>('continue_billing')
const isSavingOverage = ref(false)
const invoices = ref<InvoiceItem[]>([])

const showPlanChangeModal = ref(false)
const targetPlan = ref<PlanInfo | null>(null)
const isChangingPlan = ref(false)

const showCancelModal = ref(false)
const cancelAtPeriodEnd = ref(true)
const isCancelling = ref(false)

const receiptLoadingId = ref<string | null>(null)

const currentPlanName = computed(() => {
  const p = plans.value.find(plan => plan.plan_type === currentPlanType.value)
  return p ? p.name_ja : currentPlanType.value || '—'
})

const currentPlanPrice = computed(() => {
  const p = plans.value.find(plan => plan.plan_type === currentPlanType.value)
  return p ? p.price_yen : 0
})

/** Free / Small / Standard / Premium のときのみ表示（Mini は上限なしのため非表示） */
const showOverageBehaviorSection = computed(() => {
  const t = currentPlanType.value
  return t === 'Free' || t === 'Small' || t === 'Standard' || t === 'Premium'
})

function formatInvoiceDate(created: number | null): string {
  if (created == null) return '—'
  try {
    return new Date(created * 1000).toLocaleDateString('ja-JP')
  } catch {
    return '—'
  }
}

async function fetchPlans() {
  const res = await billingApi.getPlans()
  currentPlanType.value = res.current_plan_type
  plans.value = res.plans
  stripeConfigured.value = res.stripe_configured
  const ob = res.current_overage_behavior ?? 'continue_billing'
  currentOverageBehavior.value = ob
  overageBehaviorSelection.value = ob
}

async function fetchInvoices() {
  const res = await billingApi.getInvoices()
  invoices.value = res.invoices
}

async function fetchAll() {
  try {
    isLoading.value = true
    error.value = null
    await Promise.all([fetchPlans(), fetchInvoices()])
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail
      || (err as { message?: string })?.message
      || 'プラン・請求情報の取得に失敗しました'
    error.value = typeof msg === 'string' ? msg : 'プラン・請求情報の取得に失敗しました'
  } finally {
    isLoading.value = false
  }
}

function openPlanChangeModal(plan: PlanInfo) {
  targetPlan.value = plan
  showPlanChangeModal.value = true
}

async function confirmPlanChange() {
  if (!targetPlan.value) return
  try {
    isChangingPlan.value = true
    await billingApi.changePlan(targetPlan.value.plan_type)
    showPlanChangeModal.value = false
    targetPlan.value = null
    await fetchAll()
    alert('プランを変更しました。')
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail
      || (err as { message?: string })?.message
      || 'プラン変更に失敗しました'
    alert(typeof msg === 'string' ? msg : 'プラン変更に失敗しました')
  } finally {
    isChangingPlan.value = false
  }
}

async function confirmCancel() {
  try {
    isCancelling.value = true
    await billingApi.cancelSubscription(cancelAtPeriodEnd.value)
    showCancelModal.value = false
    await fetchAll()
    alert('解約手続きが完了しました。')
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail
      || (err as { message?: string })?.message
      || '解約に失敗しました'
    alert(typeof msg === 'string' ? msg : '解約に失敗しました')
  } finally {
    isCancelling.value = false
  }
}

async function saveOverageBehavior() {
  try {
    isSavingOverage.value = true
    await facilityApi.updateFacilitySettings({ overage_behavior: overageBehaviorSelection.value as 'continue_billing' | 'faq_only' })
    currentOverageBehavior.value = overageBehaviorSelection.value
    alert('プラン超過時の挙動を保存しました。')
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail
      || (err as { message?: string })?.message
      || '保存に失敗しました'
    alert(typeof msg === 'string' ? msg : '保存に失敗しました')
  } finally {
    isSavingOverage.value = false
  }
}

async function openReceipt(invoiceId: string) {
  try {
    receiptLoadingId.value = invoiceId
    const res = await billingApi.getReceiptUrl(invoiceId)
    if (res.url) {
      window.open(res.url, '_blank', 'noopener,noreferrer')
    }
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail
      || (err as { message?: string })?.message
      || '領収書の取得に失敗しました'
    alert(typeof msg === 'string' ? msg : '領収書の取得に失敗しました')
  } finally {
    receiptLoadingId.value = null
  }
}

onMounted(() => {
  fetchAll()
})
</script>
