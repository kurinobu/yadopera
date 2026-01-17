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
import { onMounted, onUnmounted } from 'vue'

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

const emit = defineEmits<{
  'section-change': [sectionId: string]
}>()

// スクロール監視用のIntersectionObserver
let observer: IntersectionObserver | null = null

// コンテンツ取得
const getContent = (sectionId: string, subsectionId: string): string => {
  const section = props.sections.find(s => s.id === sectionId)
  const subsection = section?.subsections.find(sub => sub.id === subsectionId)
  return subsection?.content || '説明内容は準備中です。'
}

// マークダウン風のテキストをHTMLに変換
const formatContent = (content: string): string => {
  if (!content) return ''
  
  const lines = content.split('\n')
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
      // **太字**を<strong>に変換してから<li>に追加
      const listContent = trimmed.substring(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
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
      
      // **太字**を<strong>に変換
      const formattedLine = trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      html += `<p>${formattedLine}</p>`
    }
  }
  
  // リストが最後まで続いていた場合、閉じる
  if (inList) {
    html += '</ul>'
  }
  
  return html
}

// スクロール監視のセットアップ
onMounted(() => {
  // IntersectionObserverで現在表示中のセクションを検出
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
          const sectionId = entry.target.id
          // 親セクションIDを取得
          const section = props.sections.find((s) => {
            return s.id === sectionId || s.subsections.some((sub) => sub.id === sectionId)
          })
          if (section) {
            emit('section-change', section.id)
          }
        }
      })
    },
    {
      rootMargin: '-20% 0px -50% 0px',
      threshold: [0, 0.5, 1]
    }
  )

  // すべてのセクションとサブセクションを監視対象に追加
  props.sections.forEach((section) => {
    const sectionElement = document.getElementById(section.id)
    if (sectionElement) {
      observer?.observe(sectionElement)
    }

    section.subsections.forEach((subsection) => {
      const subsectionElement = document.getElementById(subsection.id)
      if (subsectionElement) {
        observer?.observe(subsectionElement)
      }
    })
  })
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
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

