const API_URL = 'http://localhost:8000/api/trips/'
const GEOCODE_URL = 'http://localhost:8000/api/geocode/'

export class ApiError extends Error {}

const describe = (value) => (Array.isArray(value) ? value.join(' ') : String(value))

const humanize = (field) => field.replace(/_/g, ' ')

function formatApiError(data, status) {
  if (data && typeof data === 'object') {
    if (data.error) return describe(data.error)
    if (data.detail) return describe(data.detail)
    const entries = Object.entries(data)
    if (entries.length > 0) {
      return entries.map(([field, msgs]) => `${humanize(field)}: ${describe(msgs)}`).join('; ')
    }
  }

  // A bare string is useful when it is a real message, but not when the server
  // returned an HTML error page (e.g. Django's DEBUG traceback).
  if (typeof data === 'string' && data.trim() && !data.trim().startsWith('<')) {
    return data
  }

  return `Server error (HTTP ${status})`
}

async function readBody(res) {
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return res.json().catch(() => null)
  }
  return res.text().catch(() => null)
}

export async function createTrip(payload) {
  let res
  try {
    res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (cause) {
    throw new ApiError('Failed to connect to backend. Is it running on port 8000?', { cause })
  }

  const data = await readBody(res)

  if (!res.ok) {
    throw new ApiError(formatApiError(data, res.status))
  }

  if (!data || typeof data !== 'object') {
    throw new ApiError('Backend returned an unexpected response')
  }

  return data
}

export async function searchLocations(query) {
  const trimmed = query.trim()
  if (!trimmed) return []

  let res
  try {
    res = await fetch(`${GEOCODE_URL}?q=${encodeURIComponent(trimmed)}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
  } catch (cause) {
    throw new ApiError('Failed to connect to backend. Is it running on port 8000?', { cause })
  }

  const data = await readBody(res)

  if (!res.ok) {
    throw new ApiError(formatApiError(data, res.status))
  }

  if (!data || !Array.isArray(data.suggestions)) {
    throw new ApiError('Backend returned an unexpected geocoding response')
  }

  return data.suggestions
}
