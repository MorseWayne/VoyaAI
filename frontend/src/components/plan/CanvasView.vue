<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useCanvasDrag } from '@/composables/useCanvasDrag'
import CanvasItem from './CanvasItem.vue'

const props = defineProps({
  dayIndex: { type: Number, required: true },
  segments: { type: Array, required: true },
  arrivalTimes: { type: Array, required: true },
  layout: { type: Array, required: true },
})

const emit = defineEmits(['openTransport', 'removeLocation', 'updateStay'])
const planStore = usePlanStore()
const { clampPosition, resetLayout, CARD_W, CARD_H, MIN_X, MIN_Y } = useCanvasDrag()

const svgRef = ref(null)
const containerRef = ref(null)

// Dragging state
const dragState = ref({ isDragging: false, nodeIndex: null, startX: 0, startY: 0, initialLeft: 0, initialTop: 0, el: null })

function getContainerWidth() {
  return containerRef.value?.offsetWidth || 1060
}

function getContainerHeight() {
  let maxY = 600
  props.layout.forEach(p => { if (p && p.y + CARD_H + 40 > maxY) maxY = p.y + CARD_H + 40 })
  return maxY
}

function drawConnections() {
  if (!svgRef.value) return
  svgRef.value.innerHTML = ''

  // Arrow marker
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
  defs.innerHTML = `<marker id="arrowhead-${props.dayIndex}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--snake-path-stroke)" /></marker>`
  svgRef.value.appendChild(defs)

  const cardCenterW = CARD_W / 2, cardCenterH = 50
  for (let i = 0; i < props.segments.length; i++) {
    const p1 = props.layout[i]
    const p2 = props.layout[i + 1]
    if (!p1 || !p2) continue
    const start = { x: p1.x + cardCenterW, y: p1.y + cardCenterH }
    const end = { x: p2.x + cardCenterW, y: p2.y + cardCenterH }
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.setAttribute('class', 'snake-path-segment')
    path.setAttribute('marker-end', `url(#arrowhead-${props.dayIndex})`)
    path.setAttribute('d', `M ${start.x} ${start.y} L ${end.x} ${end.y}`)
    svgRef.value.appendChild(path)
  }
}

