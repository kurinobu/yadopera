<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        開発者管理ダッシュボード
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        システム全体の統計とエラーログ
      </p>
    </div>

    <!-- ローディング表示 -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">読み込み中...</p>
    </div>

    <!-- エラー表示 -->
    <div
      v-else-if="error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchData"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- ダッシュボードコンテンツ -->
    <template v-else>
      <!-- システム概要統計 -->
      <section v-if="overview" class="space-y-6">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            システム概要
          </h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="総施設数"
            :value="overview.total_facilities"
            :subtitle="overview.active_facilities != null ? `アクティブ: ${overview.active_facilities}` : ''"
          />
          <StatCard
            title="総FAQ数"
            :value="overview.total_faqs"
          />
          <StatCard
            title="過去7日のチャット数"
            :value="overview.chats_7d"
          />
          <StatCard
            title="過去7日のエスカレーション数"
            :value="overview.escalations_7d"
          />
        </div>

        <!-- 運営用統計（当月・暦月 JST） -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="有料施設数"
            :value="overview.paid_facilities_count ?? 0"
          />
          <StatCard
            title="今月の総質問数"
            :value="overview.questions_current_month ?? 0"
            subtitle="当月"
          />
          <StatCard
            title="今月の新規登録数"
            :value="overview.new_registrations_current_month ?? 0"
            subtitle="当月"
          />
          <StatCard
            title="今月の新規有料数"
            :value="overview.new_paid_current_month ?? 0"
            subtitle="当月登録かつ有料"
          />
          <StatCard
            title="解約予定施設数"
            :value="overview.cancel_at_period_end_count ?? 0"
            subtitle="期間末解約予定"
          />
        </div>

        <!-- エラー統計（過去24時間） -->
        <div v-if="overview.errors_24h" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Critical エラー"
            :value="overview.errors_24h.critical"
            subtitle="過去24時間"
          />
          <StatCard
            title="Error"
            :value="overview.errors_24h.error"
            subtitle="過去24時間"
          />
          <StatCard
            title="Warning"
            :value="overview.errors_24h.warning"
            subtitle="過去24時間"
          />
        </div>
      </section>

      <!-- 施設一覧 -->
      <section v-if="facilities.length > 0" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            施設一覧
          </h2>
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isExporting"
            @click="handleExportFacilitiesCsv"
          >
            {{ isExporting ? 'ダウンロード中...' : 'CSVダウンロード' }}
          </button>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  施設ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  施設名
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  メールアドレス
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  状態
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  料金プラン
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  登録日
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  今月の質問数
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  FAQ数
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  チャット（7日）
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  エラー（7日）
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  エスカレーション（7日）
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  最終ログイン
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="facility in facilities" :key="facility.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {{ facility.name }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.email || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span
                    :class="facility.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'"
                    class="px-2 py-1 rounded text-xs font-medium"
                  >
                    {{ facility.is_active ? 'アクティブ' : '非アクティブ' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.plan_type || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.created_at ? formatDate(facility.created_at) : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.questions_current_month ?? 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.faq_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.chats_7d }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.errors_7d }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.escalations_7d ?? 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.last_admin_login ? formatDate(facility.last_admin_login) : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    type="button"
                    class="px-3 py-2 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    @click="openCsvUploadModal(facility)"
                  >
                    CSV一括登録（FAQ）
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </section>

      <!-- エラーログ一覧（最新10件） -->
      <section v-if="recentErrors.length > 0" class="space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            最新エラーログ
          </h2>
          <router-link
            :to="{ name: 'DeveloperErrorLogs' }"
            class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            すべて見る →
          </router-link>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  レベル
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  コード
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  メッセージ
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  施設
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  発生時刻
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="error in recentErrors"
                :key="error.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                @click="viewErrorDetail(error.id)"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span
                    :class="{
                      'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': error.level === 'critical',
                      'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400': error.level === 'error',
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': error.level === 'warning'
                    }"
                    class="px-2 py-1 rounded text-xs font-medium"
                  >
                    {{ error.level.toUpperCase() }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500 dark:text-gray-400">
                  {{ error.code }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-white max-w-md truncate">
                  {{ error.message }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ error.facility_name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(error.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- CSV一括登録モーダル -->
    <div
      v-if="isCsvModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      @click.self="closeCsvUploadModal"
    >
      <div class="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-800 shadow-xl border border-gray-200 dark:border-gray-700">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">FAQ CSV 一括登録</h3>
          <button
            type="button"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            @click="closeCsvUploadModal"
          >
            ✕
          </button>
        </div>

        <div v-if="selectedFacility" class="px-6 py-5 space-y-4">
          <div class="rounded-lg border border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20 p-3 text-sm text-yellow-900 dark:text-yellow-100">
            誤登録防止のため、対象施設を確認してください。
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div><span class="font-semibold">施設ID:</span> {{ selectedFacility.id }}</div>
            <div><span class="font-semibold">施設名:</span> {{ selectedFacility.name }}</div>
            <div><span class="font-semibold">プラン:</span> {{ selectedFacility.plan_type || '-' }}</div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              CSVファイル
            </label>
            <input
              type="file"
              accept=".csv,text/csv"
              class="block w-full text-sm text-gray-700 dark:text-gray-300 file:mr-3 file:rounded file:border-0 file:bg-gray-100 file:px-3 file:py-2 file:text-sm file:font-medium hover:file:bg-gray-200 dark:file:bg-gray-700 dark:hover:file:bg-gray-600"
              @change="handleCsvFileChange"
            />
            <p v-if="selectedCsvFile" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              選択中: {{ selectedCsvFile.name }}
            </p>
          </div>

          <label class="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              v-model="csvConfirmChecked"
              type="checkbox"
              class="mt-1"
            />
            <span>対象施設・CSV内容を確認し、実行して問題ないことを確認しました。</span>
          </label>

          <p v-if="csvUploadError" class="text-sm text-red-600 dark:text-red-400">
            {{ csvUploadError }}
          </p>

          <div v-if="csvUploadResult" class="rounded-lg border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20 p-3 text-sm text-green-900 dark:text-green-100 space-y-1">
            <p>アップロード完了</p>
            <p>成功件数: {{ csvUploadResult.success_count }} / 総件数: {{ csvUploadResult.total_count }}</p>
            <p>処理時間: {{ csvUploadResult.processing_time_seconds }}秒</p>
            <p>uploaded_by: {{ csvUploadResult.uploaded_by }}</p>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-2">
          <button
            type="button"
            class="px-4 py-2 text-sm rounded border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
            :disabled="isCsvUploading"
            @click="closeCsvUploadModal"
          >
            閉じる
          </button>
          <button
            type="button"
            class="px-4 py-2 text-sm rounded text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isCsvUploading || !selectedCsvFile || !csvConfirmChecked"
            @click="submitCsvUpload"
          >
            {{ isCsvUploading ? '実行中...' : 'CSV一括登録を実行' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { developerApi } from '@/api/developer'
import type {
  SystemOverview,
  FacilitySummary,
  ErrorLog,
  DeveloperFaqBulkUploadResult
} from '@/types/developer'
import StatCard from '@/components/developer/StatCard.vue'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const isExporting = ref(false)
const overview = ref<SystemOverview | null>(null)
const facilities = ref<FacilitySummary[]>([])
const recentErrors = ref<ErrorLog[]>([])
const isCsvModalOpen = ref(false)
const isCsvUploading = ref(false)
const selectedFacility = ref<FacilitySummary | null>(null)
const selectedCsvFile = ref<File | null>(null)
const csvConfirmChecked = ref(false)
const csvUploadError = ref('')
const csvUploadResult = ref<DeveloperFaqBulkUploadResult | null>(null)

const fetchData = async () => {
  try {
    loading.value = true
    error.value = ''

    // 並列でデータ取得
    const [overviewData, facilitiesData, errorsData] = await Promise.all([
      developerApi.getOverview(),
      developerApi.getFacilities(),
      developerApi.getErrors({ page: 1, per_page: 10 })
    ])

    overview.value = overviewData
    facilities.value = facilitiesData.facilities
    recentErrors.value = errorsData.errors
  } catch (err: any) {
    error.value = err.message || 'データの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const viewErrorDetail = (errorId: number) => {
  router.push({ name: 'DeveloperErrorLogDetail', params: { errorId } })
}

const handleExportFacilitiesCsv = async () => {
  try {
    isExporting.value = true
    const blob = await developerApi.exportFacilitiesCsv()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `facilities_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    alert(err.response?.data?.detail || err.message || 'CSVのダウンロードに失敗しました')
  } finally {
    isExporting.value = false
  }
}

const openCsvUploadModal = (facility: FacilitySummary) => {
  selectedFacility.value = facility
  selectedCsvFile.value = null
  csvConfirmChecked.value = false
  csvUploadError.value = ''
  csvUploadResult.value = null
  isCsvModalOpen.value = true
}

const closeCsvUploadModal = () => {
  if (isCsvUploading.value) return
  isCsvModalOpen.value = false
}

const handleCsvFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedCsvFile.value = target.files?.[0] || null
  csvUploadError.value = ''
}

const submitCsvUpload = async () => {
  if (!selectedFacility.value || !selectedCsvFile.value) return
  if (!csvConfirmChecked.value) {
    csvUploadError.value = '確認チェックに同意してください。'
    return
  }

  try {
    isCsvUploading.value = true
    csvUploadError.value = ''
    const result = await developerApi.bulkUploadFaqCsv(
      selectedFacility.value.id,
      selectedCsvFile.value,
      'add'
    )
    csvUploadResult.value = result
    await fetchData()
  } catch (err: any) {
    csvUploadError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      err.message ||
      'CSV一括登録に失敗しました'
  } finally {
    isCsvUploading.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* Component styles */
</style>

