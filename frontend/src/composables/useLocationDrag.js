import { ref } from 'vue'
import { usePlanStore } from '@/stores/plan'

/**
 * Composable for drag-and-drop reordering of locations within a day.
 */
export function useLocationDrag() {
  const planStore = usePlanStore()
  const dragIndex = ref(null)
  const dragOverIndex = ref(null)

  function onDragStart(e, index) {
    dragIndex.value = index
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(index))
  }

  function onDragOver(e, index) {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    dragOverIndex.value = index
  }

  function onDragLeave() {
    dragOverIndex.value = null
  }

  async function onDrop(e, toIndex, dayIndex) {
    e.preventDefault()
    const fromIndex = dragIndex.value
    dragOverIndex.value = null
    if (fromIndex === null || fromIndex === toIndex) {
      dragIndex.value = null
      return
    }
    await planStore.reorderLocations(dayIndex, fromIndex, toIndex)
    dragIndex.value = null
  }

  function onDragEnd() {
    dragIndex.value = null
    dragOverIndex.value = null
  }

  return { dragIndex, dragOverIndex, onDragStart, onDragOver, onDragLeave, onDrop, onDragEnd }
}
