<script setup>
import { useUIStore } from '@/stores/ui'

const ui = useUIStore()
</script>

<template>
  <div class="fixed top-24 right-4 z-[70] space-y-2">
    <TransitionGroup name="toast">
      <div
        v-for="toast in ui.toasts"
        :key="toast.id"
        class="px-6 py-3 rounded-lg shadow-xl text-white font-medium"
        :class="toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'"
      >
        <i :class="['fas mr-2', toast.type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle']"></i>
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s ease-out; }
.toast-leave-active { transition: all 0.3s ease-in; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to { opacity: 0; transform: translateX(100%); }
</style>
