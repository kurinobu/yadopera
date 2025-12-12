<template>
  <router-link
    :to="to"
    :class="[
      'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
      isActive
        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
    ]"
  >
    <component :is="icon" class="w-5 h-5" />
    <span>{{ label }}</span>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface Props {
  to: string
  label: string
  icon: any
}

const props = defineProps<Props>()
const route = useRoute()

const isActive = computed(() => {
  return route.path === props.to || route.path.startsWith(props.to + '/')
})
</script>

<style scoped>
/* Component styles */
</style>


