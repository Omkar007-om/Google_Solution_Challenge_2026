const DEFAULT_API = ''

function getApiBase() {
  return import.meta.env?.VITE_API_URL || DEFAULT_API
}

async function request(path, { method = 'GET', headers, body } = {}) {
  const base = getApiBase()
  const h = new Headers(headers || {})
  h.set('Accept', 'application/json')

  let res
  try {
    res = await fetch(`${base}${path}`, { method, headers: h, body })
  } catch {
    throw new Error('Unable to reach backend. Start backend on port 8000 and retry.')
  }
  const text = await res.text()
  const json = text ? JSON.parse(text) : null
  if (!res.ok) {
    const msg = json?.error || json?.detail?.error || json?.detail || `HTTP ${res.status}`
    const err = new Error(typeof msg === 'string' ? msg : 'Request failed')
    err.status = res.status
    err.payload = json
    throw err
  }
  return json
}

export async function analyzeCsv({ file, subjectAccount }) {
  const fd = new FormData()
  fd.append('file', file)
  if (subjectAccount) fd.append('subject_account', subjectAccount)
  return request('/api/v1/analyze/csv', { method: 'POST', body: fd })
}

