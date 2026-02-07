<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { usePlanStore } from '@/stores/plan'
import { savePlan } from '@/api/plans'
import { searchLocationTips } from '@/api/locations'

const router = useRouter()
const ui = useUIStore()
const planStore = usePlanStore()

const startDate = ref(new Date().toISOString().split('T')[0])
const totalDays = ref(1)
const searchKeyword = ref('')
const searchResults = ref([])
const selectedLocation = ref(null)
const showResults = ref(false)
const saving = ref(false)
let searchTimer = null

function handleSearch(keyword) {
  if (searchTimer) clearTimeout(searchTimer)
  if (!keyword.trim()) {
    showResults.value = false
    return
  }
  searchTimer = setTimeout(async () => {
    showResults.value = true
    searchResults.value = []
    try {
      searchResults.value = await searchLocationTips(keyword)
    } catch (e) {
      console.error(e)
    }
  }, 400)
}

function pickLocation(item) {
  selectedLocation.value = {
    name: item.name,
    address: item.address,
    city: item.city || item.district || '',
    lat: item.location ? parseFloat(item.location.split(',')[1]) : null,
    lng: item.location ? parseFloat(item.location.split(',')[0]) : null,
  }
  showResults.value = false
}

function clearLocation() {
  selectedLocation.value = null
  searchKeyword.value = ''
}

async function handleSubmit() {
  if (!selectedLocation.value) {
    ui.showToast('请先搜索并选择出发起点', 'error')
    return
  }

  saving.value = true
  const loc = selectedLocation.value
  const dateStr = new Date(startDate.value).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
  const cityName = loc.city || ''
  const title = cityName
    ? `${cityName} · ${dateStr}出发 · ${totalDays.value}日旅行`
    : `${dateStr}出发 · ${totalDays.value}日旅行`

  const days = []
  let currentDate = new Date(startDate.value)
  for (let i = 0; i < totalDays.value; i++) {
    days.push({
      day_index: i + 1,
      date: currentDate.toISOString().split('T')[0],
      city: loc.city || '',
      segments: [],
    })
    currentDate.setDate(currentDate.getDate() + 1)
  }

  const newPlan = {
    title,
    days,
    start_location: {
      name: loc.name, lat: loc.lat, lng: loc.lng, address: loc.address, city: loc.city,
    },
  }

  try {
    const plan = await savePlan(newPlan)
    ui.showToast('行程创建成功')
    planStore.activePlan = plan
    if (!planStore.activePlan.days) planStore.activePlan.days = []
    planStore.tempStartLocation = loc
    router.push({ name: 'plan-detail', params: { id: plan.id } })
  } catch (e) {
    ui.showToast('创建失败', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto mt-8">
    <div class="glass-panel rounded-2xl shadow-xl p-8 animate-fade-in">
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-3xl font-bold t-heading">创建新行程</h2>
        <button @click="router.push({ name: 'plans' })" class="t-text-muted hover:text-cyan-500 transition">
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <div class="space-y-6">
        <!-- Start Location Search -->
        <div class="relative">
          <label class="block text-sm font-bold t-text-sub uppercase tracking-wider mb-2">出发起点 <span class="text-red-400">*</span></label>
          <div v-if="!selectedLocation" class="relative">
            <i class="fas fa-location-dot absolute left-4 top-1/2 -translate-y-1/2 t-text-muted"></i>
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索出发地点（如酒店、火车站、小区）"
              class="w-full pl-11 pr-4 py-3 rounded-xl border outline-none transition"
              @input="handleSearch(searchKeyword)"
              autocomplete="off"
            >
          </div>
          <!-- Search results dropdown -->
          <div v-if="showResults && searchResults.length > 0" class="absolute z-10 left-0 right-0 rounded-xl shadow-lg mt-1 max-h-48 overflow-y-auto" style="background: var(--modal-bg); border: 1px solid var(--border-color);">
            <div
              v-for="(item, idx) in searchResults"
              :key="idx"
              @click="pickLocation(item)"
              class="px-4 py-2.5 cursor-pointer transition flex items-center gap-3"
              style="border-bottom: 1px solid var(--border-subtle);"
            >
              <i class="fas fa-map-pin t-text-muted flex-shrink-0"></i>
              <div class="min-w-0">
                <div class="font-medium text-sm t-text truncate">{{ item.name }}</div>
                <div class="text-xs t-text-muted truncate">{{ item.district || '' }} {{ item.address || '' }}</div>
              </div>
            </div>
          </div>
          <!-- Selected badge -->
          <div v-if="selectedLocation" class="mt-2 rounded-lg px-3 py-2 flex items-center justify-between" style="background: var(--nav-active-bg); border: 1px solid rgba(6,182,212,0.2);">
            <div class="flex items-center gap-2 min-w-0">
              <i class="fas fa-check-circle text-cyan-500 flex-shrink-0"></i>
              <span class="text-sm font-medium text-cyan-600 truncate">{{ selectedLocation.name }}</span>
            </div>
            <button @click="clearLocation" class="t-text-muted hover:text-red-500 transition text-sm flex-shrink-0 ml-2 cursor-pointer">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold t-text-sub uppercase tracking-wider mb-2">出发日期</label>
            <input v-model="startDate" type="date" class="w-full rounded-xl px-4 py-3 outline-none border transition">
          </div>
          <div>
            <label class="block text-sm font-bold t-text-sub uppercase tracking-wider mb-2">旅行天数</label>
            <input v-model.number="totalDays" type="number" min="1" max="30" class="w-full rounded-xl px-4 py-3 outline-none border transition font-bold text-center text-lg">
          </div>
        </div>

        <p class="text-xs t-text-muted leading-relaxed">
          <i class="fas fa-info-circle mr-1"></i> 设置出发起点后，可在行程编辑器中继续搜索添加游玩目的地
        </p>

        <button @click="handleSubmit" :disabled="saving" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transform hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2 disabled:opacity-50">
          <span>{{ saving ? '创建中...' : '创建并编辑' }}</span>
          <i :class="['fas', saving ? 'fa-spinner fa-spin' : 'fa-arrow-right']"></i>
        </button>
      </div>
    </div>
  </div>
</template>
