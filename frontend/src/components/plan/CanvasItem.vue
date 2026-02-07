<script setup>
import { computed } from 'vue'
import { minutesToHm } from '@/utils/time'

const props = defineProps({
  location: { type: Object, default: null },
  index: { type: Number, required: true },
  isLast: { type: Boolean, default: false },
  roleLabel: { type: String, default: null },
  timeData: { type: Object, default: null },
  dayIndex: { type: Number, default: 0 },
  pos: { type: Object, default: () => ({ x: 0, y: 0 }) },
})

const emit = defineEmits(['remove', 'updateStay'])

const name = computed(() => props.location?.name || '未知地点')
const address = computed(() => props.location?.address || props.location?.city || '')
const arrivalHm = computed(() => props.timeData?.arrivalHm || '--')
const departureHm = computed(() => props.timeData?.departureHm || '--')
const stayMinutes = computed(() => props.timeData?.stayMinutes || 0)

const roleClass = computed(() => {
  if (props.roleLabel === '起点') return 'is-start'
  if (props.roleLabel === '终点') return 'is-end'
  return ''
})

function onStayChange(e) {
  emit('updateStay', props.dayIndex, props.index, parseInt(e.target.value, 10) || 0)
}
</script>

<template>
  <div
    :id="`snake-item-${dayIndex}-${index}`"
    class="snake-item absolute transition-shadow duration-200"
    :style="{ left: pos.x + 'px', top: pos.y + 'px', width: '260px', cursor: 'grab' }"
  >
    <div :class="['flow-card h-full select-none', roleClass]">
      <!-- Top Actions -->
      <div class="absolute top-2 right-2 opacity-0 hover:opacity-100 transition-opacity z-20 flex gap-1">
        <button @mousedown.stop @click="emit('remove', index, isLast)" class="w-6 h-6 rounded-full t-text-muted hover:bg-rose-500 hover:text-white flex items-center justify-center transition" style="background: var(--bg-elevated);" title="删除">
          <i class="fas fa-times text-xs"></i>
        </button>
      </div>

      <div class="flow-card-header">
        <div class="mr-2 transition-colors flex items-center h-8" style="color: var(--flow-handle-text);">
          <i class="fas fa-arrows-alt"></i>
        </div>
        <div class="flow-card-icon">
          <i v-if="roleLabel === '起点'" class="fas fa-map-marker-alt text-emerald-500"></i>
          <i v-else-if="roleLabel === '终点'" class="fas fa-flag-checkered text-rose-500"></i>
          <span v-else class="font-mono font-bold t-text-muted">{{ index + 1 }}</span>
        </div>
        <div class="min-w-0 flex-1">
          <div class="flow-card-title truncate" :title="name">{{ name }}</div>
          <div class="flow-card-meta truncate" :title="address">{{ address }}</div>
        </div>
      </div>

      <div class="flow-time-grid mt-2">
        <div class="flow-time-item">
          <div class="flow-time-label">到达</div>
          <div class="flow-time-val">{{ arrivalHm }}</div>
        </div>
        <div class="flow-time-item flex flex-col justify-center" @mousedown.stop>
          <div class="flow-time-label">停留</div>
          <div class="flex items-center justify-center rounded px-1" style="background: var(--flow-time-grid-bg);">
            <input
              type="number"
              :value="stayMinutes"
              min="0"
              step="15"
              class="flow-time-input"
              @change="onStayChange"
            >
            <span class="text-[9px] t-text-muted font-medium">m</span>
          </div>
        </div>
        <div class="flow-time-item">
          <div class="flow-time-label">离开</div>
          <div class="flow-time-val">{{ departureHm }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
