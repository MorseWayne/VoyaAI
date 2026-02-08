<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  show: Boolean,
  triggerRect: { type: Object, default: null },
})

const emit = defineEmits(['select', 'close'])

const dropdownRef = ref(null)
const style = ref({})

const modes = [
  { mode: 'driving', icon: 'fa-car', label: '驾车' },
  { mode: 'transit', icon: 'fa-bus', label: '公交/地铁' },
  { mode: 'train', icon: 'fa-train', label: '高铁/火车' },
  { mode: 'flight', icon: 'fa-plane', label: '飞机' },
  { mode: 'walking', icon: 'fa-walking', label: '步行' },
  { mode: 'cycling', icon: 'fa-bicycle', label: '骑行' },
]

function updatePosition() {
  if (!props.triggerRect) return
  const rect = props.triggerRect
  let top = rect.bottom + 8
  const left = Math.min(rect.left, window.innerWidth - 170)
  if (top + 220 > window.innerHeight) {
    top = rect.top - 220 - 8
  }
  style.value = { top: `${top}px`, left: `${left}px` }
}

function onOutsideClick(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    emit('close')
  }
}

onMounted(() => {
  updatePosition()
  nextTick(() => document.addEventListener('click', onOutsideClick))
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onOutsideClick)
})

function select(mode) {
  emit('select', mode)
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      ref="dropdownRef"
      class="fixed z-[100] rounded-xl shadow-2xl py-1.5 w-40 animate-fade-in"
      :style="{ ...style, background: 'var(--dropdown-bg)', border: '1px solid var(--dropdown-border)' }"
    >
      <button
        v-for="m in modes"
        :key="m.mode"
        @click="select(m.mode)"
        class="w-full text-left px-4 py-2.5 transition flex items-center gap-3 group"
        style="color: var(--dropdown-text);"
      >
        <i :class="['fas', m.icon, 'w-5 text-center']" style="color: var(--dropdown-icon);"></i>
        <span class="text-sm font-medium">{{ m.label }}</span>
      </button>
    </div>
  </Teleport>
</template>
