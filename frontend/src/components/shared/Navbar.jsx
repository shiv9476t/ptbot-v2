import { Link } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

export default function Navbar() {
  const { isSignedIn } = useAuth()

  return (
    <nav className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <Link to="/" className="text-black font-bold text-lg">PTBot</Link>
      <div className="flex items-center gap-4">
        <Link to="/pricing" className="text-sm text-gray-600 hover:text-black">Pricing</Link>
        {isSignedIn ? (
          <Link to="/dashboard/overview" className="text-sm bg-black text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-800">
            Dashboard
          </Link>
        ) : (
          <Link to="/sign-in" className="text-sm bg-black text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-800">
            Sign in
          </Link>
        )}
      </div>
    </nav>
  )
}