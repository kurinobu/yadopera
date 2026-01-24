<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import GuestLayout from '@/layouts/GuestLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import DeveloperLayout from '@/layouts/DeveloperLayout.vue'
import { updateManifestLink } from '@/utils/manifestGenerator'

const route = useRoute()

const layoutComponent = computed(() => {
  const layout = route.meta.layout as string | undefined
  
  if (layout === 'guest') {
    return GuestLayout
  }
  
  if (layout === 'admin') {
    return AdminLayout
  }
  
  if (layout === 'developer') {
    return DeveloperLayout
  }
  
  // デフォルト（レイアウトなし）
  return 'div'
})

// DOM ready後に動的manifestを初期化
onMounted(() => {
  updateManifestLink(null)
})
</script>

<style>
/* Global styles */
</style>


