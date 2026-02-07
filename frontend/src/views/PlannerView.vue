<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { usePlanStore } from '@/stores/plan'
import { optimizeRoute } from '@/api/routes'
import { savePlan } from '@/api/plans'
import RouteResults from '@/components/planner/RouteResults.vue'

const router = useRouter()
const ui = useUIStore()
const planStore = usePlanStore()

const city = ref('')
const locationsText = ref('')
const strategy = ref('driving')
const preference = ref('time')
const loading = ref(false)
const error = ref('')
const resultData = ref(null)

async function handleOptimize() {
  const locations = locationsText.value.split('\n').map(l => l.trim()).filter(l => l)
  if (locations.length < 2) {
    alert('请至少输入两个地点')
    return
  }

  loading.value = true
  error.value = ''
  resultData.value = null

  try {
    const data = await optimizeRoute(locations, city.value.trim(), strategy.value, preference.value)
    planStore.currentPlanData = data
    resultData.value = data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!resultData.value) return
  const cityName = city.value.trim() || '未知城市'

  const plan = {
    title: `${cityName}精彩游玩路线`,
    days: [{
      day_index: 1,
      city: cityName,
      segments: resultData.value.segments.map((seg, idx) => {
        const originPoi = resultData.value.poi_details[idx]
        const destPoi = resultData.value.poi_details[idx + 1]
        const modeStr = (seg.mode || '').toString()
        let mode = 'driving'
        if (modeStr.includes('公交') || modeStr.includes('地铁') || modeStr.includes('Transit')) mode = 'transit'
        if (modeStr.includes('步行')) mode = 'walking'
        if (modeStr.includes('骑行')) mode = 'cycling'

        return {
          type: mode,
          origin: { name: originPoi.name, lat: originPoi.lat, lng: originPoi.lng, address: originPoi.address, city: cityName },
          destination: { name: destPoi.name, lat: destPoi.lat, lng: destPoi.lng, address: destPoi.address, city: cityName },
          distance_km: parseFloat(seg.distance_km),
          duration_minutes: parseFloat(seg.duration_m),
        }
      }),
    }],
  }

  try {
    await savePlan(plan)
    ui.showToast('行程已保存')
    setTimeout(() => router.push({ name: 'plans' }), 1000)
  } catch (e) {
    ui.showToast('保存失败: ' + e.message, 'error')
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-10 animate-fade-in">
      <h1 class="text-4xl font-bold t-heading mb-3">规划您的完美旅程</h1>
      <p class="t-text-sub text-lg">智能优化路线，让每一次出行都轻松愉悦</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Left: Input Form -->
      <div class="lg:col-span-4 glass-panel rounded-2xl shadow-xl p-6 md:p-8 animate-fade-in" style="animation-delay: 0.1s;">
        <div class="space-y-6">
          <div class="relative group">
            <label class="block text-xs font-bold t-text-muted uppercase tracking-wider mb-2">出发城市</label>
            <div class="relative">
              <i class="fas fa-city absolute left-4 top-1/2 -translate-y-1/2 t-text-muted group-focus-within:text-cyan-500 transition-colors"></i>
              <input v-model="city" type="text" placeholder="例如：广州" class="w-full pl-11 pr-4 py-3.5 rounded-xl border outline-none transition-all duration-300 font-medium">
            </div>
          </div>

          <div class="relative group">
            <label class="block text-xs font-bold t-text-muted uppercase tracking-wider mb-2">游玩地点 <span class="t-text-muted font-normal normal-case ml-1">(一行一个)</span></label>
            <div class="relative">
              <i class="fas fa-map-pin absolute left-4 top-5 t-text-muted group-focus-within:text-cyan-500 transition-colors"></i>
              <textarea v-model="locationsText" rows="6" placeholder="广州塔&#10;白云山&#10;长隆野生动物世界" class="w-full pl-11 pr-4 py-3.5 rounded-xl border outline-none transition-all duration-300 font-medium resize-none"></textarea>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold t-text-muted uppercase tracking-wider mb-2">出行方式</label>
              <div class="relative">
                <select v-model="strategy" class="w-full pl-4 pr-10 py-3 rounded-xl border outline-none transition-all appearance-none cursor-pointer font-medium">
                  <option value="driving">🚗 驾车出行</option>
                  <option value="walking">🚶 步行漫游</option>
                  <option value="transit">🚌 公交地铁</option>
                </select>
                <i class="fas fa-chevron-down absolute right-4 top-1/2 -translate-y-1/2 t-text-muted pointer-events-none"></i>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold t-text-muted uppercase tracking-wider mb-2">偏好设置</label>
              <div class="relative">
                <select v-model="preference" class="w-full pl-4 pr-10 py-3 rounded-xl border outline-none transition-all appearance-none cursor-pointer font-medium">
                  <option value="time">⚡ 时间最短</option>
                  <option value="distance">📏 距离最短</option>
                  <option value="avoid_highway">🛣️ 不走高速</option>
                </select>
                <i class="fas fa-chevron-down absolute right-4 top-1/2 -translate-y-1/2 t-text-muted pointer-events-none"></i>
              </div>
            </div>
          </div>

          <button @click="handleOptimize" :disabled="loading" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-4 px-6 rounded-xl shadow-lg shadow-cyan-500/30 transform hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 flex justify-center items-center gap-3 group disabled:opacity-50">
            <span class="group-hover:tracking-wider transition-all duration-300">{{ loading ? '规划中...' : '开始智能规划' }}</span>
            <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-wand-magic-sparkles group-hover:rotate-12 transition-transform duration-300']"></i>
          </button>
        </div>
      </div>

      <!-- Right: Results -->
      <div class="lg:col-span-8 glass-panel rounded-2xl shadow-xl p-6 md:p-8 min-h-[500px] flex flex-col animate-fade-in relative overflow-hidden" style="animation-delay: 0.2s;">
        <!-- Loading -->
        <div v-if="loading" class="flex-grow flex flex-col justify-center items-center text-center">
          <i class="fas fa-compass fa-spin text-5xl text-primary mb-4"></i>
          <p class="text-xl t-text-sub">正在为您规划最佳路线...</p>
          <p class="text-sm t-text-muted mt-2">正在计算距离和时间</p>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex-grow flex flex-col justify-center items-center text-center text-red-500">
          <i class="fas fa-exclamation-circle text-5xl mb-4"></i>
          <p class="text-xl">规划出错</p>
          <p class="mt-2">{{ error }}</p>
        </div>

        <!-- Results -->
        <RouteResults v-else-if="resultData" :data="resultData" @save="handleSave" />

        <!-- Empty State -->
        <div v-else class="flex-grow flex flex-col justify-center items-center t-text-muted text-center p-8">
          <div class="w-32 h-32 rounded-full flex items-center justify-center mb-6 shadow-inner" style="background: var(--bg-inset);">
            <i class="fas fa-map-location-dot text-6xl t-text-muted"></i>
          </div>
          <h3 class="text-xl font-bold t-text-sub mb-2">等待规划</h3>
          <p class="t-text-muted max-w-xs mx-auto">在左侧输入您想去的地点，我们将为您生成最佳游玩路线。</p>
        </div>

        <!-- Decoration -->
        <div class="absolute -top-24 -right-24 w-64 h-64 bg-cyan-400/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-64 h-64 bg-blue-400/10 rounded-full blur-3xl pointer-events-none"></div>
      </div>
    </div>
  </div>
</template>
