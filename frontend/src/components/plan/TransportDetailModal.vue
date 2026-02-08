<script setup>
import { computed } from 'vue'
import { formatDuration, durationSecondsFromTimes } from '@/utils/time'
import { getTransportIcon, inferSegmentDisplayType } from '@/utils/format'

const props = defineProps({
  show: Boolean,
  segment: { type: Object, default: null },
})

const emit = defineEmits(['close', 'change'])

const displayType = computed(() => inferSegmentDisplayType(props.segment))
const icon = computed(() => getTransportIcon(props.segment))

const typeLabel = computed(() => {
  if (!props.segment) return '驾车'
  const s = props.segment
  const labels = {
    driving: '驾车',
    transit: (s.details?.display_label === '城际交通') ? '城际交通' : '公交/地铁',
    walking: '步行',
    cycling: '骑行',
    flight: s.details?.flight_no || '航班',
    train: s.details?.train_no || '高铁/火车',
  }
  return labels[displayType.value] || '驾车'
})

const dep = computed(() => props.segment?.details?.departure_time || props.segment?.origin?.departure_time)
const arr = computed(() => props.segment?.details?.arrival_time || props.segment?.destination?.arrival_time)
const durationSeconds = computed(() => {
  if (dep.value && arr.value) {
    const s = durationSecondsFromTimes(dep.value, arr.value)
    if (s > 0) return s
  }
  return props.segment?.duration_minutes != null ? props.segment.duration_minutes * 60 : null
})
const duration = computed(() => durationSeconds.value != null ? formatDuration(durationSeconds.value) : '--')
const distance = computed(() => {
  if (props.segment?.distance_km != null && props.segment.distance_km > 0) return `${props.segment.distance_km} km`
  if (displayType.value === 'flight' || displayType.value === 'train') return '—'
  return '--'
})
const originName = computed(() => props.segment?.origin?.name || '起点')
const destName = computed(() => props.segment?.destination?.name || '终点')
const isFlightOrTrain = computed(() => displayType.value === 'flight' || displayType.value === 'train')
const isImportedFixed = computed(() => (props.segment?.type === 'flight' && props.segment?.details?.flight_no) || (props.segment?.type === 'train' && props.segment?.details?.train_no))
</script>

<template>
  <Teleport to="body">
    <div v-if="show && segment" class="fixed inset-0 z-[61]">
      <div class="absolute inset-0 backdrop-blur-sm" style="background: var(--modal-overlay);" @click="emit('close')"></div>
      <div class="absolute bottom-0 left-0 right-0 md:top-1/2 md:left-1/2 md:bottom-auto md:-translate-x-1/2 md:-translate-y-1/2 md:w-[400px] max-h-[90vh] overflow-y-auto md:rounded-2xl rounded-t-2xl shadow-2xl p-6" style="background: var(--modal-bg);" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold t-heading">交通方式详情</h3>
          <button type="button" @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full t-text-sub transition" style="background: var(--bg-inset);">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="t-text-sub text-sm space-y-3 mb-6">
          <div class="py-1.5" style="border-bottom: 1px solid var(--border-subtle);">
            <div class="flex items-center gap-2 font-medium" style="color: var(--text-primary);">
              <i :class="['fas', icon, 'text-cyan-600']"></i> {{ typeLabel }}
            </div>
          </div>
          <div class="py-1.5 flex justify-between" style="border-bottom: 1px solid var(--border-subtle);">
            <span class="t-text-muted">起点</span><span>{{ originName }}</span>
          </div>
          <div class="py-1.5 flex justify-between" style="border-bottom: 1px solid var(--border-subtle);">
            <span class="t-text-muted">终点</span><span>{{ destName }}</span>
          </div>
          <div v-if="isFlightOrTrain && (dep || arr)" class="py-1.5 flex justify-between" style="border-bottom: 1px solid var(--border-subtle);">
            <span class="t-text-muted">时间</span><span>{{ dep || '--' }} → {{ arr || '--' }}</span>
          </div>
          <div v-if="isFlightOrTrain && segment.details?.seat_info" class="py-1.5 flex justify-between" style="border-bottom: 1px solid var(--border-subtle);">
            <span class="t-text-muted">座位</span><span>{{ segment.details.seat_info }}</span>
          </div>
          <div class="py-1.5 flex justify-between" style="border-bottom: 1px solid var(--border-subtle);">
            <span class="t-text-muted">时长</span><span>{{ duration }}</span>
          </div>
          <div class="py-1.5 flex justify-between">
            <span class="t-text-muted">距离</span><span>{{ distance }}</span>
          </div>
        </div>

        <button
          v-if="!isImportedFixed"
          type="button"
          class="w-full py-3 rounded-xl border-2 border-cyan-500 text-cyan-600 font-medium transition"
          @click="emit('change')"
        >
          <i class="fas fa-exchange-alt mr-2"></i> 更改交通方式
        </button>
      </div>
    </div>
  </Teleport>
</template>
