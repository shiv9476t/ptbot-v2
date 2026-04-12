import { Link } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

export default function DashboardLayout({ children }) {
  const { signOut } = useAuth()

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      
      {/* Sidebar */}
      <div className="w-56 border-r border-gray-800 flex flex-col p-4">
        <div className="text-lg font-bold mb-8">PTBot</div>
        <nav className="flex flex-col gap-2">
          <Link to="/dashboard/overview" className="px-3 py-2 rounded-md hover:bg-gray-800 text-sm">
            Overview
          </Link>
          <Link to="/dashboard/conversations" className="px-3 py-2 rounded-md hover:bg-gray-800 text-sm">
            Conversations
          </Link>
          <Link to="/dashboard/settings" className="px-3 py-2 rounded-md hover:bg-gray-800 text-sm">
            Settings
          </Link>
        </nav>
        <div className="mt-auto">
          <button onClick={() => signOut()} className="px-3 py-2 text-sm text-gray-400 hover:text-white">
            Sign out
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-8">
        {children}
      </div>

    </div>
  )
}