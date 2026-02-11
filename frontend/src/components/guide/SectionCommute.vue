<script setup>
import { ref, computed, watchEffect } from 'vue'

const props = defineProps(['section'])
const activeTab = ref('')

watchEffect(() => {
    if (props.section.data && Object.keys(props.section.data).length > 0) {
        if (!activeTab.value) activeTab.value = Object.keys(props.section.data)[0]
    }
})

const activeContent = computed(() => {
    return props.section.data ? props.section.data[activeTab.value] : null
})
</script>

<template>
  <section class="rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
      <span class="text-2xl">🚇</span> {{ section.title }}
    </h2>
    
    <div v-if="section.data && Object.keys(section.data).length > 0" class="flex space-x-1 mb-6 p-1 rounded-lg" style="background: var(--bg-input);">
      <button 
        v-for="(content, tab) in section.data"
        :key="tab"
        @click="activeTab = tab"
        class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer"
        :style="activeTab === tab ? 'background: var(--bg-card); color: var(--text-heading); box-shadow: var(--card-shadow);' : 'color: var(--text-muted);'"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="activeContent" class="prose max-w-none" style="color: var(--text-primary);">
      <div class="whitespace-pre-wrap leading-relaxed">{{ activeContent }}</div>
    </div>
    <div v-else class="prose max-w-none" style="color: var(--text-primary);">
       <div class="whitespace-pre-wrap leading-relaxed">{{ section.content }}</div>
    </div>
  </section>
</template>
