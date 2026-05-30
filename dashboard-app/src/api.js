const API = import.meta.env.VITE_API_URL || 'https://sentinel-mind-9iyt.onrender.com'

const getHeaders = () => {
  const token = localStorage.getItem('sm_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

export const auth = {
  register: (data) => fetch(`${API}/v1/auth/register`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) }).then(r => r.json()),
  login: (data) => fetch(`${API}/v1/auth/login`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) }).then(r => r.json()),
}

export const users = {
  me: () => fetch(`${API}/v1/users/me`, { headers: getHeaders() }).then(r => r.json()),
  usage: () => fetch(`${API}/v1/users/usage`, { headers: getHeaders() }).then(r => r.json()),
  apiKeys: () => fetch(`${API}/v1/users/api-keys`, { headers: getHeaders() }).then(r => r.json()),
  createKey: (name) => fetch(`${API}/v1/users/api-keys`, { method: 'POST', headers: getHeaders(), body: JSON.stringify({ name }) }).then(r => r.json()),
  revokeKey: (id) => fetch(`${API}/v1/users/api-keys/${id}`, { method: 'DELETE', headers: getHeaders() }),
}

export const billing = {
  plans: () => fetch(`${API}/v1/billing/plans`, { headers: getHeaders() }).then(r => r.json()),
  status: () => fetch(`${API}/v1/billing/billing`, { headers: getHeaders() }).then(r => r.json()),
  checkout: (plan, callback_url) => fetch(`${API}/v1/billing/checkout`, { method: 'POST', headers: getHeaders(), body: JSON.stringify({ plan, callback_url }) }).then(r => r.json()),
  verify: (reference) => fetch(`${API}/v1/billing/verify`, { method: 'POST', headers: getHeaders(), body: JSON.stringify({ reference }) }).then(r => r.json()),
}

export const scans = {
  url: (apiKey, url) => fetch(`${API}/v1/shield-phish/scan/url`, { method: 'POST', headers: { ...getHeaders(), 'X-API-Key': apiKey }, body: JSON.stringify({ url }) }).then(r => r.json()),
  email: (apiKey, data) => fetch(`${API}/v1/shield-phish/scan/email`, { method: 'POST', headers: { ...getHeaders(), 'X-API-Key': apiKey }, body: JSON.stringify(data) }).then(r => r.json()),
  code: (apiKey, data) => fetch(`${API}/v1/shield-dev/scan/code`, { method: 'POST', headers: { ...getHeaders(), 'X-API-Key': apiKey }, body: JSON.stringify(data) }).then(r => r.json()),
  logs: (apiKey, data) => fetch(`${API}/v1/shield-soc/analyze/logs`, { method: 'POST', headers: { ...getHeaders(), 'X-API-Key': apiKey }, body: JSON.stringify(data) }).then(r => r.json()),
  image: (apiKey, data) => fetch(`${API}/v1/shield-id/scan/image`, { method: 'POST', headers: { ...getHeaders(), 'X-API-Key': apiKey }, body: JSON.stringify(data) }).then(r => r.json()),
}
