const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')

async function request(path, { signal } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) message = typeof body.detail === 'string' ? body.detail : message
    } catch {
      // Keep the HTTP fallback message.
    }
    throw new Error(message)
  }
  return response.json()
}

export function getArticles(params, options) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value)
  })
  return request(`/articles?${query.toString()}`, options)
}

export function getSources(options) {
  return request('/sources', options)
}

export function getCategories(options) {
  return request('/categories', options)
}
