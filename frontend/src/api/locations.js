import { get, post } from './client'

export function searchLocationTips(keywords, city = '') {
  return get(`/travel/locations/tips?keywords=${encodeURIComponent(keywords)}&city=${encodeURIComponent(city)}`)
}

export function searchLocations(query, city = '') {
  return post('/travel/locations/search', { query, city })
}

export function resolveLocation(query, city = '') {
  return post('/travel/locations/resolve', { query, city })
}
