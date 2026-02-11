<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getGuide } from '@/api/guides'
import GuideRenderer from '@/components/guide/GuideRenderer.vue'

const route = useRoute()
const router = useRouter()
const guide = ref(null)
const loading = ref(true)
const error = ref(null)
const activeIndex = ref(0)
const mobileNavOpen = ref(false)
let observer = null

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

const navItems = computed(() => {
  if (!guide.value?.sections) return []
  return guide.value.sections.map((s, i) => ({ title: s.title, index: i }))
})

const scrollToSection = (index) => {
  const el = document.getElementById(`section-${index}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeIndex.value = index
    mobileNavOpen.value = false
  }
}

const setupScrollObserver = () => {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        const id = entry.target.id
        const match = id?.match(/^section-(\d+)$/)
        if (match) activeIndex.value = parseInt(match[1], 10)
      })
    },
    { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
  )
  navItems.value.forEach((item) => {
    const el = document.getElementById(`section-${item.index}`)
    if (el) observer.observe(el)
  })
}

watch(
  () => guide.value?.sections,
  (sections) => {
    if (sections?.length) {
      setTimeout(setupScrollObserver, 100)
    }
  },
  { immediate: true }
)

onMounted(fetchGuide)
onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<template>
  <div class="min-h-screen pb-20 pt-20" style="background: var(--bg-page);">
    <div class="container mx-auto px-4 max-w-6xl">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
      </div>

      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-500">{{ error }}</p>
        <button @click="goBack" class="mt-4 px-4 py-2 rounded bg-gray-200 hover:bg-gray-300">返回列表</button>
      </div>

      <div v-else-if="guide" class="flex gap-8 lg:gap-12">
        <!-- 移动端：目录按钮 -->
        <div v-if="navItems.length > 0" class="lg:hidden fixed bottom-24 right-4 z-40">
          <!-- 背景遮罩（先渲染，点击关闭） -->
          <div
            v-show="mobileNavOpen"
            class="fixed inset-0 bg-black/20"
            @click="mobileNavOpen = false"
          />
          <button
            type="button"
            class="relative flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg text-sm font-medium"
            style="background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary);"
            @click="mobileNavOpen = !mobileNavOpen"
          >
            <span>📋</span> 目录
          </button>
          <!-- 移动端目录浮层 -->
          <Transition name="fade">
            <div
              v-show="mobileNavOpen"
              class="absolute bottom-full right-0 mb-2 w-64 max-h-72 overflow-y-auto rounded-xl shadow-xl py-2 z-10"
              style="background: var(--bg-card); border: 1px solid var(--border-color);"
            >
              <ul class="space-y-0.5 px-2">
                <li v-for="item in navItems" :key="item.index">
                  <button
                    type="button"
                    class="w-full text-left px-3 py-2 rounded-lg text-sm truncate"
                    :class="activeIndex === item.index ? 'font-medium' : ''"
                    :style="activeIndex === item.index
                      ? { color: 'var(--nav-active-text)', background: 'var(--nav-active-bg)' }
                      : { color: 'var(--nav-text)' }"
                    @click="scrollToSection(item.index)"
                  >
                    {{ item.title }}
                  </button>
                </li>
              </ul>
            </div>
          </Transition>
        </div>

        <!-- 左侧导航栏（桌面端） -->
        <aside
          v-if="navItems.length > 0"
          class="hidden lg:block shrink-0 w-52"
        >
          <nav
            class="sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto py-2"
            style="color: var(--text-secondary);"
          >
            <p class="text-xs font-semibold uppercase tracking-wider mb-3 px-2" style="color: var(--text-muted);">
              目录
            </p>
            <ul class="space-y-0.5">
              <li v-for="item in navItems" :key="item.index">
                <button
                  type="button"
                  class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors truncate"
                  :class="activeIndex === item.index ? 'font-medium' : ''"
                  :style="activeIndex === item.index
                    ? { color: 'var(--nav-active-text)', background: 'var(--nav-active-bg)' }
                    : { color: 'var(--nav-text)' }"
                  @click="scrollToSection(item.index)"
                >
                  {{ item.title }}
                </button>
              </li>
            </ul>
          </nav>
        </aside>

        <!-- 主内容区 -->
        <main class="flex-1 min-w-0">
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
        </main>
      </div>
    </div>
  </div>
</template>
