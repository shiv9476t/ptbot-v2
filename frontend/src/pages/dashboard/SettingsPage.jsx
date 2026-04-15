import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch, createPortalSession } from '../../lib/api'

export default function SettingsPage() {
  const { getToken } = useAuth()
  const [settings, setSettings] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    async function fetchSettings() {
      const token = await getToken()
      const data = await apiFetch('/api/dashboard/settings', token)
      setSettings(data)
    }
    fetchSettings()
  }, [])

  async function handleSave() {
    setSaving(true)
    const token = await getToken()
    await apiFetch('/api/dashboard/settings', token, {
      method: 'PUT',
      body: JSON.stringify({
        tone_config: settings.tone_config,
        calendly_link: settings.calendly_link,
        price_mode: settings.price_mode,
      })
    })
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  async function handleManageSubscription() {
    const token = await getToken()
    const data = await createPortalSession(token)
    window.location.href = data.url
  }

  if (!settings) return <p className="text-gray-400">Loading...</p>

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="flex flex-col gap-6">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Calendly Link</label>
          <input
            type="text"
            value={settings.calendly_link || ''}
            onChange={e => setSettings({ ...settings, calendly_link: e.target.value })}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white outline-none focus:border-blue-500"
            placeholder="https://calendly.com/your-link"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Price Mode</label>
          <select
            value={settings.price_mode}
            onChange={e => setSettings({ ...settings, price_mode: e.target.value })}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white outline-none focus:border-blue-500"
          >
            <option value="deflect">Deflect</option>
            <option value="reveal">Reveal</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Tone Config</label>
          <textarea
            value={settings.tone_config || ''}
            onChange={e => setSettings({ ...settings, tone_config: e.target.value })}
            rows={6}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white outline-none focus:border-blue-500"
            placeholder="Describe the bot's tone and personality..."
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
        >
          {saving ? 'Saving...' : saved ? 'Saved!' : 'Save changes'}
        </button>

        <button
          onClick={handleManageSubscription}
          className="bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium px-6 py-2 rounded-lg w-fit"
        >
          Manage subscription
        </button>
      </div>
    </div>
  )
}