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

const displayContent = computed(() => activeContent.value ?? props.section.content ?? '')

/** 解析交通方式块，返回 { blocks, isSimple } */
function parseTransportBlocks(text) {
  if (!text || !text.trim()) return null

  const blocks = []
  const lines = text.split(/\n+/).map((l) => l.trim()).filter(Boolean)

  // 模式1: **大巴 (最省钱)** 或 大巴 (最省钱): 后面跟多行
  const boldMethodRe = /^\*\*([^*)]+)(?:\s*\((?:[^)]+)\))?\*\*\s*[:：]?\s*(.*)$/
  // 模式2: 方式一:地铁,... 或 方式一：地铁，...
  const fangshiRe = /^方式[一二三四五六七八九十\d]+[:：]\s*(\S+)[,，]\s*(.*)$/
  // 模式3: 地铁(推荐) 或 港铁 (最方便, 推荐)
  const methodRe = /^([^\s(（]+)\s*[（(]([^）)]+)[）)]\s*[:：]?\s*(.*)$/
  // 模式4: 推荐xxx、务必xxx 等提示
  const tipRe = /^(推荐|务必|建议|注意|小贴士)[:：]?\s*(.*)$/

  for (const line of lines) {
    let m = line.match(boldMethodRe)
    if (m) {
      blocks.push({
        type: 'transport',
        method: m[1].trim(),
        tag: (m[2].match(/^[^:：]+/)?.[0] ?? '').trim(),
        raw: m[2] || line,
        icon: getTransportIcon(m[1]),
      })
      continue
    }
    m = line.match(fangshiRe)
    if (m) {
      blocks.push({
        type: 'transport',
        method: m[1].trim(),
        tag: '',
        raw: m[2] || line,
        icon: getTransportIcon(m[1]),
      })
      continue
    }
    m = line.match(methodRe)
    if (m) {
      blocks.push({
        type: 'transport',
        method: m[1].trim(),
        tag: m[2].trim(),
        raw: m[3] || line,
        icon: getTransportIcon(m[1]),
      })
      continue
    }
    m = line.match(tipRe)
    if (m) {
      blocks.push({ type: 'tip', label: m[1], text: m[2].trim() })
      continue
    }
    // 单行可能是纯说明
    if (line.length > 20 && !line.includes('|')) {
      blocks.push({ type: 'text', text: line })
    }
  }

  // 若整段是分号分隔的紧凑格式，尝试拆分
  if (blocks.length === 0 && text.includes(';')) {
    const parts = text.split(/;\s*/).filter(Boolean)
    let lastTransport = null
    for (const p of parts) {
      const f = p.match(/^方式[一二三四五六七八九十\d]+[:：]\s*(\S+)[,，]\s*(.*)$/)
      if (f) {
        lastTransport = {
          type: 'transport',
          method: f[1].trim(),
          tag: '',
          raw: f[2] || p,
          icon: getTransportIcon(f[1]),
        }
        blocks.push(lastTransport)
        continue
      }
      const mm = p.match(/^([^\s:：]+)\s*[（(]([^）)]+)[）)]\s*[:：]?\s*(.*)$/)
      if (mm) {
        lastTransport = {
          type: 'transport',
          method: mm[1].trim(),
          tag: mm[2].trim(),
          raw: mm[3] || p,
          icon: getTransportIcon(mm[1]),
        }
        blocks.push(lastTransport)
        continue
      }
      const mm2 = p.match(/^([^\s,，:：]+)\s*[,，:：]\s*(.*)$/)
      if (mm2 && /^(地铁|大巴|港铁|高铁|步行|公交|巴士)$/.test(mm2[1].trim())) {
        lastTransport = {
          type: 'transport',
          method: mm2[1].trim(),
          tag: '',
          raw: mm2[2] || p,
          icon: getTransportIcon(mm2[1]),
        }
        blocks.push(lastTransport)
        continue
      }
      // 后续补充信息（时间、费用、支付）追加到上一个交通块
      if (lastTransport && (p.length < 50 || /^(约|~|支持|支付宝|微信|元|港币|分钟)/.test(p))) {
        lastTransport.raw = lastTransport.raw + '；' + p
      } else {
        lastTransport = null
        blocks.push({ type: 'text', text: p })
      }
    }
  }

  if (blocks.length === 0) return null
  return { blocks, isSimple: blocks.every((b) => b.type === 'text') }
}

function getTransportIcon(method) {
  const m = (method || '').toLowerCase()
  if (/地铁|metro|mtr|港铁/.test(m)) return 'subway'
  if (/大巴|公交|巴士|bus/.test(m)) return 'bus'
  if (/高铁|火车|动车|train/.test(m)) return 'train'
  if (/步行|走路|walk/.test(m)) return 'walk'
  if (/小轮|轮渡|船|ferry/.test(m)) return 'ferry'
  if (/叮叮|电车|tram/.test(m)) return 'tram'
  return 'transport'
}

