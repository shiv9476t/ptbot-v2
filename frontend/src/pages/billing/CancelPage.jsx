import { Link } from 'react-router-dom'

export default function CancelPage() {
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="text-center">
        <p className="text-gray-400 mb-6">No worries — you can subscribe whenever you're ready.</p>
        <Link
          to="/pricing"
          className="bg-white text-gray-950 px-4 py-2 rounded-lg font-medium hover:bg-gray-100"
        >
          Back to pricing
        </Link>
      </div>
    </div>
  )
}
