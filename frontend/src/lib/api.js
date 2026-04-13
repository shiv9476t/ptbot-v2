const API_URL = import.meta.env.VITE_API_URL

export async function apiFetch(endpoint, token, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

export async function createCheckoutSession(token) {
  return apiFetch('/api/dashboard/billing/create-checkout-session', token, { method: 'POST' })
}

export async function createPortalSession(token) {
  return apiFetch('/api/dashboard/billing/create-portal-session', token, { method: 'POST' })
}