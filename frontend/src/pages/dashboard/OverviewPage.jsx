import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch } from '../../lib/api'

export default function OverviewPage() {
  const { getToken } = useAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    async function fetchStats() {
      const token = await getToken()
      const data = await apiFetch('/api/dashboard/overview', token)
      setStats(data)
    }
    fetchStats()
  }, [])

  if (!stats) return <p>Loading...</p>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Overview</h1>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-500 text-sm">Total Leads</p>
          <p className="text-3xl font-bold">{stats.total_leads}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-500 text-sm">Qualified</p>
          <p className="text-3xl font-bold">{stats.qualified}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-500 text-sm">Booked</p>
          <p className="text-3xl font-bold">{stats.booked}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-500 text-sm">Conversion Rate</p>
          <p className="text-3xl font-bold">{stats.conversion_rate}%</p>
        </div>
      </div>
    </div>
  )
}