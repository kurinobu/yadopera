<template>
  <nav :class="['manual-toc', { 'mobile-toc': isMobile }]">
    <ul class="space-y-1">
      <li v-for="section in sections" :key="section.id" class="manual-toc-section">
        <!-- 章タイトル -->
        <div class="flex items-center justify-between">
          <!-- 章タイトルテキスト（クリックでスクロール） -->
          <button
            class="manual-toc-item-title flex-1 text-left"
            @click="handleSectionClick(section.id)"
          >
            <span class="font-medium">{{ section.title }}</span>
          </button>
          
          <!-- アイコンボタン（クリックで折りたたみ/展開） -->
          <button
            class="manual-toc-toggle"
            @click.stop="toggleSection(section.id)"
            :aria-label="expandedSections[section.id] ? '折りたたむ' : '展開する'"
            :aria-expanded="expandedSections[section.id]"
          >
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
          </button>
        </div>

        <!-- サブセクション（折りたたみ可能） -->
        <ul
          v-show="expandedSections[section.id]"
          class="manual-toc-subsections ml-4 mt-1 space-y-1"
        >
          <li v-for="subsection in section.subsections" :key="subsection.id">
            <button
              class="manual-toc-subitem w-full text-left text-sm"
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
import { reactive } from 'vue'

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
  isMobile?: boolean
}

const props = defineProps<Props>()

// 章の折りたたみ状態管理
const expandedSections = reactive<Record<string, boolean>>({})

// 章の折りたたみ/展開のみ（スクロールなし）
const toggleSection = (sectionId: string) => {
  expandedSections[sectionId] = !expandedSections[sectionId]
}

// 章タイトルクリック時の処理（スクロールのみ）
const handleSectionClick = (sectionId: string) => {
  scrollToSection(sectionId)
}

// サブセクションクリック時の処理
const handleSubsectionClick = (sectionId: string, subsectionId: string) => {
  // 章を展開状態にする
  expandedSections[sectionId] = true

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

.manual-toc-item-title {
  @apply px-4 py-2 rounded-lg transition-colors;
  @apply text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
  @apply cursor-pointer;
}

.manual-toc-toggle {
  @apply ml-2 flex-shrink-0;
  @apply p-1 rounded transition-colors;
  @apply text-gray-500 dark:text-gray-400;
  @apply hover:bg-gray-200 dark:hover:bg-gray-700;
  @apply hover:text-gray-700 dark:hover:text-gray-300;
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
</style>

