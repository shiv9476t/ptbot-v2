import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { createCheckoutSession } from '../../lib/api'

export default function CheckoutPage() {
  const { getToken } = useAuth()
  const [error, setError] = useState(false)

  async function startCheckout() {
    setError(false)
    try {
      const token = await getToken()
      const data = await createCheckoutSession(token)
      window.location.href = data.url
    } catch {
      setError(true)
    }
  }

  useEffect(() => {
    startCheckout()
  }, [])

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">Something went wrong. Please try again.</p>
          <button
            onClick={startCheckout}
            className="bg-white text-gray-950 px-4 py-2 rounded-lg font-medium hover:bg-gray-100"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <p className="text-gray-400">Setting up your subscription...</p>
    </div>
  )
}
