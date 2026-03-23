<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        リード一覧（クーポン取得）
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        クーポン取得で登録されたメールアドレス一覧。CSVでダウンロードできます。
      </p>
    </div>

    <Loading v-if="isLoading" />

    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        type="button"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        @click="fetchLeads"
      >
        再試行
      </button>
    </div>

    <div v-else class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          合計 {{ total }} 件
        </p>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
          :disabled="isExporting"
          @click="handleExportCsv"
        >
          {{ isExporting ? 'ダウンロード中...' : 'CSVダウンロード' }}
        </button>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">お名前</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">メールアドレス</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">クーポン送信日時</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">登録日時</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="lead in leads"
                :key="lead.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/30"
              >
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                  {{ lead.guest_name || '—' }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                  {{ lead.email }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDateTime(lead.coupon_sent_at) }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDateTime(lead.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="leads.length === 0" class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
          まだリードはありません。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Loading from '@/components/common/Loading.vue'
import { leadsApi, type LeadItem } from '@/api/leads'

const isLoading = ref(false)
const isExporting = ref(false)
const error = ref<string | null>(null)
const leads = ref<LeadItem[]>([])
const total = ref(0)

function formatDateTime(iso: string | null): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    return d.toLocaleString('ja-JP')
  } catch {
    return iso
  }
}

async function fetchLeads() {
  try {
    isLoading.value = true
    error.value = null
    const res = await leadsApi.getLeads(0, 500)
    leads.value = res.leads
    total.value = res.total
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'リード一覧の取得に失敗しました'
  } finally {
    isLoading.value = false
  }
}

async function handleExportCsv() {
  try {
    isExporting.value = true
    const blob = await leadsApi.exportCsv()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `leads_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    alert(err.response?.data?.detail || 'CSVのダウンロードに失敗しました')
  } finally {
    isExporting.value = false
  }
}

onMounted(() => {
  fetchLeads()
})
</script>
