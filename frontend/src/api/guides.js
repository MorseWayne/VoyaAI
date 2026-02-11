import { get, post, del } from './client'

export const listGuides = () => {
  return get('/guides')
}

export const getGuide = (id) => {
  return get(`/guides/${id}`)
}

export const importGuide = (content) => {
  return post('/guides/import', { content })
}

export const deleteGuide = (id) => {
  return del(`/guides/${id}`)
}
