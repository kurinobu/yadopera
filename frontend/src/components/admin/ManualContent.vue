<template>
  <div class="manual-content">
    <div
      v-for="section in sections"
      :key="section.id"
      :id="section.id"
      class="manual-section"
    >
      <!-- 章タイトル -->
      <h1 class="manual-h1">{{ section.title }}</h1>

      <!-- サブセクション -->
      <div
        v-for="subsection in section.subsections"
        :key="subsection.id"
        :id="subsection.id"
        class="manual-subsection"
      >
        <h2 class="manual-h2">{{ subsection.title }}</h2>
        <div class="manual-text" v-html="formatContent(getContent(section.id, subsection.id))"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ManualSubsection {
  id: string
  title: string
  content?: string
}

interface ManualSection {
  id: string
  title: string
  subsections: ManualSubsection[]
}

interface Props {
  sections: ManualSection[]
}

const props = defineProps<Props>()

// コンテンツ取得
const getContent = (sectionId: string, subsectionId: string): string => {
  const section = props.sections.find(s => s.id === sectionId)
  const subsection = section?.subsections.find(sub => sub.id === subsectionId)
  return subsection?.content || '説明内容は準備中です。'
}

// CSVテンプレートDL用URL（修正案A: フォールバックで確実にリンク化するため）
const CSV_TEMPLATE_PATH = '/faq-csv-template/FAQ_CSV_template_4lang.csv'
const CSV_TEMPLATE_LINK_CLASS = 'text-blue-600 dark:text-blue-400 hover:underline'

// [表示テキスト](URL) をリンクに変換（**変換の後に適用）
const applyLink = (s: string): string =>
  s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 dark:text-blue-400 hover:underline">$1</a>')

// プレースホルダ（content 段階で CSV リンクを確実に <a> にするため）
const CSV_LINK_PLACEHOLDER = '__CSV_TEMPLATE_LINK__'
// 半角・全角括弧を許容するパターン（本番ビルド・表記ゆれに対応）
const csvMarkdownInContent = /\[CSVテンプレートをダウンロード\]\s*[（(]\/faq-csv-template\/FAQ_CSV_template_4lang\.csv[）)]/g

// マークダウン風のテキストをHTMLに変換
const formatContent = (content: string): string => {
  if (!content) return ''

  // 問題A 根本対策: 元の content の段階で CSV リンク部分をプレースホルダに置換し、最後に必ず <a> に戻す
  const normalizedContent = content.replace(csvMarkdownInContent, CSV_LINK_PLACEHOLDER)

  const lines = normalizedContent.split('\n')
  let html = ''
  let inList = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()

    // リスト項目の処理
    if (trimmed.startsWith('- ')) {
      if (!inList) {
        html += '<ul>'
        inList = true
      }
      // **太字**を<strong>に変換してからリンクを適用し<li>に追加
      const listContent = applyLink(trimmed.substring(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'))
      html += `<li>${listContent}</li>`
    } else {
      // リストの終了
      if (inList) {
        html += '</ul>'
        inList = false
      }

      // 空行は無視
      if (trimmed === '') {
        html += '<br>'
        continue
      }

      // **太字**を<strong>に変換してからリンクを適用
      const formattedLine = applyLink(trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'))
      html += `<p>${formattedLine}</p>`
    }
  }
  
  // リストが最後まで続いていた場合、閉じる
  if (inList) {
    html += '</ul>'
  }

  // 修正案A: CSVテンプレートリンクのフォールバック（applyLink が効いていない場合でも確実に <a> にする）
  const csvTemplateAnchor = `<a href="${CSV_TEMPLATE_PATH}" class="${CSV_TEMPLATE_LINK_CLASS}">CSVテンプレートをダウンロード</a>`
  // 完全一致置換
  const csvTemplateMarkdown = `[CSVテンプレートをダウンロード](${CSV_TEMPLATE_PATH})`
  const exactMatch = html.includes(csvTemplateMarkdown)
  if (exactMatch) {
    html = html.replace(csvTemplateMarkdown, csvTemplateAnchor)
  }
  // 正規表現で柔軟に置換（空白類の有無など再表示時の表記差に対応）
  const csvLinkPattern = /\[CSVテンプレートをダウンロード\]\s*\(\/faq-csv-template\/FAQ_CSV_template_4lang\.csv\)/g
  const beforeRegex = html
  html = html.replace(csvLinkPattern, csvTemplateAnchor)
  const regexReplaceCount = (beforeRegex.match(csvLinkPattern) || []).length

  // 問題A 根本対策: プレースホルダを必ず <a> に置換（行単位変換に依存しない）
  html = html.split(CSV_LINK_PLACEHOLDER).join(csvTemplateAnchor)

  // デバッグ: ?debug=csv のときだけコンソールに出力（ステージング等の切り分け用）
  if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('debug') === 'csv') {
    const hasCsvText = content.includes('CSVテンプレートをダウンロード')
    console.log('[yadopera-csv] ManualContent formatContent:', {
      hasCsvText,
      exactMatch,
      regexReplaceCount,
      linkInHtml: html.includes(CSV_TEMPLATE_PATH) && html.includes('CSVテンプレートをダウンロード'),
    })
  }

  return html
}
</script>

<style scoped>
.manual-content {
  @apply space-y-8;
}

.manual-section {
  @apply scroll-mt-20;
}

/* 章タイトル（h1） - 2rem = text-3xl (1.875rem) が最も近い */
.manual-h1 {
  @apply text-3xl font-bold;
  @apply text-gray-900 dark:text-white;
  @apply mt-12 mb-6 pb-2;
  @apply border-b-2 border-blue-500;
}

/* 中項目（h2） - 1.5rem = text-2xl (1.5rem) */
.manual-h2 {
  @apply text-2xl font-semibold;
  @apply text-gray-800 dark:text-gray-200;
  @apply mt-8 mb-4;
}

/* 小項目（h3） */
.manual-h3 {
  @apply text-xl font-semibold;
  @apply text-gray-700 dark:text-gray-300;
  @apply mt-6 mb-3;
}

/* テキスト */
.manual-text {
  @apply text-base;
  @apply leading-[1.75];
  @apply text-gray-600 dark:text-gray-400;
}

.manual-text p {
  @apply mb-4;
  @apply text-base;
  @apply leading-[1.75];
}

.manual-text code {
  @apply bg-gray-100 dark:bg-gray-800;
  @apply px-1.5 py-0.5 rounded;
  @apply font-mono text-sm;
  @apply text-gray-800 dark:text-gray-200;
}

.manual-text ul,
.manual-text ol {
  @apply mb-4 ml-6;
}

.manual-text ul {
  @apply list-disc;
}

.manual-text ol {
  @apply list-decimal;
}

.manual-text li {
  @apply mb-2;
}

.manual-text strong {
  @apply font-semibold text-gray-900 dark:text-gray-100;
}

/* 強調表示 */
.manual-note {
  @apply bg-blue-50 dark:bg-blue-900/20;
  @apply border-l-4 border-blue-500;
  @apply p-4 my-4 rounded;
}

.manual-warning {
  @apply bg-yellow-50 dark:bg-yellow-900/20;
  @apply border-l-4 border-yellow-500;
  @apply p-4 my-4 rounded;
}

.manual-tip {
  @apply bg-green-50 dark:bg-green-900/20;
  @apply border-l-4 border-green-500;
  @apply p-4 my-4 rounded;
}

.manual-subsection {
  @apply scroll-mt-20;
}
</style>

