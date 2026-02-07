<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { parseTicket } from '@/api/plans'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['close', 'imported'])

const imageBase64 = ref(null)
const status = ref('')
const error = ref('')
const submitting = ref(false)
let pasteHandler = null

function setImageFromFile(file) {
  const reader = new FileReader()
  reader.onload = () => {
    imageBase64.value = reader.result
    error.value = ''
  }
  reader.readAsDataURL(file)
}

function onFileChange(e) {
  const f = e.target.files[0]
  if (f && f.type.startsWith('image/')) setImageFromFile(f)
}

function onDropClick() {
  document.getElementById('ticket-file-input')?.click()
}

async function handleSubmit() {
  if (!imageBase64.value) return
  submitting.value = true
  status.value = '正在识别票据…'
  error.value = ''

  try {
    const data = await parseTicket(imageBase64.value)
    if (data.type === 'unknown' || data.error) {
      error.value = data.error || '无法识别为机票或火车票'
      status.value = ''
      return
    }
    status.value = '已加入当天行程'
    emit('imported', data)
    emit('close')
  } catch (e) {
    error.value = e.message || '识别失败，请重试'
    status.value = ''
  } finally {
    submitting.value = false
  }
}

function onClose() {
  imageBase64.value = null
  status.value = ''
  error.value = ''
  emit('close')
}

onMounted(() => {
  pasteHandler = (e) => {
    if (props.show && e.clipboardData?.files?.length) {
      const f = Array.from(e.clipboardData.files).find(f => f.type.startsWith('image/'))
      if (f) { e.preventDefault(); setImageFromFile(f) }
    }
  }
  window.addEventListener('paste', pasteHandler)
})

onBeforeUnmount(() => {
  if (pasteHandler) window.removeEventListener('paste', pasteHandler)
})
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[70]">
      <div class="absolute inset-0 backdrop-blur-sm" style="background: var(--modal-overlay);" @click="onClose"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[calc(100%-2rem)] max-w-md rounded-2xl shadow-2xl p-6" style="background: var(--modal-bg);" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold t-heading">导入航班 / 车票</h3>
          <button type="button" @click="onClose" class="w-8 h-8 flex items-center justify-center rounded-full t-text-sub transition" style="background: var(--bg-inset);">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <p class="text-sm t-text-sub mb-3">上传或粘贴机票、高铁票等截图，自动识别并加入当天行程</p>

        <div @click="onDropClick" class="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer hover:border-cyan-400 transition" style="border-color: var(--border-color);">
          <input id="ticket-file-input" type="file" accept="image/*" class="hidden" @change="onFileChange">
          <div v-if="!imageBase64">
            <i class="fas fa-image text-4xl t-text-muted mb-2"></i>
            <p class="text-sm t-text-sub">点击选择或 <kbd class="px-1.5 py-0.5 rounded text-xs" style="background: var(--bg-inset);">Ctrl+V</kbd> 粘贴截图</p>
          </div>
          <img v-else :src="imageBase64" class="max-h-48 mx-auto rounded-lg object-contain" alt="预览">
        </div>

        <div v-if="status" class="mt-3 text-sm text-cyan-600">{{ status }}</div>
        <div v-if="error" class="mt-3 text-sm text-red-500">{{ error }}</div>

        <button
          type="button"
          :disabled="!imageBase64 || submitting"
          class="mt-4 w-full py-3 rounded-xl bg-primary text-white font-medium transition"
          :class="{ 'opacity-50 cursor-not-allowed': !imageBase64 || submitting }"
          @click="handleSubmit"
        >
          {{ submitting ? '识别中...' : '识别并导入' }}
        </button>
      </div>
    </div>
  </Teleport>
</template>
