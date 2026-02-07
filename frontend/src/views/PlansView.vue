<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchPlans, deletePlan as deletePlanApi } from '@/api/plans'
import PlanCard from '@/components/plan/PlanCard.vue'

const router = useRouter()
const plans = ref([])
const loading = ref(true)

async function loadPlans() {
  loading.value = true
  try {
    plans.value = await fetchPlans()
  } catch (e) {
    console.error('Error loading plans:', e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(planId) {
  if (!confirm('确定要删除这个行程吗？')) return
  try {
    await deletePlanApi(planId)
    loadPlans()
  } catch {
    alert('删除失败')
  }
}

onMounted(loadPlans)
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <div class="flex justify-between items-end mb-8 animate-fade-in">
      <div>
        <h2 class="text-3xl font-bold t-heading flex items-center gap-3">
          <i class="fas fa-bookmark text-cyan-500"></i> 我的行程列表
        </h2>
        <p class="t-text-sub mt-2">管理和查看您保存的所有旅行计划</p>
      </div>
      <div class="flex gap-3">
        <button @click="router.push({ name: 'create-plan' })" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all flex items-center gap-2 font-medium">
          <i class="fas fa-plus"></i> 新建行程
        </button>
        <button @click="loadPlans" class="px-4 py-2 rounded-lg transition-all shadow-sm flex items-center gap-2 t-text-sub" style="background: var(--bg-card); border: 1px solid var(--border-color);">
          <i class="fas fa-sync-alt"></i> 刷新列表
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in" style="animation-delay: 0.1s;">
      <div v-if="loading" class="col-span-full text-center py-20 t-text-muted rounded-2xl border-2 border-dashed" style="background: var(--bg-surface); border-color: var(--border-color);">
        <i class="fas fa-spinner fa-spin text-4xl mb-4 text-cyan-500"></i>
        <p>正在加载您的精彩行程...</p>
      </div>

      <div v-else-if="plans.length === 0" class="col-span-full text-center py-12 rounded-xl border-dashed border-2" style="background: var(--bg-surface); border-color: var(--border-color);">
        <i class="fas fa-inbox text-4xl t-text-muted mb-4"></i>
        <p class="t-text-sub">暂无保存的行程</p>
      </div>

      <PlanCard
        v-else
        v-for="plan in plans"
        :key="plan.id"
        :plan="plan"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>
