<script setup>
import { computed } from 'vue'
import { formatDuration, durationSecondsFromTimes } from '@/utils/time'
import { getTransportIcon, getTransportLabel, inferSegmentDisplayType } from '@/utils/format'

const props = defineProps({
  segment: { type: Object, required: true },
  index: { type: Number, required: true },
})

const emit = defineEmits(['openDetail'])

const icon = computed(() => getTransportIcon(props.segment))
const label = computed(() => getTransportLabel(props.segment))

const displayType = computed(() => inferSegmentDisplayType(props.segment))
const isFlightOrTrain = computed(() => displayType.value === 'flight' || displayType.value === 'train')

const dep = computed(() => props.segment.details?.departure_time || props.segment.origin?.departure_time)
const arr = computed(() => props.segment.details?.arrival_time || props.segment.destination?.arrival_time)
const timeRange = computed(() => (dep.value && arr.value) ? `${dep.value} → ${arr.value}` : (dep.value || arr.value || ''))

/** 优先用起降时间计算时长；若存了错误的大数值 duration_minutes 则用时间差覆盖 */
const durationSeconds = computed(() => {
  if (dep.value && arr.value) {
    const s = durationSecondsFromTimes(dep.value, arr.value)
    if (s > 0) return s
  }
  return props.segment.duration_minutes != null ? props.segment.duration_minutes * 60 : null
})

const infoText = computed(() => {
  if (isFlightOrTrain.value && timeRange.value) return timeRange.value
  return durationSeconds.value != null ? formatDuration(durationSeconds.value) : '--'
})

const distance = computed(() => {
  if (props.segment.distance_km != null && props.segment.distance_km > 0) return `${props.segment.distance_km}km`
  if (isFlightOrTrain.value) return '—'
  return '--'
})
</script>

<template>
  <div class="transport-connector-row">
    <!-- Align with timeline rail -->
    <div class="timeline-rail-spacer">
      <div class="timeline-line-through"></div>
    </div>
    <!-- Connector badge -->
    <div class="flex-1 min-w-0 py-1">
      <div @click="emit('openDetail', index)" class="transport-badge group/conn" title="点击查看详情">
        <i :class="['fas', icon, 'text-xs']"></i>
        <span class="font-semibold">{{ label }}</span>
        <span class="transport-badge-divider"></span>
        <span class="font-mono text-[11px] opacity-80">{{ infoText }}</span>
        <span class="font-mono text-[11px] opacity-60 ml-0.5">({{ distance }})</span>
        <i class="fas fa-chevron-right text-[10px] opacity-40 ml-1 group-hover/conn:opacity-100 transition-opacity"></i>
      </div>
    </div>
  </div>
</template>
