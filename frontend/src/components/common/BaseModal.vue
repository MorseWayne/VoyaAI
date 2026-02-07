<script setup>
defineProps({
  show: Boolean,
  title: { type: String, default: '' },
  maxWidth: { type: String, default: '500px' },
})

const emit = defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center">
      <div class="absolute inset-0 backdrop-blur-sm transition-opacity" style="background: var(--modal-overlay);" @click="emit('close')"></div>
      <div
        class="relative w-[calc(100%-2rem)] rounded-2xl shadow-2xl p-6 animate-fade-in"
        :style="{ maxWidth, background: 'var(--modal-bg)' }"
      >
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold t-heading">{{ title }}</h3>
          <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full t-text-sub transition" style="background: var(--bg-inset);">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