const parsed = computed(() => parseTransportBlocks(displayContent.value))

const tabKeys = computed(() => {
  if (!props.section.data) return []
  return Object.keys(props.section.data)
})
</script>

<template>
  <section
    class="rounded-2xl overflow-hidden shadow-sm transition-shadow duration-200 hover:shadow-md"
    style="background: var(--bg-card); border: 1px solid var(--border-color); border-top: none;"
  >
    <!-- 标题区 -->
    <div class="p-6 pb-4">
      <div class="flex items-center gap-3">
        <div
          class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl"
          style="background: linear-gradient(135deg, var(--nav-active-bg), rgba(9, 105, 218, 0.08));"
        >
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        </div>
        <div>
          <h2 class="text-xl font-bold" style="color: var(--text-heading);">{{ section.title }}</h2>
          <p v-if="tabKeys.length > 0" class="text-sm mt-0.5" style="color: var(--text-secondary);">切换下方标签查看各阶段详情</p>
        </div>
      </div>
    </div>

    <!-- 标签页 -->
    <div
      v-if="tabKeys.length > 0"
      class="px-6 pb-4"
    >
      <div
        class="flex flex-wrap gap-2 p-1.5 rounded-xl"
        style="background: var(--bg-inset);"
      >
        <button
          v-for="tab in tabKeys"
          :key="tab"
          @click="activeTab = tab"
          class="min-w-0 flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer whitespace-nowrap overflow-hidden text-ellipsis hover:opacity-90"
          :class="activeTab === tab ? 'shadow-sm' : ''"
          :style="activeTab === tab
            ? 'background: var(--bg-card); color: var(--text-heading); box-shadow: var(--card-shadow); border: 1px solid var(--border-color);'
            : 'color: var(--text-muted);'"
        >
          {{ tab }}
        </button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="px-6 pb-6 pt-2">
      <template v-if="parsed && parsed.blocks.length > 0">
        <div class="space-y-4">
          <template v-for="(block, idx) in parsed.blocks" :key="idx">
            <!-- 交通方式卡片 -->
            <div
              v-if="block.type === 'transport'"
              class="rounded-xl p-4 transition-colors duration-200 cursor-default"
              style="background: var(--bg-inset); border: 1px solid var(--border-subtle);"
            >
              <div class="flex items-start gap-3">
                <div
                  class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                  style="background: var(--nav-active-bg);"
                >
                  <!-- 地铁 -->
                  <svg v-if="block.icon === 'subway'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                  <!-- 大巴 -->
                  <svg v-else-if="block.icon === 'bus'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h4a2 2 0 002-2V7m-4 0V4m0 4h4M5 7h14" />
                  </svg>
                  <!-- 高铁 -->
                  <svg v-else-if="block.icon === 'train'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <!-- 步行 -->
                  <svg v-else-if="block.icon === 'walk'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <!-- 渡轮 -->
                  <svg v-else-if="block.icon === 'ferry'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21h18M4 18h16M5 12h14M6 9h12M7 6h10" />
                  </svg>
                  <!-- 电车 -->
                  <svg v-else-if="block.icon === 'tram'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                  <!-- 默认 -->
                  <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2 mb-1.5">
                    <span class="font-semibold" style="color: var(--text-heading);">{{ block.method }}</span>
                    <span
                      v-if="block.tag"
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                      style="background: var(--badge-start-bg); color: var(--badge-start-text);"
                    >
                      {{ block.tag }}
                    </span>
                  </div>
                  <p class="text-sm leading-relaxed" style="color: var(--text-primary);">
                    {{ block.raw }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 提示块 -->
            <div
              v-else-if="block.type === 'tip'"
              class="flex items-start gap-3 rounded-xl p-4"
              style="background: rgba(9, 105, 218, 0.06); border: 1px solid rgba(9, 105, 218, 0.2);"
            >
              <svg class="h-5 w-5 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--nav-active-text);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <span class="font-semibold" style="color: var(--nav-active-text);">{{ block.label }}：</span>
                <span style="color: var(--text-primary);">{{ block.text }}</span>
              </div>
            </div>

            <!-- 普通文本 -->
            <p
              v-else
              class="text-sm leading-relaxed"
              style="color: var(--text-primary);"
            >
              {{ block.text }}
            </p>
          </template>
        </div>
      </template>

      <!-- 回退：原样展示，改善排版 -->
      <div
        v-else
        class="prose prose-sm max-w-none"
        style="color: var(--text-primary);"
      >
        <div
          class="whitespace-pre-wrap leading-relaxed text-sm"
          style="line-height: 1.75; color: var(--text-primary);"
        >
          {{ displayContent }}
        </div>
      </div>
    </div>
  </section>
</template>
