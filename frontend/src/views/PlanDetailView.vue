<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlanStore } from '@/stores/plan'
import { useUIStore } from '@/stores/ui'
import { fetchPlan, deletePlan } from '@/api/plans'
import { ensureDayStayArray, getDayArrivalTimes } from '@/utils/time'
import { useLocationDrag } from '@/composables/useLocationDrag'
import DayTabs from '@/components/plan/DayTabs.vue'
import DayOverview from '@/components/plan/DayOverview.vue'
import LocationCard from '@/components/plan/LocationCard.vue'
import TransportConnector from '@/components/plan/TransportConnector.vue'
import TransportDropdown from '@/components/plan/TransportDropdown.vue'
import TransportDetailModal from '@/components/plan/TransportDetailModal.vue'
import AddLocationModal from '@/components/modals/AddLocationModal.vue'
import TicketImportModal from '@/components/modals/TicketImportModal.vue'

const route = useRoute()
const router = useRouter()
const planStore = usePlanStore()
const ui = useUIStore()
const { dragIndex, dragOverIndex, onDragStart, onDragOver, onDragLeave, onDrop, onDragEnd } = useLocationDrag({ enabled: false })

const loading = ref(true)

// Modal states
const showAddModal = ref(false)
const addInsertIndex = ref(null)
const addModalMode = ref('add') // 'add' | 'replaceStart'
const showTicketModal = ref(false)
const showTransportDetail = ref(false)
const transportDetailSegment = ref(null)
const transportDetailIndex = ref(-1)
const showTransportDropdown = ref(false)
const transportDropdownRect = ref(null)
const transportDropdownSegIndex = ref(-1)
/** When set, ticket modal is in "replace this segment with flight" mode; must upload flight ticket. */
const flightTicketReplaceSegIndex = ref(null)

// Auto-save timer
let saveTimer = null

// Plan metadata
const plan = computed(() => planStore.activePlan)
const days = computed(() => plan.value?.days || [])
const isOverview = computed(() => planStore.activeDetailTab === 'overview')
const currentDayIndex = computed(() => planStore.getCurrentDayIndex())
const currentDay = computed(() => days.value[currentDayIndex.value] || null)
const currentSegments = computed(() => currentDay.value?.segments || [])

// Compute arrival times for current day
const arrivalTimes = computed(() => {
  if (!currentDay.value) return []
  ensureDayStayArray(currentDay.value)
  return getDayArrivalTimes(currentDay.value)
})

// Has content in timeline view
const hasLocations = computed(() => {
  return currentSegments.value.length > 0 || planStore.tempStartLocation
})

