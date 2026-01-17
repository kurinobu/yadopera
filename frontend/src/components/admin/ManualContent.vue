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
        <div class="manual-text">
          <p>{{ getContent(section.id, subsection.id) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

interface ManualSubsection {
  id: string
  title: string
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

// コンテンツ取得（暫定実装、後で詳細を追加）
const getContent = (_sectionId: string, subsectionId: string): string => {
  // 暫定的なプレースホルダー
  // 後で各セクションの詳細な内容を実装
  // sectionIdは将来の実装で使用予定
  return `${subsectionId}の説明内容は後で追加します。`
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

