<script setup>
import NavBar from '@/components/layout/NavBar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import { useThemeStore } from '@/stores/theme'

// Initialize theme store (applies theme immediately)
useThemeStore()
</script>

<template>
  <NavBar />
  <main class="flex-grow container mx-auto px-4 py-8">
    <RouterView />
  </main>
  <AppFooter />
  <ToastContainer />
</template>
