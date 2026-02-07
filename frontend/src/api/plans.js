import { get, post, del } from './client'

export function fetchPlans() {
  return get('/travel/plans')
}

export function fetchPlan(id) {
  return get(`/travel/plans/${id}`)
}

export function savePlan(plan) {
  return post('/travel/plans', plan)
}

export function deletePlan(id) {
  return del(`/travel/plans/${id}`)
}

export function parseTicket(imageBase64) {
  return post('/travel/parse-ticket', { image_base64: imageBase64 })
}

export function generateTitle(cities, days) {
  return post('/travel/generate-title', { cities, days })
}
