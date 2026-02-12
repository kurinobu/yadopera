<template>
  <div class="space-y-4">
    <!-- テンプレートダウンロード -->
    <div
      v-if="!result && !uploadError"
      class="rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 p-3"
    >
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">
        推奨テンプレート（日本語・英語・フランス語・繁体中国語）をダウンロードして編集し、アップロードにご利用ください。
      </p>
      <a
        href="/faq-csv-template/FAQ_CSV_template_4lang.csv"
        download="FAQ_CSV_template_4lang.csv"
        class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline"
      >
        CSVテンプレートをダウンロード
      </a>
    </div>

    <!-- ファイル選択 -->
    <div
      v-if="!result && !uploadError"
      class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center transition-colors"
      :class="{ 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/10': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".csv"
        class="hidden"
        @change="onFileSelect"
      />
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
        CSVファイルをドラッグ＆ドロップするか、下のボタンで選択してください
      </p>
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
        @click="fileInputRef?.click()"
      >
        ファイルを選択
      </button>
      <p v-if="selectedFile" class="mt-2 text-sm text-gray-700 dark:text-gray-300">
        選択中: {{ selectedFile.name }}（{{ formatSize(selectedFile.size) }}）
      </p>
    </div>

    <!-- 送信中 -->
    <div v-if="uploading" class="space-y-2">
      <p class="text-sm text-gray-700 dark:text-gray-300">アップロード中...</p>
      <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden">
        <div
          class="h-full bg-blue-600 dark:bg-blue-500 transition-all duration-300"
          :style="{ width: `${uploadProgress}%` }"
        />
      </div>
    </div>

    <!-- 成功結果 -->
    <div
      v-if="result"
      class="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-4"
    >
      <p class="font-medium text-green-800 dark:text-green-200">アップロードが完了しました</p>
      <ul class="mt-2 text-sm text-green-700 dark:text-green-300 space-y-1">
        <li>成功: {{ result.success_count }} 件</li>
        <li>処理時間: {{ result.processing_time_seconds }} 秒</li>
      </ul>
    </div>

    <!-- エラー -->
    <div
      v-if="uploadError"
      class="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4"
    >
      <p class="font-medium text-red-800 dark:text-red-200">アップロードに失敗しました</p>
      <p class="mt-1 text-sm text-red-700 dark:text-red-300">{{ uploadError }}</p>
    </div>

    <!-- フッター -->
    <div class="flex justify-end gap-2 pt-2">
      <button
        v-if="result || uploadError"
        type="button"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition-colors"
        @click="reset"
      >
        もう一度アップロード
      </button>
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition-colors"
        @click="$emit('close')"
      >
        閉じる
      </button>
      <button
        v-if="!result && !uploadError && selectedFile && !uploading"
        type="button"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50"
        :disabled="uploading"
        @click="upload"
      >
        アップロード
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { faqApi, type BulkUploadResult } from '@/api/faq'

const emit = defineEmits<{
  close: []
  success: []
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const result = ref<BulkUploadResult | null>(null)
const uploadError = ref<string | null>(null)
const isDragging = ref(false)

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectedFile.value = file
    uploadError.value = null
    result.value = null
  }
  target.value = ''
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.name.toLowerCase().endsWith('.csv')) {
    selectedFile.value = file
    uploadError.value = null
    result.value = null
  }
}

function reset() {
  selectedFile.value = null
  result.value = null
  uploadError.value = null
  uploadProgress.value = 0
}

async function upload() {
  if (!selectedFile.value) return
  uploading.value = true
  uploadError.value = null
  result.value = null
  uploadProgress.value = 0
  try {
    const res = await faqApi.bulkUploadCsv(
      selectedFile.value,
      'add',
      (p) => { uploadProgress.value = p }
    )
    result.value = res
    emit('success')
  } catch (err: unknown) {
    // axios インターセプターで handleApiError が返す AppError { code, message } を優先して表示
    const appErrorMsg =
      err && typeof err === 'object' && 'message' in err && typeof (err as { message: unknown }).message === 'string'
        ? (err as { message: string }).message
        : null
    const rawDetail =
      err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : null
    const msg = appErrorMsg ?? (typeof rawDetail === 'string' ? rawDetail : null)
    uploadError.value = msg ?? 'アップロードに失敗しました。しばらく待ってから再度お試しください。'
  } finally {
    uploading.value = false
    uploadProgress.value = 100
  }
}

defineExpose({ reset })
</script>
