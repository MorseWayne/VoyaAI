import { defineStore } from 'pinia'
import { ref } from 'vue'

let toastId = 0

export const useUIStore = defineStore('ui', () => {
  const toasts = ref([])

  function showToast(message, type = 'success') {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  return { toasts, showToast }
})
