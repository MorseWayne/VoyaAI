<script setup>
const props = defineProps({
  data: { type: Object, required: true },
})
const emit = defineEmits(['save'])

const totalDuration = parseFloat(props.data.total_duration_hours) * 60
const totalDist = props.data.total_distance_km
</script>

<template>
  <div class="w-full p-6 rounded-xl shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
    <h3 class="text-xl font-bold t-heading mb-4 flex justify-between items-center">
      <span>规划结果</span>
      <div class="flex items-center gap-2">
        <span class="text-sm font-normal t-text-sub px-3 py-1 rounded-full" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
          总程: {{ totalDist }}km / 约 {{ Math.round(totalDuration) }}分钟
        </span>
        <button @click="emit('save')" class="text-sm bg-primary text-white px-3 py-2 rounded-lg hover:bg-cyan-600 transition flex items-center shadow-sm">
          <i class="fas fa-plus mr-1"></i> 保存行程
        </button>
      </div>
    </h3>

    <div class="relative ml-4 pl-8 space-y-8" style="border-left: 4px solid var(--border-color);">
      <div v-for="(loc, index) in data.poi_details" :key="index" class="relative">
        <div class="absolute -left-[42px] text-cyan-500 w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-md" style="background: var(--bg-elevated); border: 2px solid var(--border-color);">
          {{ index + 1 }}
        </div>
        <div class="p-4 rounded-lg transition" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
          <h4 class="font-bold text-lg t-text">{{ loc.name }}</h4>
          <p class="text-sm t-text-muted mt-1"><i class="fas fa-map-marker-alt mr-1"></i> {{ loc.address || '地址未知' }}</p>
        </div>
        <div v-if="index < data.poi_details.length - 1 && data.segments[index]" class="mt-4 mb-2 text-sm t-text-sub pl-2 flex items-center gap-2">
          <i class="fas fa-arrow-down text-cyan-500"></i>
          <span>约 {{ data.segments[index].duration_m }}分钟</span>
          <span class="t-text-muted">|</span>
          <span>{{ data.segments[index].distance_km }}km</span>
          <span class="t-text-muted">|</span>
          <span class="text-xs t-text-sub px-2 py-0.5 rounded" style="background: var(--bg-inset); border: 1px solid var(--border-color);">{{ data.segments[index].mode }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
