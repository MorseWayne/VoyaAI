<script setup>
import { usePlanStore } from '@/stores/plan'

defineProps({
  days: { type: Array, required: true },
})

const planStore = usePlanStore()
</script>

<template>
  <div class="space-y-4">
    <div
      v-for="(day, dayIdx) in days"
      :key="dayIdx"
      @click="planStore.activeDetailTab = dayIdx"
      class="rounded-xl p-4 cursor-pointer transition group"
      style="background: var(--bg-card); border: 1px solid var(--border-color);"
    >
      <div class="flex justify-between items-center">
        <span class="font-bold t-text group-hover:text-cyan-500 transition">第 {{ dayIdx + 1 }} 天</span>
        <span class="text-sm t-text-muted">
          {{ day.date ? new Date(day.date).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' }) : `第 ${dayIdx + 1} 天` }}
        </span>
      </div>
      <p class="text-sm t-text-sub mt-1">{{ (day.segments || []).length > 0 ? (day.segments.length + 1) : 0 }} 个地点</p>
    </div>
  </div>
</template>
