import { computed } from 'vue'
import { getDayArrivalTimes, ensureDayStayArray } from '@/utils/time'

/**
 * Composable for computing arrival times for a given day reactively.
 * @param {import('vue').Ref|import('vue').ComputedRef} dayRef - reactive reference to the day data
 * @returns {{ arrivalTimes: ComputedRef<Array> }}
 */
export function useTimeCalc(dayRef) {
  const arrivalTimes = computed(() => {
    const day = dayRef.value
    if (!day) return []
    ensureDayStayArray(day)
    return getDayArrivalTimes(day)
  })

  return { arrivalTimes }
}
