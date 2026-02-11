<script setup>
defineProps(['section'])
</script>

<template>
  <section class="rounded-xl p-6 shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color); border-top: none;">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
      <span class="text-2xl">🌤️</span> {{ section.title }}
    </h2>
    <div class="overflow-x-auto" v-if="section.data && section.data.length > 0">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr style="border-bottom: 1px solid var(--border-color);">
            <th v-for="(value, key) in section.data[0]" :key="key" class="p-3 font-semibold" style="color: var(--text-secondary);">
              {{ key }}
            </th>
          </tr>
        </thead>
        <tbody style="color: var(--text-primary);">
          <tr v-for="(row, idx) in section.data" :key="idx" style="border-bottom: 1px solid var(--border-subtle);">
            <td v-for="(value, key) in row" :key="key" class="p-3">
              {{ value }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="whitespace-pre-wrap" style="color: var(--text-primary);">
        {{ section.content }}
    </div>
  </section>
</template>
