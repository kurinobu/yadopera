<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import GuestLayout from '@/layouts/GuestLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

const route = useRoute()

const layoutComponent = computed(() => {
  const layout = route.meta.layout as string | undefined
  
  if (layout === 'guest') {
    return GuestLayout
  }
  
  if (layout === 'admin') {
    return AdminLayout
  }
  
  // デフォルト（レイアウトなし）
  return 'div'
})
</script>

<style>
/* Global styles */
</style>


