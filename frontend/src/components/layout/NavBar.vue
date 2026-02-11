<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const mobileMenuOpen = ref(false)

const isHome = computed(() => route.name === 'home')

const navItems = [
  { name: 'planner', label: '路线规划', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { name: 'plans', label: '我的行程', icon: 'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z' },
  { name: 'guides', label: '攻略合集', icon: 'M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15' },
  { name: 'chat', label: '智能助手', icon: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z' },
]

function goHome() {
  router.push({ name: 'home' })
}

function navigate(name) {
  router.push({ name })
  mobileMenuOpen.value = false
}
</script>

<template>
  <nav class="glass-panel sticky top-0 z-50 shadow-sm">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div @click="goHome" class="flex items-center space-x-3 cursor-pointer group" role="button" tabindex="0" aria-label="返回首页">
          <div class="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-cyan-500/30 group-hover:shadow-cyan-500/50 transition-shadow">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"/>
            </svg>
          </div>
          <span class="text-2xl font-bold logo-text tracking-tight">VoyaAI</span>
        </div>

        <!-- Desktop Menu -->
        <div v-show="!isHome" class="hidden md:flex space-x-1 items-center">
          <button
            v-for="item in navItems"
            :key="item.name"
            @click="navigate(item.name)"
            class="nav-item py-3 px-4 transition duration-200 rounded-lg flex items-center gap-2 cursor-pointer"
            :class="{ active: route.name === item.name }"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon"/>
            </svg>
            {{ item.label }}
          </button>
          <div class="w-px h-6 mx-1" style="background: var(--border-color);"></div>
          <ThemeToggle />
        </div>

        <!-- Mobile Menu Button -->
        <div v-show="!isHome" class="md:hidden flex items-center gap-2">
          <ThemeToggle />
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="t-text-sub hover:text-primary focus:outline-none p-2 rounded-lg transition cursor-pointer" style="background: var(--nav-hover-bg);" aria-label="打开菜单">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu Dropdown -->
      <div v-show="mobileMenuOpen && !isHome" class="md:hidden pb-4 mt-1" style="border-top: 1px solid var(--border-color);">
        <button
          v-for="item in navItems"
          :key="item.name"
          @click="navigate(item.name)"
          class="w-full py-3 px-4 text-left t-text-sub hover:text-cyan-600 rounded-lg transition flex items-center gap-3 cursor-pointer"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon"/>
          </svg>
          {{ item.label }}
        </button>
      </div>
    </div>
  </nav>
</template>
