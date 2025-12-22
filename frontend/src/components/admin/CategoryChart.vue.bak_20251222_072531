<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
      カテゴリ別内訳
    </h3>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
      過去7日間のメッセージで使用されたFAQのカテゴリ集計
    </p>
    
    <!-- 円グラフ -->
    <div class="flex items-center justify-center mb-6">
      <svg :width="size" :height="size" class="transform -rotate-90">
        <circle
          :cx="center"
          :cy="center"
          :r="radius"
          fill="none"
          stroke="#e5e7eb"
          :stroke-width="strokeWidth"
          class="dark:stroke-gray-700"
        />
        <circle
          v-for="(segment, index) in segments"
          :key="index"
          :cx="center"
          :cy="center"
          :r="radius"
          fill="none"
          :stroke="segment.color"
          :stroke-width="strokeWidth"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="segment.offset"
          :stroke-linecap="'round'"
          class="transition-all duration-300"
        />
      </svg>
    </div>

    <!-- 凡例 -->
    <div class="space-y-2">
      <div
        v-for="(item, index) in chartData"
        :key="index"
        class="flex items-center justify-between"
      >
        <div class="flex items-center">
          <div
            :class="[
              'w-4 h-4 rounded-full mr-3',
              item.colorClass
            ]"
          />
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ item.label }}
          </span>
        </div>
        <span class="text-sm font-semibold text-gray-900 dark:text-white">
          {{ item.value }}件
        </span>
      </div>
    </div>

    <!-- 合計 -->
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          合計
        </span>
        <span class="text-lg font-bold text-gray-900 dark:text-white">
          {{ total }}件
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface CategoryData {
  basic: number
  facilities: number
  location: number
  trouble: number
}

interface Props {
  data: CategoryData
}

const props = defineProps<Props>()

const size = 200
const center = size / 2
const radius = 80
const strokeWidth = 20
const circumference = 2 * Math.PI * radius

const chartData = computed(() => {
  const categories = [
    { key: 'basic', label: 'Basic', color: '#3b82f6', colorClass: 'bg-blue-500' },
    { key: 'facilities', label: 'Facilities', color: '#10b981', colorClass: 'bg-green-500' },
    { key: 'location', label: 'Location', color: '#f59e0b', colorClass: 'bg-yellow-500' },
    { key: 'trouble', label: 'Trouble', color: '#ef4444', colorClass: 'bg-red-500' }
  ]

  return categories.map(item => ({
    ...item,
    value: props.data[item.key as keyof CategoryData]
  }))
})

const total = computed(() => {
  return Object.values(props.data).reduce((sum, val) => sum + val, 0)
})

const segments = computed(() => {
  let currentOffset = 0
  
  // 値が0より大きいカテゴリのみをフィルタ
  const validItems = chartData.value.filter((item) => item.value > 0)
  
  return validItems.map((item) => {
    const percentage = total.value > 0 ? item.value / total.value : 0
    const dashLength = circumference * percentage
    const offset = circumference - (currentOffset + dashLength)  // 修正: 正しい計算式（円周から累積オフセット+セグメント長を引く）
    
    currentOffset += dashLength  // 次のセグメントの開始位置を更新
    
    return {
      color: item.color,
      offset: offset
    }
  })
})
</script>

<style scoped>
/* Component styles */
</style>

