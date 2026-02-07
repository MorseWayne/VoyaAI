<script setup>
import { usePlanStore } from '@/stores/plan'

const planStore = usePlanStore()

defineProps({
  days: { type: Array, required: true },
})
</script>

<template>
  <div class="mb-4" style="border-bottom: 1px solid var(--border-color);">
    <div class="flex gap-2 overflow-x-auto py-2 -mx-1 px-1 min-h-[44px] items-center">
      <button
        type="button"
        @click="planStore.activeDetailTab = 'overview'"
        class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition whitespace-nowrap"
        :class="planStore.activeDetailTab === 'overview' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20' : 't-text-sub'"
        :style="planStore.activeDetailTab !== 'overview' ? 'background: var(--bg-card); border: 1px solid var(--border-color);' : ''"
      >
        总览
      </button>
      <button
        v-for="(day, i) in days"
        :key="i"
        type="button"
        @click="planStore.activeDetailTab = i"
        class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition whitespace-nowrap"
        :class="planStore.activeDetailTab === i ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20' : 't-text-sub'"
        :style="planStore.activeDetailTab !== i ? 'background: var(--bg-card); border: 1px solid var(--border-color);' : ''"
      >
        第 {{ i + 1 }} 天
      </button>
    </div>
  </div>
</template>