// Load the plan on mount
onMounted(async () => {
  try {
    const id = route.params.id
    if (planStore.activePlan?.id === id) {
      // already loaded
    } else {
      const data = await fetchPlan(id)
      planStore.activePlan = data
    }
    planStore.activeDetailTab = 0
    // Ensure stay arrays exist
    plan.value?.days?.forEach(d => ensureDayStayArray(d))
    planStore.syncTempStartLocationForCurrentDay()
  } catch (e) {
    ui.showToast('加载行程失败', 'error')
    router.push({ name: 'plans' })
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (saveTimer) clearTimeout(saveTimer)
})

// 切换日期时，当天的起点继承上一天终点（或已保存的当日起点）
watch(
  () => planStore.activeDetailTab,
  () => {
    if (!plan.value?.days?.length) return
    planStore.syncTempStartLocationForCurrentDay()
  },
  { immediate: false },
)

// Auto-save on changes
watch(
  () => plan.value,
  () => {
    if (!plan.value || loading.value) return
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(() => planStore.saveActivePlanSilently(), 2000)
  },
  { deep: true },
)

// --- Handlers ---

function updateDepartureDate(e) {
  planStore.updatePlanDepartureDate(e.target.value)
}

function updateDaysCount(e) {
  const n = parseInt(e.target.value, 10) || 1
  planStore.updatePlanDaysCount(n)
}

function updateStartTimeHm(e) {
  if (currentDay.value) {
    currentDay.value.start_time_hm = e.target.value || '08:00'
  }
}

function updateStay(dayIndex, locationIndex, val) {
  const day = days.value[dayIndex]
  if (!day) return
  ensureDayStayArray(day)
  if (day.location_stay_minutes[locationIndex] !== undefined) {
    day.location_stay_minutes[locationIndex] = val
  }
}

// Add location via modal
function openAddModal(insertIndex = null) {
  addModalMode.value = 'add'
  addInsertIndex.value = insertIndex
  showAddModal.value = true
}

function openReplaceStartModal() {
  addModalMode.value = 'replaceStart'
  addInsertIndex.value = null
  showAddModal.value = true
}

async function handleReplaceStart(loc) {
  showAddModal.value = false
  const dayIdx = currentDayIndex.value
  if (!loc.city && plan.value.start_location?.city) loc.city = plan.value.start_location.city
  planStore.setDayStartLocation(dayIdx, loc)
  planStore.tempStartLocation = { ...loc }
  ui.showToast('当日起点已更新')
}

async function handleLocationSelectFromModal(loc) {
  if (addModalMode.value === 'replaceStart') {
    await handleReplaceStart(loc)
    addModalMode.value = 'add'
    return
  }
  await handleAddLocation(loc)
}

async function handleAddLocation(loc) {
  showAddModal.value = false

  const dayIdx = currentDayIndex.value
  const segs = days.value[dayIdx].segments

  if (!loc.city && plan.value.start_location?.city) {
    loc.city = plan.value.start_location.city
  }

  // If this is the very first location (tempStartLocation empty, no segments)
  if (segs.length === 0 && !planStore.tempStartLocation) {
    planStore.tempStartLocation = loc
    if (dayIdx === 0) {
      plan.value.start_location = { name: loc.name, lat: loc.lat, lng: loc.lng, address: loc.address, city: loc.city }
    }
    ui.showToast('起点设置成功')
    return
  }

  // If we only have a temp start location, add first segment
  if (segs.length === 0 && planStore.tempStartLocation) {
    await planStore.addSegment(planStore.tempStartLocation, loc)
    planStore.tempStartLocation = null
    ui.showToast('地点已添加')
    return
  }

  // Insert at specific index or append
  if (addInsertIndex.value !== null) {
    await planStore.insertSegmentAt(addInsertIndex.value, loc)
    ui.showToast('地点已插入')
    return
  }

  // Append to end
  const lastDest = segs[segs.length - 1].destination
  await planStore.addSegment(lastDest, loc)
  ui.showToast('地点已添加')
}

async function handleRemoveLocation(index, isLast) {
  if (!confirm('确定要删除这个地点吗？')) return
  await planStore.removeLocation(index, isLast)
  ui.showToast('地点已删除')
}

// Transport detail modal
function openTransportDetail(index) {
  transportDetailIndex.value = index
  transportDetailSegment.value = currentSegments.value[index]
  showTransportDetail.value = true
}

function onTransportChange() {
  showTransportDetail.value = false
  if (transportDetailIndex.value >= 0) {
    openTransportDropdown(transportDetailIndex.value)
  }
}

function openTransportDropdown(segIndex) {
  const el = document.querySelector(`[data-seg-idx="${segIndex}"]`)
  const rect = el?.getBoundingClientRect() || { top: 200, left: 200, bottom: 240, right: 300 }
  transportDropdownRect.value = rect
  transportDropdownSegIndex.value = segIndex
  showTransportDropdown.value = true
}

async function onTransportModeSelect(mode) {
  const segIndex = transportDropdownSegIndex.value
  showTransportDropdown.value = false
  if (segIndex < 0) return
  if (mode === 'flight') {
    flightTicketReplaceSegIndex.value = segIndex
    showTicketModal.value = true
    return
  }
  try {
    await planStore.changeTransportMode(segIndex, mode)
    ui.showToast('交通方式已更新')
  } catch {
    ui.showToast('切换交通方式失败', 'error')
  }
}

// Ticket import
function openTicketImport() {
  flightTicketReplaceSegIndex.value = null
  showAddModal.value = false
  showTicketModal.value = true
}

function onTicketModalClose() {
  showTicketModal.value = false
  flightTicketReplaceSegIndex.value = null
}

async function handleTicketImported(data) {
  if (flightTicketReplaceSegIndex.value !== null) {
    planStore.replaceSegmentWithTicketData(flightTicketReplaceSegIndex.value, data)
    flightTicketReplaceSegIndex.value = null
    showTicketModal.value = false
    ui.showToast('已更新为航班')
    return
  }
  showTicketModal.value = false
  const dayIdx = currentDayIndex.value
  const segs = days.value[dayIdx].segments

  const originLoc = {
    name: data.departure_station || data.departure_city || '出发地',
    city: data.departure_city || '',
    departure_time: data.departure_time,
  }
  const destLoc = {
    name: data.arrival_station || data.arrival_city || '目的地',
    city: data.arrival_city || '',
    arrival_time: data.arrival_time,
  }

  const durationMin = data.duration_seconds ? Math.round(data.duration_seconds / 60) : 0

  const newSeg = {
    type: data.type || 'train',
    origin: originLoc,
    destination: destLoc,
    distance_km: data.distance_km || 0,
    duration_minutes: durationMin,
    details: {
      flight_no: data.flight_no,
      train_no: data.train_no,
      departure_time: data.departure_time,
      arrival_time: data.arrival_time,
      seat_info: data.seat_info,
    },
  }

  segs.push(newSeg)
  ensureDayStayArray(days.value[dayIdx])
  ui.showToast('票据已导入')
  planStore.saveActivePlanSilently()
}

async function handleSave() {
  try {
    await planStore.saveActivePlan()
    ui.showToast('行程已保存')
  } catch (e) {
    ui.showToast('保存失败', 'error')
  }
}

async function handleDelete() {
  if (!confirm('确定要删除整个行程吗？此操作不可恢复。')) return
  try {
    await deletePlan(plan.value.id)
    ui.showToast('行程已删除')
    router.push({ name: 'plans' })
  } catch {
    ui.showToast('删除失败', 'error')
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-20 t-text-muted animate-fade-in">
      <i class="fas fa-spinner fa-spin text-4xl text-cyan-500 mb-4"></i>
      <p class="text-lg">加载行程...</p>
    </div>

    <!-- Plan Loaded -->
    <div v-else-if="plan" class="animate-fade-in">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <div class="flex items-center gap-3 mb-1">
            <button @click="router.push({ name: 'plans' })" class="t-text-muted hover:text-cyan-500 transition">
              <i class="fas fa-arrow-left mr-1"></i> 返回
            </button>
          </div>
          <h1 class="text-2xl font-bold t-heading">{{ plan.title || '未命名行程' }}</h1>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button @click="handleSave" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition flex items-center gap-2 font-medium text-sm">
            <i class="fas fa-save"></i> 保存
          </button>
          <button @click="handleDelete" class="px-4 py-2 rounded-lg border transition t-text-sub hover:text-red-500 hover:border-red-400 text-sm" style="border-color: var(--border-color);">
            <i class="fas fa-trash-alt mr-1"></i> 删除
          </button>
        </div>
      </div>

      <!-- Metadata Bar -->
      <div class="glass-panel rounded-xl p-4 mb-6 flex flex-wrap gap-4 items-center">
        <div class="flex items-center gap-2">
          <i class="far fa-calendar-alt text-cyan-500"></i>
          <label class="text-xs t-text-muted font-medium">出发日期</label>
          <input
            type="date"
            :value="days[0]?.date || ''"
            class="rounded-lg px-3 py-1.5 text-sm border outline-none"
            @change="updateDepartureDate"
          >
        </div>
        <div class="flex items-center gap-2">
          <i class="fas fa-hashtag text-cyan-500"></i>
          <label class="text-xs t-text-muted font-medium">天数</label>
          <input
            type="number"
            :value="days.length"
            min="1"
            max="30"
            class="w-16 rounded-lg px-3 py-1.5 text-sm border outline-none text-center"
            @change="updateDaysCount"
          >
        </div>
        <div v-if="!isOverview" class="flex items-center gap-2">
          <i class="far fa-clock text-cyan-500"></i>
          <label class="text-xs t-text-muted font-medium">当日出发时间</label>
          <input
            type="time"
            :value="currentDay?.start_time_hm || '08:00'"
            class="rounded-lg px-3 py-1.5 text-sm border outline-none"
            @change="updateStartTimeHm"
          >
        </div>
      </div>

      <!-- Day Tabs -->
      <DayTabs :days="days" />

      <!-- Overview -->
      <DayOverview v-if="isOverview" :days="days" />

      <!-- Day Detail -->
      <div v-else class="max-w-3xl mx-auto">
        <!-- Timeline List View -->
        <div v-if="hasLocations" class="space-y-0">
          <!-- Temp start point if present -->
          <LocationCard
            v-if="currentSegments.length === 0 && planStore.tempStartLocation"
            :location="planStore.tempStartLocation"
            :index="0"
            :is-last="true"
            :role-label="currentDayIndex === 0 ? '起点' : '起点'"
            :arrival-hm="arrivalTimes[0]?.arrivalHm || '--'"
            :stay-minutes="arrivalTimes[0]?.stayMinutes || 0"
            :departure-hm="arrivalTimes[0]?.departureHm"
            :day-index="currentDayIndex"
            :can-edit-start="true"
            @insert="openAddModal"
            @edit-start="openReplaceStartModal"
            @remove="handleRemoveLocation"
            @update-stay="updateStay"
          />

          <!-- Segments loop -->
          <template v-for="(seg, i) in currentSegments" :key="i">
            <div
              draggable="false"
              @dragstart="onDragStart($event, i)"
              @dragover="onDragOver($event, i)"
              @dragleave="onDragLeave"
              @drop="onDrop($event, i, currentDayIndex)"
              @dragend="onDragEnd"
              :class="{ 'opacity-50': dragIndex === i, 'ring-2 ring-cyan-400 rounded-xl': dragOverIndex === i }"
            >
              <LocationCard
                :location="seg.origin"
                :index="i"
                :is-last="false"
                :role-label="(i === 0 && currentDayIndex === 0) ? '起点' : (i === 0 ? '起点' : null)"
                :arrival-hm="arrivalTimes[i]?.arrivalHm || '--'"
                :stay-minutes="arrivalTimes[i]?.stayMinutes || 0"
                :departure-hm="arrivalTimes[i]?.departureHm"
                :day-index="currentDayIndex"
                :can-edit-start="i === 0"
                @insert="openAddModal"
                @edit-start="openReplaceStartModal"
                @remove="handleRemoveLocation"
                @update-stay="updateStay"
              />
            </div>

            <div :data-seg-idx="i">
              <TransportConnector :segment="seg" :index="i" @open-detail="openTransportDetail(i)" />
            </div>
          </template>

          <!-- Last destination -->
          <div
            v-if="currentSegments.length > 0"
            draggable="false"
            @dragstart="onDragStart($event, currentSegments.length)"
            @dragover="onDragOver($event, currentSegments.length)"
            @dragleave="onDragLeave"
            @drop="onDrop($event, currentSegments.length, currentDayIndex)"
            @dragend="onDragEnd"
            :class="{ 'opacity-50': dragIndex === currentSegments.length, 'ring-2 ring-cyan-400 rounded-xl': dragOverIndex === currentSegments.length }"
          >
            <LocationCard
              :location="currentSegments[currentSegments.length - 1].destination"
              :index="currentSegments.length"
              :is-last="true"
              role-label="终点"
              :arrival-hm="arrivalTimes[currentSegments.length]?.arrivalHm || '--'"
              :stay-minutes="arrivalTimes[currentSegments.length]?.stayMinutes || 0"
              :departure-hm="arrivalTimes[currentSegments.length]?.departureHm"
              :day-index="currentDayIndex"
              @insert="openAddModal"
              @remove="handleRemoveLocation"
              @update-stay="updateStay"
            />
          </div>
        </div>

        <!-- Add Button -->
        <div class="mt-6 text-center">
          <button type="button" @click="openAddModal(null)" class="px-6 py-3 border-2 border-dashed border-cyan-400/50 rounded-xl text-cyan-500 hover:bg-cyan-500/10 hover:border-cyan-400 transition flex items-center gap-2 mx-auto">
            <i class="fas fa-plus"></i> 添加下一站目的地
          </button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddLocationModal
      :show="showAddModal"
      :title="addModalMode === 'replaceStart' ? '修改当日起点' : '添加行程地点'"
      :city="currentDay?.city || ''"
      :insert-at-index="addInsertIndex"
      @close="showAddModal = false"
      @select="handleLocationSelectFromModal"
      @open-ticket-import="openTicketImport"
    />

    <TicketImportModal
      :show="showTicketModal"
      :title="flightTicketReplaceSegIndex !== null ? '上传机票截图' : '导入航班 / 车票'"
      :expect-flight-only="flightTicketReplaceSegIndex !== null"
      @close="onTicketModalClose"
      @imported="handleTicketImported"
    />

    <TransportDetailModal
      :show="showTransportDetail"
      :segment="transportDetailSegment"
      @close="showTransportDetail = false"
      @change="onTransportChange"
    />

    <TransportDropdown
      v-if="showTransportDropdown"
      :show="showTransportDropdown"
      :trigger-rect="transportDropdownRect"
      @select="onTransportModeSelect"
      @close="showTransportDropdown = false"
    />
  </div>
</template>
