import { post } from './client'

export function optimizeRoute(locations, city, strategy, preference) {
  return post('/travel/optimize', { locations, city, strategy, preference })
}

export function calculateSegment(origin, destination, mode, city = '') {
  return post('/travel/calculate-segment', { origin, destination, mode, city })
}
