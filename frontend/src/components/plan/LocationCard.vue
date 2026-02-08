<script setup>
import { computed } from 'vue'

const props = defineProps({
  location: { type: Object, default: null },
  index: { type: Number, required: true },
  isLast: { type: Boolean, default: false },
  roleLabel: { type: String, default: null },
  arrivalHm: { type: String, default: '--' },
  stayMinutes: { type: Number, default: 0 },
  dayIndex: { type: Number, default: 0 },
  departureHm: { type: String, default: null },
  canEditStart: { type: Boolean, default: false },
})

const emit = defineEmits(['insert', 'remove', 'updateStay', 'editStart'])

const name = computed(() => {
  if (props.location?.name) return props.location.name
  if (props.roleLabel === '起点') return '起点（待补充）'
  if (props.roleLabel === '终点') return '终点（待补充）'
  return '未知地点'
})

const address = computed(() => props.location?.address || props.location?.city || props.location?.name || '未知地址')

const timeLabel = computed(() => {
  if (props.departureHm && props.stayMinutes > 0) {
    return `到达 ${props.arrivalHm} · 离开 ${props.departureHm}`
  }
  return `到达 ${props.arrivalHm}`
})

function onStayChange(e) {
  const val = Math.max(0, Math.min(480, parseInt(e.target.value, 10) || 0))
  emit('updateStay', props.dayIndex, props.index, val)
}
</script>

<template>
  <div class="timeline-item group relative">
    <!-- Timeline Rail -->
    <div class="timeline-rail">
      <div
        class="timeline-node"
        :class="{
          'bg-emerald-500 border-emerald-300 text-white shadow-emerald-500/30': roleLabel === '起点',
          'bg-rose-500 border-rose-300 text-white shadow-rose-500/30': isLast && roleLabel === '终点',
        }"
      >
        <span class="text-sm font-bold font-mono">{{ index + 1 }}</span>
      </div>
      <div class="timeline-time">
        {{ arrivalHm }}
      </div>
      <!-- Vertical line -->
      <div v-if="!isLast" class="timeline-line"></div>
    </div>

    <!-- Card Content -->
    <div class="flex-1 min-w-0 pb-2">
      <div
        class="location-card"
        :class="{ 'is-start': roleLabel === '起点', 'is-end': roleLabel === '终点' }"
      >
        <div class="flex justify-between items-start gap-3">
          <div class="min-w-0 flex-1">
            <div class="flex items-center flex-wrap gap-2 mb-1.5">
              <h4 class="font-bold t-heading text-lg leading-snug">{{ name }}</h4>
              <span v-if="roleLabel === '起点'" class="px-2 py-0.5 rounded-full text-xs font-bold shadow-sm" style="background: var(--badge-start-bg); color: var(--badge-start-text);">起点</span>
              <span v-if="roleLabel === '终点'" class="px-2 py-0.5 rounded-full text-xs font-bold shadow-sm" style="background: var(--badge-end-bg); color: var(--badge-end-text);">终点</span>
            </div>

            <p class="text-sm t-text-sub flex items-center gap-1.5 mb-3">
              <i class="fas fa-map-marker-alt text-cyan-500/70 text-xs"></i>
              <span class="truncate opacity-80">{{ address }}</span>
            </p>

            <div class="flex items-center gap-4 flex-wrap">
              <div class="inline-flex items-center gap-2 rounded-lg px-2.5 py-1" style="background: var(--bg-inset); border: 1px solid var(--border-subtle);">
                <i class="far fa-clock t-text-muted text-xs"></i>
                <span class="text-xs t-text-sub font-medium">{{ timeLabel }}</span>
              </div>

              <div class="inline-flex items-center gap-1.5" @click.stop>
                <i class="fas fa-hourglass-half t-text-muted text-xs"></i>
                <span class="text-xs t-text-muted">停留</span>
                <input
                  type="number"
                  min="0"
                  max="480"
                  step="15"
                  :value="stayMinutes"
                  class="w-14 text-xs text-center border-0 bg-transparent py-0.5 focus:ring-0 font-medium transition-colors"
                  style="border-bottom: 1px solid var(--border-color); color: var(--text-primary);"
                  @change="onStayChange"
                >
                <span class="text-xs t-text-muted">分</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200" @click.stop>
            <button
              v-if="canEditStart"
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-amber-600 hover:bg-amber-500 hover:text-white transition shadow-sm"
              style="background: var(--nav-active-bg);"
              @click="emit('editStart')"
              title="修改起点"
            >
              <i class="fas fa-edit text-xs"></i>
            </button>
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-cyan-600 hover:bg-cyan-500 hover:text-white transition shadow-sm"
              style="background: var(--nav-active-bg);"
              @click="emit('insert', isLast ? null : index + 1)"
              title="在此处插入下一站"
            >
              <i class="fas fa-plus text-xs"></i>
            </button>
            <button
              type="button"
              class="w-8 h-8 flex items-center justify-center rounded-lg t-text-muted hover:bg-rose-500/10 hover:text-rose-500 transition shadow-sm"
              style="background: var(--bg-inset);"
              @click="emit('remove', index, isLast)"
              title="删除此地点"
            >
              <i class="fas fa-trash-alt text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
