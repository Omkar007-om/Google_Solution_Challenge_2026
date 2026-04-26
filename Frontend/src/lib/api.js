const DEFAULT_API = ''

function getApiBase() {
  return import.meta.env?.VITE_API_URL || DEFAULT_API
}

export function getToken() {
  try {
    return localStorage.getItem('nexus.jwt') || ''
  } catch {
    return ''
  }
}

export function getSessionToken() {
  try {
    return sessionStorage.getItem('nexus.jwt') || ''
  } catch {
    return ''
  }
}

export function getAnyToken() {
  return getToken() || getSessionToken()
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem('nexus.jwt', token)
    else localStorage.removeItem('nexus.jwt')
  } catch {
    // ignore
  }
}

export function setSessionToken(token) {
  try {
    if (token) sessionStorage.setItem('nexus.jwt', token)
    else sessionStorage.removeItem('nexus.jwt')
  } catch {
    // ignore
  }
}

async function request(path, { method = 'GET', headers, body, auth = true } = {}) {
  const base = getApiBase()
  const h = new Headers(headers || {})
  h.set('Accept', 'application/json')
  if (auth) {
    const t = getAnyToken()
    if (t) h.set('Authorization', `Bearer ${t}`)
  }

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

export async function login({ username, password }) {
  return request('/api/v1/auth/login', {
    method: 'POST',
    auth: false,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

export async function me() {
  return request('/api/v1/auth/me', { method: 'GET' })
}

export async function analyzeCsv({ file, subjectAccount }) {
  const fd = new FormData()
  fd.append('file', file)
  if (subjectAccount) fd.append('subject_account', subjectAccount)
  return request('/api/v1/analyze/csv', { method: 'POST', body: fd })
}

