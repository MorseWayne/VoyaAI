import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as plansApi from '@/api/plans'
import * as routesApi from '@/api/routes'
import { ensureDayStayArray } from '@/utils/time'

export const usePlanStore = defineStore('plan', () => {
  // Active plan being edited
  const activePlan = ref(null)
  // Currently selected day tab: 'overview' | number (0-based day index)
  const activeDetailTab = ref(0)
  // Route planner result data
  const currentPlanData = ref(null)
  // Temp start location for new plans
  const tempStartLocation = ref(null)

  /** Currently selected day index (for editing). Overview defaults to day 0. */
  function getCurrentDayIndex() {
    return activeDetailTab.value === 'overview' ? 0 : activeDetailTab.value
  }

  /** Get the effective end location of a day (last segment destination, or start if no segments). */
  function getDayEndLocation(dayIndex) {
    const days = activePlan.value?.days || []
    const day = days[dayIndex]
    if (!day) return null
    const segs = day.segments || []
    if (segs.length > 0) return segs[segs.length - 1].destination
    return getDayStartLocation(dayIndex)
  }

  /** Get the effective start location of a day (plan start / day start_location / or previous day end). */
  function getDayStartLocation(dayIndex) {
    const days = activePlan.value?.days || []
    if (dayIndex === 0) return activePlan.value?.start_location ?? null
    const day = days[dayIndex]
    if (!day) return null
    if (day.start_location) return day.start_location
    return getDayEndLocation(dayIndex - 1)
  }

  /** Set the start location for a day (day 0 → plan.start_location; day N → days[N].start_location). */
  function setDayStartLocation(dayIndex, loc) {
    if (!activePlan.value) return
    const locObj = {
      name: loc.name,
      lat: loc.lat,
      lng: loc.lng,
      address: loc.address,
      city: loc.city,
    }
    if (dayIndex === 0) {
      activePlan.value.start_location = locObj
    } else {
      const day = activePlan.value.days[dayIndex]
      if (day) day.start_location = locObj
    }
  }

  /** Sync tempStartLocation to the current day's effective start when that day has no segments. */
  function syncTempStartLocationForCurrentDay() {
    const dayIdx = getCurrentDayIndex()
    const days = activePlan.value?.days || []
    const day = days[dayIdx]
    const hasSegments = day?.segments?.length > 0
    if (hasSegments) {
      tempStartLocation.value = null
      return
    }
    tempStartLocation.value = getDayStartLocation(dayIdx) || null
  }

  /** Save the active plan silently (no UI feedback) */
  async function saveActivePlanSilently() {
    if (!activePlan.value) return
    const planToSave = JSON.parse(JSON.stringify(activePlan.value))
    delete planToSave.tempStartLocation
    // Clean internal markers
    ;(planToSave.days || []).forEach(d => {
      ;(d.segments || []).forEach(seg => { delete seg._amapAttempted })
    })
    try {
      const saved = await plansApi.savePlan(planToSave)
      if (saved.id) activePlan.value.id = saved.id
      if (saved.created_at) activePlan.value.created_at = saved.created_at
    } catch (e) {
      console.error('[auto-save]', e)
    }
  }

  /** Save active plan with UI feedback */
  async function saveActivePlan() {
    if (!activePlan.value) return
    const planToSave = JSON.parse(JSON.stringify(activePlan.value))
    delete planToSave.tempStartLocation
    ;(planToSave.days || []).forEach(d => {
      ;(d.segments || []).forEach(seg => { delete seg._amapAttempted })
    })
    const saved = await plansApi.savePlan(planToSave)
    if (saved.id) activePlan.value.id = saved.id
    if (saved.created_at) activePlan.value.created_at = saved.created_at
    return saved
  }

  /** Sync title from metadata (start location, date, days) */
  function syncPlanTitleFromMeta() {
    if (!activePlan.value || !activePlan.value.days.length) return
    const locationPart = (activePlan.value.start_location?.name)
      || (activePlan.value.title?.includes(' · ')
        ? activePlan.value.title.split(' · ')[0].trim()
        : '')
    const dateStr = activePlan.value.days[0].date
      ? new Date(activePlan.value.days[0].date).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
      : ''
    const dayCount = activePlan.value.days.length
    activePlan.value.title = locationPart
      ? `${locationPart} · ${dateStr}出发 · ${dayCount}日旅行`
      : `${dateStr}出发 · ${dayCount}日旅行`
  }

  /** Update departure date and recalculate all day dates */
  function updatePlanDepartureDate(dateStr) {
    if (!activePlan.value || !dateStr || !activePlan.value.days.length) return
    const start = new Date(dateStr)
    activePlan.value.days.forEach((day, i) => {
      const d = new Date(start)
      d.setDate(d.getDate() + i)
      day.date = d.toISOString().split('T')[0]
    })
    syncPlanTitleFromMeta()
  }

  /** Update number of travel days */
  function updatePlanDaysCount(newCount) {
    if (!activePlan.value || newCount < 1 || newCount > 30) return
    const current = activePlan.value.days.length
    if (newCount === current) return

    if (newCount < current) {
      const toRemove = activePlan.value.days.slice(newCount)
      const hasContent = toRemove.some(d => d.segments && d.segments.length > 0)
      if (hasContent && !confirm(`将删除第 ${newCount + 1}～${current} 天的行程内容，确定继续？`)) {
        return false
      }
      activePlan.value.days.length = newCount
      if (activeDetailTab.value !== 'overview' && activeDetailTab.value >= newCount) {
        activeDetailTab.value = newCount - 1
      }
    } else {
      const lastDate = activePlan.value.days[activePlan.value.days.length - 1].date
      const base = lastDate ? new Date(lastDate) : new Date()
      for (let i = current; i < newCount; i++) {
        const d = new Date(base)
        d.setDate(d.getDate() + (i - current + 1))
        activePlan.value.days.push({
          day_index: i + 1,
          date: d.toISOString().split('T')[0],
          city: activePlan.value.days[0].city || '',
          segments: [],
          start_time_hm: '08:00',
        })
      }
    }
    syncPlanTitleFromMeta()
    return true
  }

  /** Calculate segment data from API */
  async function calculateSegmentData(origin, dest, mode) {
    const city = activePlan.value?.days?.[getCurrentDayIndex()]?.city || ''
    return routesApi.calculateSegment(origin.name, dest.name, mode, city)
  }

  /** Add a segment between origin and destination */
  async function addSegment(origin, dest) {
    const defaultMode = 'driving'
    try {
      const result = await calculateSegmentData(origin, dest, defaultMode)
      activePlan.value.days[getCurrentDayIndex()].segments.push({
        type: defaultMode,
        origin,
        destination: dest,
        distance_km: result.distance_km,
        duration_minutes: result.duration_minutes,
      })
    } catch (e) {
      activePlan.value.days[getCurrentDayIndex()].segments.push({
        type: defaultMode,
        origin,
        destination: dest,
        distance_km: 0,
        duration_minutes: 0,
      })
    }
    ensureDayStayArray(activePlan.value.days[getCurrentDayIndex()])
  }

  /** Insert a location at a specific index */
  async function insertSegmentAt(locationIndex, newLoc) {
    const dayIdx = getCurrentDayIndex()
    const segments = activePlan.value.days[dayIdx].segments
    const defaultMode = 'driving'

    if (newLoc.city && !activePlan.value.days[dayIdx].city) {
      activePlan.value.days[dayIdx].city = newLoc.city
    }

    try {
      if (locationIndex === 0) {
        const firstOrigin = segments[0].origin
        const result = await calculateSegmentData(newLoc, firstOrigin, defaultMode)
        segments.unshift({
          type: defaultMode, origin: newLoc, destination: firstOrigin,
          distance_km: result.distance_km, duration_minutes: result.duration_minutes,
        })
      } else {
        const prev = segments[locationIndex - 1]
        const [res1, res2] = await Promise.all([
          calculateSegmentData(prev.origin, newLoc, defaultMode),
          calculateSegmentData(newLoc, prev.destination, defaultMode),
        ]).catch(() => [{ distance_km: 0, duration_minutes: 0 }, { distance_km: 0, duration_minutes: 0 }])
        segments.splice(locationIndex - 1, 1,
          { type: defaultMode, origin: prev.origin, destination: newLoc, distance_km: res1.distance_km, duration_minutes: res1.duration_minutes },
          { type: defaultMode, origin: newLoc, destination: prev.destination, distance_km: res2.distance_km, duration_minutes: res2.duration_minutes },
        )
      }
    } catch {
      if (locationIndex === 0) {
        segments.unshift({ type: defaultMode, origin: newLoc, destination: segments[0].origin, distance_km: 0, duration_minutes: 0 })
      } else {
        const prev = segments[locationIndex - 1]
        segments.splice(locationIndex - 1, 1,
          { type: defaultMode, origin: prev.origin, destination: newLoc, distance_km: 0, duration_minutes: 0 },
          { type: defaultMode, origin: newLoc, destination: prev.destination, distance_km: 0, duration_minutes: 0 },
        )
      }
    }
    ensureDayStayArray(activePlan.value.days[dayIdx])
    const stay = activePlan.value.days[dayIdx].location_stay_minutes
    if (stay && locationIndex >= 0 && locationIndex <= stay.length) {
      stay.splice(locationIndex, 0, 0)
    }
  }

  /** Remove a location at a given index */
  async function removeLocation(index, isLast) {
    const dayIdx = getCurrentDayIndex()
    const segments = activePlan.value.days[dayIdx].segments

    if (tempStartLocation.value && segments.length === 0) {
      tempStartLocation.value = null
      return
    }

    const day = activePlan.value.days[dayIdx]
    ensureDayStayArray(day)
    const stay = day.location_stay_minutes

    if (index === 0) {
      if (segments.length === 1) {
        tempStartLocation.value = segments[0].destination
        segments.shift()
        if (stay.length > 0) stay.shift()
      } else {
        segments.shift()
        if (stay.length > 0) stay.shift()
      }
    } else if (isLast) {
      segments.pop()
      if (stay.length > 0) stay.pop()
    } else {
      const prevSeg = segments[index - 1]
      const nextSeg = segments[index]
      const newOrigin = prevSeg.origin
      const newDest = nextSeg.destination
      segments.splice(index - 1, 2)
      if (stay.length > index) stay.splice(index, 1)
      try {
        const res = await calculateSegmentData(newOrigin, newDest, 'driving')
        segments.splice(index - 1, 0, {
          type: 'driving', origin: newOrigin, destination: newDest,
          distance_km: res.distance_km, duration_minutes: res.duration_minutes,
        })
      } catch {
        segments.splice(index - 1, 0, {
          type: 'driving', origin: newOrigin, destination: newDest,
          distance_km: 0, duration_minutes: 0,
        })
      }
    }
  }

  /** Change transport mode for a segment */
  async function changeTransportMode(segmentIndex, mode) {
    const dayIdx = getCurrentDayIndex()
    const segment = activePlan.value.days[dayIdx].segments[segmentIndex]
    if (!segment || segment.type === mode) return

    const result = await calculateSegmentData(segment.origin, segment.destination, mode)
    segment.type = mode
    segment.distance_km = result.distance_km
    segment.duration_minutes = result.duration_minutes
  }

  /** Replace a segment with flight/train ticket data (e.g. after uploading ticket screenshot). */
  function replaceSegmentWithTicketData(segmentIndex, ticketData) {
    const dayIdx = getCurrentDayIndex()
    const segments = activePlan.value?.days?.[dayIdx]?.segments
    if (!segments || segmentIndex < 0 || segmentIndex >= segments.length) return
    const segment = segments[segmentIndex]

    const originLoc = {
      ...segment.origin,
      name: ticketData.departure_station || ticketData.origin_name || segment.origin?.name || '出发地',
      city: ticketData.departure_city || ticketData.origin_city || segment.origin?.city || '',
      departure_time: ticketData.departure_time,
    }
    const destLoc = {
      ...segment.destination,
      name: ticketData.arrival_station || ticketData.destination_name || segment.destination?.name || '目的地',
      city: ticketData.arrival_city || ticketData.destination_city || segment.destination?.city || '',
      arrival_time: ticketData.arrival_time,
    }
    const durationMin = ticketData.duration_seconds ? Math.round(ticketData.duration_seconds / 60) : (segment.duration_minutes || 0)

    segment.type = ticketData.type || 'flight'
    segment.origin = originLoc
    segment.destination = destLoc
    segment.distance_km = ticketData.distance_km ?? segment.distance_km ?? 0
    segment.duration_minutes = durationMin
    segment.details = {
      flight_no: ticketData.flight_no,
      train_no: ticketData.train_no,
      departure_time: ticketData.departure_time,
      arrival_time: ticketData.arrival_time,
      seat_info: ticketData.seat_info,
    }
    saveActivePlanSilently()
  }

  /** Reorder locations within a day */
  async function reorderLocations(dayIndex, fromIndex, toIndex) {
    const day = activePlan.value.days[dayIndex]
    const segments = day.segments
    const locations = []

    if (segments.length > 0) {
      locations.push(segments[0].origin)
      segments.forEach(seg => locations.push(seg.destination))
    } else {
      return
    }

    if (fromIndex < 0 || fromIndex >= locations.length || toIndex < 0 || toIndex >= locations.length) return

    const [movedItem] = locations.splice(fromIndex, 1)
    locations.splice(toIndex, 0, movedItem)

    if (dayIndex === 0 && locations.length > 0) {
      activePlan.value.start_location = {
        name: locations[0].name,
        address: locations[0].address,
        city: locations[0].city,
        lat: locations[0].lat,
        lng: locations[0].lng,
      }
      tempStartLocation.value = null
    }

    ensureDayStayArray(day)
    const [movedStay] = day.location_stay_minutes.splice(fromIndex, 1)
    day.location_stay_minutes.splice(toIndex, 0, movedStay)

    const newSegments = []
    for (let i = 0; i < locations.length - 1; i++) {
      newSegments.push({
        type: 'driving', origin: locations[i], destination: locations[i + 1],
        distance_km: 0, duration_minutes: 0,
      })
    }
    day.segments = newSegments

    const promises = newSegments.map(seg =>
      calculateSegmentData(seg.origin, seg.destination, seg.type)
        .then(res => {
          seg.distance_km = res.distance_km
          seg.duration_minutes = res.duration_minutes
        })
        .catch(() => {}),
    )
    await Promise.all(promises)
    saveActivePlanSilently()
  }

  return {
    activePlan,
    activeDetailTab,
    currentPlanData,
    tempStartLocation,
    getCurrentDayIndex,
    getDayStartLocation,
    getDayEndLocation,
    setDayStartLocation,
    syncTempStartLocationForCurrentDay,
    saveActivePlanSilently,
    saveActivePlan,
    syncPlanTitleFromMeta,
    updatePlanDepartureDate,
    updatePlanDaysCount,
    calculateSegmentData,
    addSegment,
    insertSegmentAt,
    removeLocation,
    changeTransportMode,
    replaceSegmentWithTicketData,
    reorderLocations,
  }
})
