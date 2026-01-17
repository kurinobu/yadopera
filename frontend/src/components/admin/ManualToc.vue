<template>
  <nav :class="['manual-toc', { 'mobile-toc': isMobile }]">
    <ul class="space-y-1">
      <li v-for="section in sections" :key="section.id" class="manual-toc-section">
        <!-- 章タイトル -->
        <button
          :class="[
            'manual-toc-item w-full text-left',
            activeSection === section.id ? 'active' : ''
          ]"
          @click="handleSectionClick(section.id)"
        >
          <div class="flex items-center justify-between">
            <span class="font-medium">{{ section.title }}</span>
            <svg
              :class="[
                'w-4 h-4 transition-transform',
                expandedSections[section.id] ? 'rotate-90' : ''
              ]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </div>
        </button>

        <!-- サブセクション（折りたたみ可能） -->
        <ul
          v-show="expandedSections[section.id]"
          class="manual-toc-subsections ml-4 mt-1 space-y-1"
        >
          <li v-for="subsection in section.subsections" :key="subsection.id">
            <button
              :class="[
                'manual-toc-subitem w-full text-left text-sm',
                activeSubsection === subsection.id ? 'active' : ''
              ]"
              @click="handleSubsectionClick(section.id, subsection.id)"
            >
              {{ subsection.title }}
            </button>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

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
  activeSection: string
  isMobile?: boolean
}

const props = defineProps<Props>()

// 章の折りたたみ状態管理
const expandedSections = reactive<Record<string, boolean>>({})

// アクティブなサブセクション
const activeSubsection = ref<string>('')

// 初期化: アクティブな章は展開状態にする
watch(
  () => props.activeSection,
  (newSection) => {
    if (newSection && !expandedSections[newSection]) {
      expandedSections[newSection] = true
    }
  },
  { immediate: true }
)

// 章クリック時の処理
const handleSectionClick = (sectionId: string) => {
  // 折りたたみ/展開をトグル
  expandedSections[sectionId] = !expandedSections[sectionId]

  // スクロール処理（親コンポーネントに通知）
  scrollToSection(sectionId)
}

// サブセクションクリック時の処理
const handleSubsectionClick = (sectionId: string, subsectionId: string) => {
  // 章を展開状態にする
  expandedSections[sectionId] = true

  // アクティブなサブセクションを設定
  activeSubsection.value = subsectionId

  // スクロール処理
  scrollToSubsection(subsectionId)
}

// セクションへスクロール
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// サブセクションへスクロール
const scrollToSubsection = (subsectionId: string) => {
  const element = document.getElementById(subsectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<style scoped>
.manual-toc {
  @apply w-full md:w-[200px] lg:w-64;
  @apply overflow-y-auto;
  @apply pr-4;
  @apply border-r-0 md:border-r border-gray-200 dark:border-gray-700;
  @apply p-4 md:p-0;
}

.manual-toc:not(.mobile-toc) {
  @apply sticky top-20;
  @apply max-h-[calc(100vh-100px)];
}

.manual-toc.mobile-toc {
  @apply max-h-[70vh];
}

.manual-toc-section {
  @apply mb-1;
}

.manual-toc-item {
  @apply px-4 py-2 rounded-lg transition-colors;
  @apply text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
}

.manual-toc-item.active {
  @apply bg-blue-100 dark:bg-blue-900/30;
  @apply text-blue-700 dark:text-blue-300;
  @apply font-semibold;
}

.manual-toc-subsections {
  @apply border-l-2 border-gray-200 dark:border-gray-700 pl-2;
}

.manual-toc-subitem {
  @apply px-3 py-1.5 rounded transition-colors;
  @apply text-gray-600 dark:text-gray-400;
  @apply hover:bg-gray-50 dark:hover:bg-gray-800;
  @apply hover:text-gray-900 dark:hover:text-gray-200;
}

.manual-toc-subitem.active {
  @apply bg-blue-50 dark:bg-blue-900/20;
  @apply text-blue-600 dark:text-blue-400;
  @apply font-medium;
}
</style>

