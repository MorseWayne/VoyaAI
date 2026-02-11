<script setup>
import { computed } from 'vue'

const props = defineProps(['section'])

/** 解析内容：识别列表项(-/—/•)和键值对(label: value)，优化展示 */
const parsedLines = computed(() => {
  const content = props.section?.content?.trim()
  if (!content) return []
  const lines = content.split(/\n+/).map((l) => l.trim()).filter(Boolean)
  return lines.map((line) => {
    // 列表项：- xxx、— xxx、• xxx
    const listMatch = line.match(/^[-—–•]\s+(.+)$/)
    if (listMatch) return { type: 'list', text: listMatch[1] }
    // 键值对：标签: 值 或 标签：值
    const kvMatch = line.match(/^([^:：]+)[:：]\s*(.+)$/)
    if (kvMatch) return { type: 'kv', label: kvMatch[1].trim(), value: kvMatch[2].trim() }
    return { type: 'text', text: line }
  })
})

/** 是否有可解析的结构化内容（列表或键值对） */
const hasStructured = computed(() =>
  parsedLines.value.some((p) => p.type === 'list' || p.type === 'kv')
)
</script>

<template>
  <section class="rounded-xl p-6 shadow-sm transition-shadow hover:shadow-md" style="background: var(--bg-card); border: 1px solid var(--border-color); border-top: none;">
    <h2 v-if="section.title" class="text-xl font-bold mb-4 flex items-center gap-2" style="color: var(--text-heading);">
      {{ section.title }}
    </h2>
    <div class="prose max-w-none" style="color: var(--text-primary);">
      <div v-if="hasStructured" class="space-y-2 leading-relaxed">
        <div
          v-for="(item, i) in parsedLines"
          :key="i"
          class="flex flex-wrap gap-x-2 gap-y-0.5"
        >
          <template v-if="item.type === 'list'">
            <span class="opacity-50 shrink-0" aria-hidden="true">·</span>
            <span>{{ item.text }}</span>
          </template>
          <template v-else-if="item.type === 'kv'">
            <span class="font-medium shrink-0" style="color: var(--text-secondary);">{{ item.label }}:</span>
            <span>{{ item.value }}</span>
          </template>
          <template v-else>
            <span>{{ item.text }}</span>
          </template>
        </div>
      </div>
      <div v-else class="whitespace-pre-wrap leading-relaxed">{{ section.content }}</div>
    </div>
  </section>
</template>
