<script setup>
defineProps(['section'])
</script>

<template>
  <section class="rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color); border-top: none;">
    <h2 class="text-xl font-bold mb-6 flex items-center gap-2" style="color: var(--text-heading);">
      <span class="text-2xl">📅</span> {{ section.title }}
    </h2>
    
    <div v-if="section.data && section.data.length > 0" class="relative border-l-2 ml-3 space-y-8" style="border-color: var(--border-subtle);">
      <div v-for="(item, idx) in section.data" :key="idx" class="relative pl-8">
        <span class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-2" style="border-color: var(--nav-active-text);"></span>
        <div class="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-1">
          <span class="font-bold text-lg" style="color: var(--text-heading);">{{ item.time }}</span>
          <span class="font-semibold" style="color: var(--text-primary);">{{ item.title }}</span>
        </div>
        <p class="text-sm" style="color: var(--text-secondary);">{{ item.description }}</p>
      </div>
    </div>
    <div v-else class="whitespace-pre-wrap" style="color: var(--text-primary);">
        {{ section.content }}
    </div>
  </section>
</template>
