<template>
  <div class="manual-container">
    <!-- ページヘッダー -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            ご利用マニュアル
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            YadOPERAの操作方法・機能説明
          </p>
        </div>
        <!-- モバイル用目次トグルボタン -->
        <button
          @click="isMobileTocOpen = !isMobileTocOpen"
          class="lg:hidden p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
          aria-label="目次を開く"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- モバイル用目次（折りたたみ） -->
    <div
      v-if="isMobileTocOpen"
      class="lg:hidden mb-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg"
    >
      <ManualToc :sections="sections" :activeSection="activeSection" :isMobile="true" />
    </div>

    <!-- メインコンテンツエリア -->
    <div class="flex gap-6">
      <!-- 目次（タブレット・デスクトップ） -->
      <aside class="hidden md:block md:w-[200px] lg:w-64 flex-shrink-0">
        <ManualToc :sections="sections" :activeSection="activeSection" />
      </aside>

      <!-- マニュアル本文 -->
      <main class="flex-1 md:max-w-3xl lg:max-w-[800px]">
        <ManualContent :sections="sections" @section-change="handleSectionChange" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ManualToc from '@/components/admin/ManualToc.vue'
import ManualContent from '@/components/admin/ManualContent.vue'

// モバイル用目次開閉状態
const isMobileTocOpen = ref(false)

// マニュアルセクション定義（12章構成）
const sections = ref([
  {
    id: 'intro',
    title: '第1章 はじめに',
    subsections: [
      { id: 'intro-about', title: '1.1 YadOPERAとは' },
      { id: 'intro-howto', title: '1.2 本マニュアルの使い方' },
      { id: 'intro-requirements', title: '1.3 システム要件' }
    ]
  },
  {
    id: 'login',
    title: '第2章 ログイン・ログアウト',
    subsections: [
      { id: 'login-first', title: '2.1 初回ログイン' },
      { id: 'login-logout', title: '2.2 ログアウト' },
      { id: 'login-error', title: '2.3 ログインできない場合' }
    ]
  },
  {
    id: 'dashboard',
    title: '第3章 ダッシュボードの見方',
    subsections: [
      { id: 'dashboard-overview', title: '3.1 ダッシュボード概要' },
      { id: 'dashboard-total', title: '3.2 総質問数' },
      { id: 'dashboard-rate', title: '3.3 自動応答率' },
      { id: 'dashboard-confidence', title: '3.4 平均信頼度' },
      { id: 'dashboard-unresolved', title: '3.5 未解決質問' },
      { id: 'dashboard-category', title: '3.6 カテゴリ別内訳' },
      { id: 'dashboard-realtime', title: '3.7 リアルタイムチャット履歴' }
    ]
  },
  {
    id: 'faq',
    title: '第4章 FAQ管理',
    subsections: [
      { id: 'faq-overview', title: '4.1 FAQ管理画面の概要' },
      { id: 'faq-list', title: '4.2 FAQ一覧の見方' },
      { id: 'faq-create', title: '4.3 新規FAQ登録' },
      { id: 'faq-edit', title: '4.4 FAQ編集' },
      { id: 'faq-delete', title: '4.5 FAQ削除' },
      { id: 'faq-suggestion', title: '4.6 FAQ改善提案機能' },
      { id: 'faq-best-practices', title: '4.7 FAQ作成のベストプラクティス' }
    ]
  },
  {
    id: 'overnight-queue',
    title: '第5章 スタッフ不在時間帯対応キュー',
    subsections: [
      { id: 'overnight-overview', title: '5.1 スタッフ不在時間帯対応キューとは' },
      { id: 'overnight-list', title: '5.2 対応キュー一覧の見方' },
      { id: 'overnight-response', title: '5.3 質問への対応' },
      { id: 'overnight-manage', title: '5.4 対応済み質問の管理' }
    ]
  },
  {
    id: 'facility',
    title: '第6章 施設設定',
    subsections: [
      { id: 'facility-overview', title: '6.1 施設設定画面の概要' },
      { id: 'facility-basic', title: '6.2 基本情報設定' },
      { id: 'facility-overnight', title: '6.3 スタッフ不在時間帯設定' },
      { id: 'facility-save', title: '6.4 施設情報の保存' }
    ]
  },
  {
    id: 'qr-code',
    title: '第7章 QRコード発行',
    subsections: [
      { id: 'qr-overview', title: '7.1 QRコードとは' },
      { id: 'qr-generate', title: '7.2 QRコード発行手順' },
      { id: 'qr-download', title: '7.3 QRコードのダウンロード' },
      { id: 'qr-install', title: '7.4 QRコードの設置方法' },
      { id: 'qr-test', title: '7.5 QRコードのテスト' }
    ]
  },
  {
    id: 'conversation',
    title: '第8章 会話詳細の確認',
    subsections: [
      { id: 'conversation-overview', title: '8.1 会話詳細画面の概要' },
      { id: 'conversation-history', title: '8.2 会話履歴の見方' },
      { id: 'conversation-guest', title: '8.3 ゲスト情報の確認' },
      { id: 'conversation-reply', title: '8.4 手動返信（将来機能）' }
    ]
  },
  {
    id: 'guest',
    title: '第9章 ゲスト側の使い方（管理者向け説明）',
    subsections: [
      { id: 'guest-flow', title: '9.1 ゲストの利用フロー' },
      { id: 'guest-language', title: '9.2 言語選択画面' },
      { id: 'guest-welcome', title: '9.3 ウェルカム画面' },
      { id: 'guest-chat', title: '9.4 チャット画面' },
      { id: 'guest-pwa', title: '9.5 PWA（Progressive Web App）機能' }
    ]
  },
  {
    id: 'troubleshooting',
    title: '第10章 トラブルシューティング',
    subsections: [
      { id: 'trouble-faq', title: '10.1 よくある質問（FAQ）' },
      { id: 'trouble-error', title: '10.2 エラーメッセージ一覧' },
      { id: 'trouble-cache', title: '10.3 ブラウザキャッシュのクリア方法' },
      { id: 'trouble-contact', title: '10.4 問い合わせ方法' }
    ]
  },
  {
    id: 'best-practices',
    title: '第11章 運用のベストプラクティス',
    subsections: [
      { id: 'practice-checklist', title: '11.1 初期設定チェックリスト' },
      { id: 'practice-daily', title: '11.2 日次運用' },
      { id: 'practice-weekly', title: '11.3 週次運用' },
      { id: 'practice-monthly', title: '11.4 月次運用' }
    ]
  },
  {
    id: 'appendix',
    title: '第12章 付録',
    subsections: [
      { id: 'appendix-glossary', title: '12.1 用語集' },
      { id: 'appendix-flow', title: '12.2 画面遷移図' },
      { id: 'appendix-template', title: '12.3 FAQ初期テンプレート例' },
      { id: 'appendix-history', title: '12.4 更新履歴' }
    ]
  }
])

const activeSection = ref('intro')

const handleSectionChange = (sectionId: string) => {
  activeSection.value = sectionId
}

onMounted(() => {
  // 初期化処理（必要に応じて）
})
</script>

<style scoped>
.manual-container {
  @apply w-full;
}
</style>

