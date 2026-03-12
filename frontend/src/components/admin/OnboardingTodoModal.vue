<template>
  <Modal
    :model-value="modelValue"
    title="はじめにやること"
    size="lg"
    closable
    :close-on-backdrop="true"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="space-y-4 text-left">
      <ol class="list-decimal list-inside space-y-4 text-gray-700 dark:text-gray-300">
        <li>
          <span>施設設定の確認（施設名・連絡先・WiFi・チェックイン/アウト・館内ルールなど）</span>
        </li>
        <li>
          <div class="font-semibold text-amber-700 dark:text-amber-400">
            ★ FAQの登録・編集（最重要）
          </div>
          <p class="mt-1 ml-6 text-sm text-gray-600 dark:text-gray-400">
            登録数が多く、内容が具体的なほどAIの回答精度が上がり、自動応答率が高まります。初期デフォルトを確認し、施設に合わせて追加・編集してください。
          </p>
        </li>
        <li>
          <div class="font-semibold text-amber-700 dark:text-amber-400">
            ★ QRコードの発行と設置（最重要）
          </div>
          <p class="mt-1 ml-6 text-sm text-gray-600 dark:text-gray-400">
            ゲストが質問にアクセスする入口です。掲示・貼り付けに加え、チェックイン時にQRコードを読み込んでもらうと利用率が上がります。入口・客室など見やすい場所へ設置し、読み取りテストをしてください。
          </p>
        </li>
        <li>
          <span>動作確認（ゲスト画面・AI回答・エスカレーション）</span>
        </li>
        <li>
          <span>初期設定チェックリストの確認（マニュアル第12章）</span>
        </li>
      </ol>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        詳しくはご利用マニュアルの<strong>初期設定</strong>をご覧ください。
      </p>
    </div>
    <template #footer>
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg"
        @click="onClose(false)"
      >
        閉じる
      </button>
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg"
        @click="onClose(true)"
      >
        マニュアルで見る
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import Modal from '@/components/common/Modal.vue'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  done: [payload: { goToManual: boolean }]
}>()

function onClose(goToManual: boolean) {
  emit('done', { goToManual })
  emit('update:modelValue', false)
}
</script>
