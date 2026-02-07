<script setup>
import { ref } from 'vue'
import { searchLocationTips } from '@/api/locations'
import BaseModal from '@/components/common/BaseModal.vue'

const props = defineProps({
  show: Boolean,
  city: { type: String, default: '' },
  insertAtIndex: { type: [Number, null], default: null },
})

const emit = defineEmits(['close', 'select', 'openTicketImport'])

const keyword = ref('')
const results = ref([])
const searching = ref(false)
let debounceTimer = null

function handleSearch(value) {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!value.trim()) return
  debounceTimer = setTimeout(async () => {
    searching.value = true
    try {
      results.value = await searchLocationTips(value, props.city)
    } catch (e) {
      console.error(e)
    } finally {
      searching.value = false
    }
  }, 500)
}

function selectItem(item) {
  emit('select', {
    name: item.name,
    address: item.address,
    city: item.city || props.city || '',
    lat: item.location ? parseFloat(item.location.split(',')[1]) : null,
    lng: item.location ? parseFloat(item.location.split(',')[0]) : null,
  })
}

function onClose() {
  keyword.value = ''
  results.value = []
  emit('close')
}
</script>

<template>
  <BaseModal :show="show" title="添加行程地点" @close="onClose">
    <div class="relative mb-4">
      <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 t-text-muted"></i>
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索地点..."
        class="w-full pl-11 pr-4 py-3 rounded-xl border outline-none transition"
        @input="handleSearch(keyword)"
      >
    </div>

    <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
      <button class="flex-shrink-0 px-3 py-1.5 text-cyan-600 text-xs rounded-lg font-medium flex items-center gap-1" style="background: var(--nav-active-bg); border: 1px solid rgba(6,182,212,0.2);">
        <i class="fas fa-search"></i> 搜索
      </button>
      <button type="button" @click="onClose(); emit('openTicketImport')" class="flex-shrink-0 px-3 py-1.5 text-cyan-600 text-xs rounded-lg font-medium flex items-center gap-1 transition" style="background: var(--nav-active-bg); border: 1px solid rgba(6,182,212,0.2);">
        <i class="fas fa-camera"></i> 截图导入
      </button>
    </div>

    <div class="h-64 overflow-y-auto space-y-2">
      <div v-if="searching" class="text-center py-4 t-text-muted">
        <i class="fas fa-spinner fa-spin"></i> 搜索中...
      </div>

      <div v-else-if="results.length === 0 && !keyword" class="text-center t-text-muted py-10">
        <i class="fas fa-map-marked-alt text-3xl mb-2 opacity-50"></i>
        <p class="text-sm">输入关键词搜索地点</p>
        <p v-if="insertAtIndex !== null" class="text-xs mt-1 text-cyan-600">将添加为当前站点的下一站</p>
      </div>

      <div v-else-if="results.length === 0" class="text-center py-4 t-text-muted">未找到相关地点</div>

      <div
        v-for="item in results"
        :key="item.name + item.address"
        @click="selectItem(item)"
        class="p-3 rounded-lg cursor-pointer transition flex items-center gap-3"
        style="border-bottom: 1px solid var(--border-subtle);"
      >
        <div class="w-8 h-8 rounded-full flex items-center justify-center t-text-muted flex-shrink-0" style="background: var(--bg-inset);">
          <i class="fas fa-map-pin"></i>
        </div>
        <div>
          <div class="font-medium text-sm t-text">{{ item.name }}</div>
          <div class="text-xs t-text-muted truncate w-64">{{ item.district || '' }} {{ item.address || '' }}</div>
        </div>
      </div>
    </div>
  </BaseModal>
</template>
