<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listGuides, importGuide, deleteGuide } from '@/api/guides'

const router = useRouter()
const guides = ref([])
const loading = ref(false)
const showImportModal = ref(false)
const importContent = ref('')
const importing = ref(false)

const fetchGuides = async () => {
  loading.value = true
  try {
    guides.value = await listGuides()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleImport = async () => {
  if (!importContent.value) return
  importing.value = true
  try {
    await importGuide(importContent.value)
    showImportModal.value = false
    importContent.value = ''
    await fetchGuides()
  } catch (e) {
    alert('导入失败: ' + e.message)
  } finally {
    importing.value = false
  }
}

const handleDelete = async (id, event) => {
    event.stopPropagation()
    if (!confirm('确定要删除这个攻略吗？')) return
    try {
        await deleteGuide(id)
        await fetchGuides()
    } catch (e) {
        console.error(e)
    }
}

const navigateToGuide = (id) => {
    router.push({ name: 'guide-detail', params: { id } })
}

onMounted(fetchGuides)
</script>

<template>
  <div class="min-h-screen pt-20 pb-20 px-4" style="background: var(--bg-page);">
    <div class="container mx-auto max-w-6xl">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold" style="color: var(--text-heading);">攻略合集</h1>
        <button 
          @click="showImportModal = true"
          class="px-4 py-2 rounded-lg font-medium text-white transition-colors flex items-center gap-2 shadow-lg hover:shadow-xl"
          style="background: linear-gradient(135deg, var(--logo-text-from), var(--logo-text-to));"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          导入攻略
        </button>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
        <p class="mt-4 text-gray-500">加载中...</p>
      </div>

      <div v-else-if="guides.length === 0" class="text-center py-12 rounded-xl border-2 border-dashed" style="border-color: var(--border-color);">
        <p class="text-lg mb-4" style="color: var(--text-secondary);">暂无攻略，请导入 Markdown 笔记</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="guide in guides" 
          :key="guide.id"
          @click="navigateToGuide(guide.id)"
          class="group relative rounded-xl p-6 shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer border border-transparent hover:border-cyan-500/30"
          style="background: var(--bg-card);"
        >
          <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="(e) => handleDelete(guide.id, e)" class="p-2 text-red-500 hover:bg-red-50 rounded-full">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
          </div>
          <div class="h-40 mb-4 rounded-lg bg-gradient-to-br from-blue-50 to-cyan-50 flex items-center justify-center">
             <span class="text-6xl">🗺️</span>
          </div>
          <h3 class="text-xl font-bold mb-2 line-clamp-1" style="color: var(--text-heading);">{{ guide.title }}</h3>
          <p class="text-sm mb-4 line-clamp-2" style="color: var(--text-secondary);">
            {{ guide.sections.length }} 个章节 · 创建于 {{ new Date(guide.created_at).toLocaleDateString() }}
          </p>
          <div class="flex items-center text-sm font-medium" style="color: var(--nav-active-text);">
            查看详情 <svg class="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background: rgba(0,0,0,0.5);">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl p-6" style="background: var(--bg-card);">
        <h2 class="text-xl font-bold mb-4" style="color: var(--text-heading);">导入 Markdown 攻略</h2>
        <textarea 
          v-model="importContent"
          class="w-full h-64 p-4 rounded-lg border mb-4 focus:ring-2 focus:ring-cyan-500 outline-none resize-none font-mono text-sm"
          style="background: var(--bg-input); border-color: var(--border-color); color: var(--text-primary);"
          placeholder="# 标题&#10;## 章节...&#10;内容..."
        ></textarea>
        <div class="flex justify-end gap-3">
          <button 
            @click="showImportModal = false"
            class="px-4 py-2 rounded-lg font-medium transition-colors"
            style="color: var(--text-secondary); background: var(--bg-inset);"
          >
            取消
          </button>
          <button 
            @click="handleImport"
            :disabled="importing || !importContent"
            class="px-4 py-2 rounded-lg font-medium text-white transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, var(--logo-text-from), var(--logo-text-to));"
          >
            {{ importing ? '导入中...' : '确认导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
