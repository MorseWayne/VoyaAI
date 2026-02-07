/**
 * Time utility functions - pure functions for time calculations.
 */

/** Format seconds into human-readable duration string */
export function formatDuration(seconds) {
  if (!seconds) return '0分钟'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

/** Format meters into human-readable distance */
export function formatDistance(meters) {
  if (!meters) return '0米'
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)}公里`
  }
  return `${meters}米`
}

/** Parse "YYYY-MM-DD HH:MM" or "HH:MM" into milliseconds timestamp */
export function parseTimeToMs(str) {
  if (!str || typeof str !== 'string') return NaN
  const s = str.trim()
  if (/^\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}/.test(s)) {
    return new Date(s.replace(/-/g, '/')).getTime()
  }
  if (/^\d{1,2}:\d{2}/.test(s)) {
    const [h, m] = s.split(':').map(Number)
    return (h * 60 + m) * 60 * 1000
  }
  return NaN
}

/** Calculate flight/ride duration in seconds from dep/arr strings. Returns 0 if invalid */
export function durationSecondsFromTimes(depStr, arrStr) {
  const depMs = parseTimeToMs(depStr)
  const arrMs = parseTimeToMs(arrStr)
  if (Number.isNaN(depMs) || Number.isNaN(arrMs) || arrMs <= depMs) return 0
  return Math.round((arrMs - depMs) / 1000)
}

/** Minutes since midnight -> "HH:MM" */
export function minutesToHm(minutes) {
  if (minutes == null || minutes < 0) return '--'
  const h = Math.floor(minutes / 60) % 24
  const m = Math.floor(minutes % 60)
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

/** "HH:MM" -> minutes since midnight */
export function hmToMinutes(hm) {
  if (!hm || typeof hm !== 'string') return 0
  const parts = hm.trim().match(/^(\d{1,2}):(\d{2})$/)
  if (!parts) return 0
  return parseInt(parts[1], 10) * 60 + parseInt(parts[2], 10)
}

/** Time string ("HH:MM" or "YYYY-MM-DD HH:MM") -> minutes since midnight, null if invalid */
export function timeStringToMinutes(str) {
  if (!str || typeof str !== 'string') return null
  const ms = parseTimeToMs(str.trim())
  if (Number.isNaN(ms)) return null
  const d = new Date(ms)
  return d.getHours() * 60 + d.getMinutes()
}

/** Check if a segment has imported ticket times (flight/train with dep + arr times) */
export function segmentHasTicketTimes(seg) {
  if (!seg || (seg.type !== 'flight' && seg.type !== 'train')) return false
  const dep = seg.details?.departure_time || seg.origin?.departure_time
  const arr = seg.details?.arrival_time || seg.destination?.arrival_time
  return !!(dep && arr && timeStringToMinutes(dep) != null && timeStringToMinutes(arr) != null)
}

/** Ensure day's location_stay_minutes array matches the number of locations (segments.length + 1) */
export function ensureDayStayArray(day) {
  if (!day) return
  const len = (day.segments && day.segments.length) ? day.segments.length + 1 : 1
  if (!day.location_stay_minutes) day.location_stay_minutes = []
  while (day.location_stay_minutes.length < len) {
    day.location_stay_minutes.push(0)
  }
  if (day.location_stay_minutes.length > len) {
    day.location_stay_minutes.length = len
  }
}

/**
 * Calculate arrival and departure times for each location in a day.
 * Respects imported ticket times for flight/train segments.
 */
export function getDayArrivalTimes(day) {
  const segs = day.segments || []
  const stay = day.location_stay_minutes || []
  const startHm = day.start_time_hm || '08:00'
  let minutes = hmToMinutes(startHm)
  const result = []

  for (let i = 0; i < segs.length; i++) {
    const seg = segs[i]
    const stayMin = Math.max(0, parseFloat(stay[i]) || 0)

    if (segmentHasTicketTimes(seg)) {
      const depStr = seg.details?.departure_time || seg.origin?.departure_time
      const arrStr = seg.details?.arrival_time || seg.destination?.arrival_time
      const departMin = timeStringToMinutes(depStr)
      const arrMin = timeStringToMinutes(arrStr)
      result.push({
        arrivalMinutes: minutes,
        arrivalHm: minutesToHm(minutes),
        stayMinutes: stayMin,
        departureMinutes: departMin,
        departureHm: minutesToHm(departMin),
      })
      minutes = arrMin
    } else {
      const departMin = minutes + stayMin
      result.push({
        arrivalMinutes: minutes,
        arrivalHm: minutesToHm(minutes),
        stayMinutes: stayMin,
        departureMinutes: departMin,
        departureHm: minutesToHm(departMin),
      })
      const segDuration = Math.max(0, parseFloat(seg.duration_minutes) || 0)
      minutes = departMin + segDuration
    }
  }

  const lastStay = Math.max(0, parseFloat(stay[segs.length]) || 0)
  result.push({
    arrivalMinutes: minutes,
    arrivalHm: minutesToHm(minutes),
    stayMinutes: lastStay,
    departureMinutes: minutes + lastStay,
    departureHm: minutesToHm(minutes + lastStay),
  })
  return result
}
