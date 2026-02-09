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
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            施設一覧
          </h2>
        </div>
        
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  施設名
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  状態
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  料金プラン
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
                  最終ログイン
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="facility in facilities" :key="facility.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {{ facility.name }}
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
                  {{ facility.faq_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.chats_7d }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.errors_7d }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ facility.last_admin_login ? formatDate(facility.last_admin_login) : '-' }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { developerApi } from '@/api/developer'
import type { SystemOverview, FacilitySummary, ErrorLog } from '@/types/developer'
import StatCard from '@/components/developer/StatCard.vue'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const overview = ref<SystemOverview | null>(null)
const facilities = ref<FacilitySummary[]>([])
const recentErrors = ref<ErrorLog[]>([])

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

