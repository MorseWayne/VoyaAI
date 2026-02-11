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
  <div class="max-w-7xl mx-auto px-4 pb-20">
    <!-- Hero Section -->
    <div class="mb-10 pt-10 text-center relative overflow-hidden rounded-3xl bg-gradient-to-br from-cyan-600 to-blue-700 text-white shadow-xl animate-fade-in">
       <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?ixlib=rb-4.0.3&auto=format&fit=crop&w=2021&q=80')] opacity-20 bg-cover bg-center"></div>
       <div class="relative z-10 py-16 px-6">
         <h1 class="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight">VoyaAI 智能旅行助手</h1>
         <p class="text-xl md:text-2xl opacity-90 mb-8 max-w-2xl mx-auto font-light">探索世界从未如此简单，AI 为您规划每一次难忘旅程</p>
         <button 
           @click="router.push({ name: 'create-plan' })"
           class="px-8 py-4 bg-white text-blue-600 rounded-full font-bold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center gap-2 mx-auto"
         >
           <span>立即开启旅程</span>
           <i class="fas fa-arrow-right"></i>
         </button>
       </div>
    </div>

    <!-- Feature Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10 animate-fade-in" style="animation-delay: 0.1s;">
      <!-- Smart Plan -->
      <div @click="router.push({ name: 'create-plan' })" class="group relative overflow-hidden rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <div class="w-12 h-12 rounded-xl bg-cyan-100 text-cyan-600 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-300">
          <i class="fas fa-magic"></i>
        </div>
        <h3 class="text-lg font-bold t-heading mb-2">智能规划</h3>
        <p class="t-text-sub text-sm">输入需求，一键生成完整行程攻略，省时省力。</p>
        <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-cyan-500">
          <i class="fas fa-arrow-right"></i>
        </div>
      </div>

      <!-- Route Optimizer -->
      <div @click="router.push({ name: 'planner' })" class="group relative overflow-hidden rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <div class="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-300">
          <i class="fas fa-route"></i>
        </div>
        <h3 class="text-lg font-bold t-heading mb-2">路线优化</h3>
        <p class="t-text-sub text-sm">多地点智能排序，计算最优路径，高效打卡。</p>
        <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-emerald-500">
          <i class="fas fa-arrow-right"></i>
        </div>
      </div>

      <!-- Travel Guides -->
      <div @click="router.push({ name: 'guides' })" class="group relative overflow-hidden rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <div class="w-12 h-12 rounded-xl bg-pink-100 text-pink-600 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-300">
          <i class="fas fa-book-open"></i>
        </div>
        <h3 class="text-lg font-bold t-heading mb-2">攻略合集</h3>
        <p class="t-text-sub text-sm">导入 Markdown 笔记，生成可视化精美攻略。</p>
        <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-pink-500">
          <i class="fas fa-arrow-right"></i>
        </div>
      </div>

      <!-- AI Assistant -->
      <div @click="router.push({ name: 'chat' })" class="group relative overflow-hidden rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl" style="background: var(--bg-card); border: 1px solid var(--border-color);">
        <div class="w-12 h-12 rounded-xl bg-violet-100 text-violet-600 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform duration-300">
          <i class="fas fa-robot"></i>
        </div>
        <h3 class="text-lg font-bold t-heading mb-2">AI 助手</h3>
        <p class="t-text-sub text-sm">随时待命的旅行问答向导，解答您的所有疑问。</p>
        <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-violet-500">
          <i class="fas fa-arrow-right"></i>
        </div>
      </div>
    </div>

    <!-- Dashboard Area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in" style="animation-delay: 0.2s;">
      <!-- Left: Stats -->
      <div class="col-span-1 space-y-6">
        <div class="glass-panel p-6 rounded-2xl h-full flex flex-col justify-center">
           <h3 class="text-lg font-bold t-heading mb-6 flex items-center gap-2">
            <i class="fas fa-chart-pie text-blue-500"></i> 旅行足迹
           </h3>
           <div class="grid grid-cols-2 gap-4 text-center">
             <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20">
               <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">{{ planCount }}</div>
               <div class="text-sm t-text-muted">行程总数</div>
             </div>
             <div class="p-4 rounded-xl bg-cyan-50 dark:bg-cyan-900/20">
               <div class="text-3xl font-bold text-cyan-600 dark:text-cyan-400 mb-1">{{ cityCount }}</div>
               <div class="text-sm t-text-muted">打卡城市</div>
             </div>
           </div>
        </div>
      </div>

      <!-- Right: Recent Plans -->
      <div class="col-span-1 lg:col-span-2">
        <div class="glass-panel rounded-2xl p-6 h-full min-h-[400px] flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-bold t-heading flex items-center gap-2">
              <i class="far fa-clock text-cyan-500"></i> 最近行程
            </h3>
            <button @click="router.push({ name: 'plans' })" class="text-sm t-text-sub hover:text-cyan-500 transition font-medium">
              查看全部 <i class="fas fa-chevron-right text-xs ml-1"></i>
            </button>
          </div>

          <div class="space-y-4 flex-1 overflow-y-auto pr-2 custom-scrollbar">
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
              class="rounded-xl p-4 cursor-pointer transition flex items-center justify-between group hover:shadow-md"
              style="background: var(--bg-card); border: 1px solid var(--border-color);"
            >
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-12 h-12 rounded-lg flex flex-col items-center justify-center text-cyan-600 bg-cyan-50 dark:bg-cyan-900/20 font-bold text-sm shrink-0">
                  <span class="text-lg leading-none">{{ (plan.days || []).length }}</span>
                  <span class="text-[10px] uppercase">Days</span>
                </div>
                <div class="min-w-0">
                  <h4 class="font-bold t-text truncate text-lg group-hover:text-cyan-500 transition mb-1">{{ plan.title || '未命名行程' }}</h4>
                  <div class="text-xs t-text-muted flex items-center gap-3">
                    <span class="flex items-center gap-1"><i class="far fa-calendar-alt"></i> {{ new Date(plan.created_at || Date.now()).toLocaleDateString() }}</span>
                    <span class="flex items-center gap-1"><i class="fas fa-map-marker-alt"></i> {{ (plan.days || []).reduce((acc, d) => acc + (d.segments?.length || 0), 0) }} 个地点</span>
                  </div>
                </div>
              </div>
              <div class="w-8 h-8 rounded-full flex items-center justify-center t-text-muted group-hover:bg-cyan-50 group-hover:text-cyan-500 transition">
                <i class="fas fa-chevron-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--text-muted);
}
</style>
