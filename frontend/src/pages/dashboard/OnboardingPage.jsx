import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch } from '../../lib/api'

export default function OnboardingPage() {
  const { getToken } = useAuth()
  const [settings, setSettings] = useState(null)
  const [websiteUrl, setWebsiteUrl] = useState('')
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [calendlyLink, setCalendlyLink] = useState('')
  const [saving, setSaving] = useState(false)

  async function fetchSettings() {
    const token = await getToken()
    const data = await apiFetch('/api/dashboard/settings', token)
    setSettings(data)
  }

  useEffect(() => { fetchSettings() }, [])

  async function connectInstagram() {
    const token = await getToken()
    const data = await apiFetch('/auth/instagram', token)
    window.location.href = data.url
  }

  async function generateKb() {
    setGenerating(true)
    setError(null)
    try {
      const token = await getToken()
      await apiFetch('/api/dashboard/onboarding/generate', token, {
        method: 'POST',
        body: JSON.stringify({ website_url: websiteUrl || null }),
      })
      await fetchSettings()
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  async function saveCalendly() {
    setSaving(true)
    setError(null)
    try {
      const token = await getToken()
      await apiFetch('/api/dashboard/settings', token, {
        method: 'PUT',
        body: JSON.stringify({ calendly_link: calendlyLink }),
      })
      await fetchSettings()
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  if (!settings) return <p className="text-gray-500">Loading...</p>

  if (!settings.instagram_account_id) {
    return (
      <div className="max-w-lg">
        <h1 className="text-2xl font-bold mb-2">Step 1: Connect your Instagram account</h1>
        <p className="text-gray-500 mb-6">PTBot needs access to your Instagram DMs to qualify your leads automatically.</p>
        <button
          onClick={connectInstagram}
          className="bg-black hover:bg-gray-800 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
        >
          Connect Instagram
        </button>
      </div>
    )
  }

  if (!settings.onboarding_complete) {
    return (
      <div className="max-w-lg">
        <h1 className="text-2xl font-bold mb-2">Step 2: Set up your bot</h1>
        <p className="text-gray-500 mb-6">We'll pull your recent Instagram posts and generate a knowledge base so your bot sounds like you.</p>
        <div className="flex flex-col gap-3">
          <input
            type="text"
            value={websiteUrl}
            onChange={e => setWebsiteUrl(e.target.value)}
            className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm outline-none focus:border-blue-500"
            placeholder="https://yourwebsite.com (optional)"
          />
          <button
            onClick={generateKb}
            disabled={generating}
            className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
          >
            {generating ? 'Setting up your bot...' : 'Generate my knowledge base'}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      </div>
    )
  }

  if (!settings.calendly_link) {
    return (
      <div className="max-w-lg">
        <h1 className="text-2xl font-bold mb-2">Step 3: Add your Calendly link</h1>
        <p className="text-gray-500 mb-6">This is where qualified leads will be sent to book a discovery call with you.</p>
        <div className="flex flex-col gap-3">
          <input
            type="text"
            value={calendlyLink}
            onChange={e => setCalendlyLink(e.target.value)}
            className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm outline-none focus:border-blue-500"
            placeholder="https://calendly.com/your-link"
          />
          <button
            onClick={saveCalendly}
            disabled={saving}
            className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
          >
            {saving ? 'Saving...' : 'Save and finish'}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold mb-2">Your bot is ready 🎉</h1>
      <p className="text-gray-500 mb-6">PTBot is live on your Instagram. Leads who DM you will be qualified automatically.</p>
      <div className="flex flex-col gap-3">
        <input
          type="text"
          value={websiteUrl}
          onChange={e => setWebsiteUrl(e.target.value)}
          className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm outline-none focus:border-blue-500"
          placeholder="https://yourwebsite.com (optional)"
        />
        <button
          onClick={generateKb}
          disabled={generating}
          className="bg-black hover:bg-gray-800 disabled:opacity-50 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
        >
          {generating ? 'Setting up your bot...' : 'Regenerate knowledge base'}
        </button>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>
    </div>
  )
}
