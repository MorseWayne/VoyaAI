<script setup>
defineProps(['section'])
</script>

<template>
  <section class="rounded-xl p-6 shadow-sm transition-shadow hover:shadow-md" style="background: var(--bg-card); border: 1px solid var(--border-color);">
    <h2 v-if="section.title" class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
      {{ section.title }}
    </h2>
    <div class="prose max-w-none" style="color: var(--text-primary);">
      <div class="whitespace-pre-wrap leading-relaxed">{{ section.content }}</div>
    </div>
  </section>
</template>