function initDrag(e, nodeIndex) {
  if (e.button !== 0) return
  e.preventDefault()
  const el = document.getElementById(`snake-item-${props.dayIndex}-${nodeIndex}`)
  if (!el) return
  dragState.value = {
    isDragging: true, nodeIndex, startX: e.clientX, startY: e.clientY,
    initialLeft: parseFloat(el.style.left) || 0, initialTop: parseFloat(el.style.top) || 0, el,
  }
  el.style.zIndex = '100'
  el.style.cursor = 'grabbing'
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(e) {
  if (!dragState.value.isDragging) return
  const dx = e.clientX - dragState.value.startX
  const dy = e.clientY - dragState.value.startY
  const rawLeft = dragState.value.initialLeft + dx
  const rawTop = dragState.value.initialTop + dy

  // Clamp to container bounds
  const cw = getContainerWidth()
  const clamped = clampPosition({ x: rawLeft, y: rawTop }, cw)

  dragState.value.el.style.left = `${clamped.x}px`
  dragState.value.el.style.top = `${clamped.y}px`

  const day = planStore.activePlan.days[props.dayIndex]
  if (day.layout?.[dragState.value.nodeIndex]) {
    day.layout[dragState.value.nodeIndex].x = clamped.x
    day.layout[dragState.value.nodeIndex].y = clamped.y
  }
  requestAnimationFrame(drawConnections)
}

function handleMouseUp() {
  if (!dragState.value.isDragging) return
  const { nodeIndex, el } = dragState.value
  const day = planStore.activePlan.days[props.dayIndex]
  if (!day.layout) day.layout = []

  const cw = getContainerWidth()
  const clamped = clampPosition(
    { x: parseFloat(el.style.left), y: parseFloat(el.style.top) },
    cw,
  )
  day.layout[nodeIndex] = clamped

  if (containerRef.value) {
    const finalTop = clamped.y
    if (finalTop + CARD_H + 40 > containerRef.value.offsetHeight) {
      containerRef.value.style.height = `${finalTop + CARD_H + 80}px`
    }
  }

  el.style.zIndex = ''
  el.style.cursor = 'grab'
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  dragState.value = { isDragging: false, nodeIndex: null, startX: 0, startY: 0, initialLeft: 0, initialTop: 0, el: null }
  planStore.saveActivePlanSilently()
}

function handleResetLayout() {
  const day = planStore.activePlan.days[props.dayIndex]
  if (!day) return
  const cw = getContainerWidth()
  resetLayout(day, cw)
  nextTick(drawConnections)
  planStore.saveActivePlanSilently()
}

function getBadgePos(i) {
  const p1 = props.layout[i]
  const p2 = props.layout[i + 1]
  if (!p1 || !p2) return null
  return { x: (p1.x + p2.x + CARD_W) / 2, y: (p1.y + p2.y + 100) / 2 }
}

let resizeHandler = null
onMounted(() => {
  nextTick(drawConnections)
  resizeHandler = () => drawConnections()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})

watch(() => [props.segments, props.layout], () => nextTick(drawConnections), { deep: true })
</script>

<template>
  <div class="hidden md:block">
    <!-- Reset layout button -->
    <div class="flex justify-end mb-2">
      <button
        @click="handleResetLayout"
        class="px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 t-text-sub hover:text-cyan-500"
        style="background: var(--bg-elevated); border: 1px solid var(--border-color);"
        title="重置卡片位置为默认排列"
      >
        <i class="fas fa-th-large"></i> 重置布局
      </button>
    </div>

    <div ref="containerRef" class="snake-container" :style="{ height: getContainerHeight() + 'px', position: 'relative' }">
      <svg ref="svgRef" class="snake-svg-container" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index: 0; pointer-events:none;"></svg>

      <!-- Location nodes -->
      <template v-for="(seg, i) in segments" :key="'origin-' + i">
        <CanvasItem
          :location="seg.origin"
          :index="i"
          :is-last="false"
          :role-label="(i === 0 && dayIndex === 0) ? '起点' : null"
          :time-data="arrivalTimes[i]"
          :day-index="dayIndex"
          :pos="layout[i] || { x: 0, y: 0 }"
          @mousedown="initDrag($event, i)"
          @remove="emit('removeLocation', i, false)"
          @update-stay="(di, li, val) => emit('updateStay', di, li, val)"
        />
      </template>

      <!-- Last destination -->
      <CanvasItem
        v-if="segments.length > 0"
        :location="segments[segments.length - 1].destination"
        :index="segments.length"
        :is-last="true"
        role-label="终点"
        :time-data="arrivalTimes[segments.length]"
        :day-index="dayIndex"
        :pos="layout[segments.length] || { x: 0, y: 0 }"
        @mousedown="initDrag($event, segments.length)"
        @remove="emit('removeLocation', segments.length, true)"
        @update-stay="(di, li, val) => emit('updateStay', di, li, val)"
      />

      <!-- Transport badges at midpoints -->
      <template v-for="(seg, i) in segments" :key="'badge-' + i">
        <div
          v-if="getBadgePos(i)"
          class="absolute z-30 flex items-center gap-2 px-3 py-1.5 text-xs rounded-full shadow-lg backdrop-blur-sm transition-all duration-200 whitespace-nowrap cursor-pointer"
          :style="{ top: getBadgePos(i).y + 'px', left: getBadgePos(i).x + 'px', transform: 'translate(-50%, -50%)', background: 'var(--transport-bg)', color: 'var(--transport-text)', border: '1px solid var(--transport-border)' }"
          @click.stop="emit('openTransport', $event, i)"
        >
          <i :class="['fas', seg.type === 'transit' ? 'fa-bus' : seg.type === 'walking' ? 'fa-walking' : seg.type === 'cycling' ? 'fa-bicycle' : seg.type === 'flight' ? 'fa-plane' : seg.type === 'train' ? 'fa-train' : 'fa-car']"></i>
          <span class="font-bold">{{ seg.type === 'transit' ? '公交' : seg.type === 'walking' ? '步行' : seg.type === 'cycling' ? '骑行' : seg.type === 'flight' ? '航班' : seg.type === 'train' ? '火车' : '驾车' }}</span>
        </div>
      </template>
    </div>
  </div>
</template>
