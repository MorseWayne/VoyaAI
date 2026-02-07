/**
 * HTTP client wrapper for API calls.
 */

const BASE_URL = ''

export async function request(url, options = {}) {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || data.message || `Request failed: ${response.status}`)
  }

  return data
}

export function get(url) {
  return request(url)
}

export function post(url, body) {
  return request(url, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function del(url) {
  return request(url, { method: 'DELETE' })
}
