<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchPlans } from '@/api/plans'

const router = useRouter()
const recentPlans = ref([])
const planCount = ref(0)
const cityCount = ref(0)
const loading = ref(true)

onMounted(async () => {
  try {
    const plans = await fetchPlans()
    planCount.value = plans.length
    const cities = new Set()
    plans.forEach(p => {
      if (p.start_location?.city) cities.add(p.start_location.city)
      p.days?.forEach(d => {
        if (d.city) cities.add(d.city)
        d.segments?.forEach(s => {
          if (s.origin?.city) cities.add(s.origin.city)
          if (s.destination?.city) cities.add(s.destination.city)
        })
      })
    })
    cityCount.value = cities.size
    recentPlans.value = plans.slice(0, 10)
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
})

function viewPlan(id) {
  router.push({ name: 'plan-detail', params: { id } })
}
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <!-- Welcome Banner -->
    <div class="mb-8 animate-fade-in">
      <h1 class="text-3xl font-bold t-heading mb-2">欢迎回来，旅行者</h1>
      <p class="t-text-sub">准备好开启下一段旅程了吗？</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left: Quick Actions -->
      <div class="space-y-6 animate-fade-in" style="animation-delay: 0.1s;">
        <!-- Create New -->
        <div @click="router.push({ name: 'create-plan' })" class="glass-panel p-6 rounded-2xl cursor-pointer transition group relative overflow-hidden">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
            <i class="fas fa-map-marked-alt text-8xl text-cyan-400"></i>
          </div>
          <div class="relative z-10">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white mb-4 shadow-lg shadow-cyan-500/30">
              <i class="fas fa-plus text-xl"></i>
            </div>
            <h3 class="text-xl font-bold t-heading mb-1">创建新行程</h3>
            <p class="t-text-sub text-sm mb-4">智能规划路线，一键生成攻略</p>
            <span class="text-cyan-500 text-sm font-medium flex items-center gap-2 group-hover:gap-3 transition-all">
              立即开始 <i class="fas fa-arrow-right"></i>
            </span>
          </div>
        </div>

        <!-- Quick Tools -->
        <div class="grid grid-cols-2 gap-4">
          <div @click="router.push({ name: 'planner' })" class="glass-panel p-4 rounded-2xl cursor-pointer transition text-center group">
            <i class="fas fa-route text-2xl text-emerald-400 mb-2 group-hover:scale-110 transition-transform"></i>
            <div class="font-medium t-text">路线优化</div>
          </div>
          <div @click="router.push({ name: 'chat' })" class="glass-panel p-4 rounded-2xl cursor-pointer transition text-center group">
            <i class="fas fa-robot text-2xl text-violet-400 mb-2 group-hover:scale-110 transition-transform"></i>
            <div class="font-medium t-text">AI 助手</div>
          </div>
        </div>

        <!-- Stats -->
        <div class="glass-panel p-6 rounded-2xl">
          <h4 class="text-sm font-bold t-text-muted uppercase tracking-wider mb-4">旅行足迹</h4>
          <div class="flex items-center justify-between">
            <div>
              <div class="text-3xl font-bold t-heading">{{ planCount }}</div>
              <div class="text-xs t-text-muted">行程总数</div>
            </div>
            <div class="h-8 w-px" style="background: var(--border-color);"></div>
            <div>
              <div class="text-3xl font-bold t-heading">{{ cityCount }}</div>
              <div class="text-xs t-text-muted">打卡城市</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Recent Plans -->
      <div class="lg:col-span-2 animate-fade-in" style="animation-delay: 0.2s;">
        <div class="glass-panel rounded-2xl p-6 h-full min-h-[500px] flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-bold t-heading flex items-center gap-2">
              <i class="far fa-clock text-cyan-500"></i> 最近行程
            </h3>
            <button @click="router.push({ name: 'plans' })" class="text-sm t-text-sub hover:text-cyan-500 transition">
              查看全部 <i class="fas fa-chevron-right text-xs ml-1"></i>
            </button>
          </div>

          <div class="space-y-4 flex-1 overflow-y-auto pr-2">
            <div v-if="loading" class="text-center py-20 t-text-muted">
              <i class="fas fa-spinner fa-spin text-2xl mb-3"></i>
              <p>加载中...</p>
            </div>

            <div v-else-if="recentPlans.length === 0" class="text-center py-12 t-text-muted">
              <i class="fas fa-wind text-3xl mb-3 opacity-50"></i>
              <p>暂无行程，快去创建吧！</p>
            </div>

            <div
              v-else
              v-for="plan in recentPlans"
              :key="plan.id"
              @click="viewPlan(plan.id)"
              class="rounded-xl p-4 cursor-pointer transition flex items-center justify-between group"
              style="background: var(--bg-card); border: 1px solid var(--border-color);"
            >
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center text-cyan-500 font-bold text-sm" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
                  {{ (plan.days || []).length }}天
                </div>
                <div class="min-w-0">
                  <h4 class="font-bold t-text truncate group-hover:text-cyan-500 transition">{{ plan.title || '未命名行程' }}</h4>
                  <div class="text-xs t-text-muted flex items-center gap-2">
                    <span><i class="far fa-calendar-alt mr-1"></i> {{ new Date(plan.created_at || Date.now()).toLocaleDateString() }}</span>
                    <span>&bull;</span>
                    <span>{{ (plan.days || []).reduce((acc, d) => acc + (d.segments?.length || 0), 0) }} 个地点</span>
                  </div>
                </div>
              </div>
              <div class="t-text-muted group-hover:text-cyan-500 transition">
                <i class="fas fa-chevron-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
