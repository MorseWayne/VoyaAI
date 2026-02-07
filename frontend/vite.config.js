import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  base: '/',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/travel': 'http://localhost:8182',
      '/health': 'http://localhost:8182',
      '/status': 'http://localhost:8182',
      '/test': 'http://localhost:8182',
    },
  },
})
