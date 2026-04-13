import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch } from '../../lib/api'

const POLL_INTERVAL_MS = 2000
const TIMEOUT_MS = 30000

export default function SuccessPage() {
  const { getToken } = useAuth()
  const navigate = useNavigate()
  const [timedOut, setTimedOut] = useState(false)
  const intervalRef = useRef(null)
  const timeoutRef = useRef(null)

  useEffect(() => {
    async function checkStatus() {
      try {
        const token = await getToken()
        const data = await apiFetch('/api/dashboard/billing/status', token)
        if (data.subscription_status === 'active' || data.subscription_status === 'trialing') {
          clearInterval(intervalRef.current)
          clearTimeout(timeoutRef.current)
          navigate('/dashboard/overview')
        }
      } catch {
        // keep polling
      }
    }

    intervalRef.current = setInterval(checkStatus, POLL_INTERVAL_MS)

    timeoutRef.current = setTimeout(() => {
      clearInterval(intervalRef.current)
      setTimedOut(true)
    }, TIMEOUT_MS)

    checkStatus()

    return () => {
      clearInterval(intervalRef.current)
      clearTimeout(timeoutRef.current)
    }
  }, [])

  if (timedOut) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <p className="text-gray-400 text-center">
          This is taking longer than expected — please contact support.
        </p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <p className="text-gray-400">Activating your account...</p>
    </div>
  )
}
