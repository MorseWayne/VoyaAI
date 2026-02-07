<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  plan: { type: Object, required: true },
})
const emit = defineEmits(['delete'])
const router = useRouter()

function viewPlan() {
  router.push({ name: 'plan-detail', params: { id: props.plan.id } })
}
</script>

<template>
  <div class="rounded-xl shadow-md hover:shadow-lg transition p-6 border-t-4 border-cyan-500 relative group" style="background: var(--bg-card); border-left: 1px solid var(--border-color); border-right: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color);">
    <button @click.stop="emit('delete', plan.id)" class="absolute top-4 right-4 t-text-muted hover:text-red-400 opacity-0 group-hover:opacity-100 transition">
      <i class="fas fa-trash-alt"></i>
    </button>
    <h3 class="font-bold text-xl mb-2 t-heading truncate" :title="plan.title || '未命名行程'">{{ plan.title || '未命名行程' }}</h3>
    <div class="text-sm t-text-sub mb-4 space-y-1">
      <p><i class="far fa-calendar-alt w-5 text-cyan-500"></i> {{ new Date(plan.created_at || Date.now()).toLocaleDateString() }}</p>
      <p><i class="fas fa-map-marker-alt w-5 text-cyan-500"></i> {{ plan.days ? plan.days.length : 0 }} 天行程</p>
    </div>
    <button @click="viewPlan" class="w-full mt-2 t-text-sub hover:bg-cyan-600 hover:text-white font-medium py-2 rounded-lg transition" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
      查看详情
    </button>
  </div>
</template>
