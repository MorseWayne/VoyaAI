<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getGuide } from '@/api/guides'
import GuideRenderer from '@/components/guide/GuideRenderer.vue'

const route = useRoute()
const router = useRouter()
const guide = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchGuide = async () => {
  loading.value = true
  try {
    guide.value = await getGuide(route.params.id)
  } catch (e) {
    error.value = '加载攻略失败: ' + e.message
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'guides' })
}

onMounted(fetchGuide)
</script>

<template>
  <div class="min-h-screen pb-20 pt-20" style="background: var(--bg-page);">
    <div class="container mx-auto px-4 max-w-4xl">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
      </div>

      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-500">{{ error }}</p>
        <button @click="goBack" class="mt-4 px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">返回列表</button>
      </div>

      <div v-else-if="guide">
        <!-- Back Button -->
        <button 
          @click="goBack"
          class="mb-6 flex items-center gap-2 text-sm font-medium transition-colors hover:text-cyan-600"
          style="color: var(--text-secondary);"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          返回攻略列表
        </button>

        <!-- Header -->
        <div class="mb-8 text-center">
          <h1 class="text-3xl font-bold mb-2" style="color: var(--text-heading);">{{ guide.title }}</h1>
          <p v-if="guide.description" class="text-lg" style="color: var(--text-secondary);">{{ guide.description }}</p>
        </div>

        <!-- Content -->
        <GuideRenderer :guide="guide" />
      </div>
    </div>
  </div>
</template>
