<script setup>
import { computed } from 'vue'
import { formatDuration } from '@/utils/time'
import { getTransportIcon, getTransportLabel } from '@/utils/format'

const props = defineProps({
  segment: { type: Object, required: true },
  index: { type: Number, required: true },
})

const emit = defineEmits(['openDetail'])

const icon = computed(() => getTransportIcon(props.segment.type))
const label = computed(() => getTransportLabel(props.segment))

const isFlightOrTrain = computed(() => props.segment.type === 'flight' || props.segment.type === 'train')

const dep = computed(() => props.segment.details?.departure_time || props.segment.origin?.departure_time)
const arr = computed(() => props.segment.details?.arrival_time || props.segment.destination?.arrival_time)
const timeRange = computed(() => (dep.value && arr.value) ? `${dep.value} → ${arr.value}` : (dep.value || arr.value || ''))

const infoText = computed(() => {
  if (isFlightOrTrain.value && timeRange.value) return timeRange.value
  return props.segment.duration_minutes ? formatDuration(props.segment.duration_minutes * 60) : '--'
})

const distance = computed(() => props.segment.distance_km ? `${props.segment.distance_km}km` : '--')
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
