import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const saved = localStorage.getItem('voyaai-theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const currentTheme = ref(saved || (prefersDark ? 'dark' : 'light'))

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('voyaai-theme', theme)
    currentTheme.value = theme
  }

  function toggleTheme() {
    const next = currentTheme.value === 'dark' ? 'light' : 'dark'
    applyTheme(next)
  }

  // Apply theme immediately
  applyTheme(currentTheme.value)

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('voyaai-theme')) {
      applyTheme(e.matches ? 'dark' : 'light')
    }
  })

  return { currentTheme, toggleTheme, applyTheme }
})
