<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="max-w-2xl mx-auto mt-10">
    <div class="glass-panel rounded-3xl shadow-2xl p-8 md:p-12 text-center relative overflow-hidden animate-fade-in">
      <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500"></div>

      <div class="w-24 h-24 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-inner rotate-3 hover:rotate-6 transition-transform" style="background: var(--nav-active-bg);">
        <i class="fas fa-robot text-5xl text-cyan-500"></i>
      </div>

      <h2 class="text-3xl font-bold t-heading mb-4">智能助手升级中</h2>
      <div class="w-16 h-1 bg-cyan-500/30 mx-auto rounded-full mb-6"></div>

      <p class="text-lg t-text-sub mb-8 leading-relaxed">
        为了给您提供更精准的旅行建议，我们的 AI 引擎正在进行重要升级。
        <br>请先尝试使用 <span class="font-bold text-cyan-500">路线规划</span> 功能。
      </p>

      <button @click="router.push({ name: 'planner' })" class="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white px-8 py-3.5 rounded-xl font-bold shadow-lg transform hover:-translate-y-1 transition-all duration-200 flex items-center justify-center gap-2 mx-auto">
        <span>前往路线规划</span>
        <i class="fas fa-arrow-right"></i>
      </button>
    </div>
  </div>
</template>
