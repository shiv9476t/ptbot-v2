import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-blue-500">Home</h1>
      <Link to="/pricing" className="text-sm text-gray-400 hover:text-white">
        Go to Pricing
      </Link>
    </div>
  )
}