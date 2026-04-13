import Navbar from '../../components/shared/Navbar'
import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-black">
      <Navbar />
      
      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-24 pb-20 text-center">
        <h1 className="text-5xl font-bold leading-tight mb-6">
          Qualify leads and book discovery calls.<br />
          <span className="text-gray-400">Automatically.</span>
        </h1>
        <p className="text-lg text-gray-500 mb-10 max-w-xl mx-auto">
          PTBot handles your Instagram DMs — qualifying leads, nurturing conversations, and booking discovery calls in your own voice.
        </p>
        <Link
          to="/sign-up"
          className="bg-black text-white px-8 py-3 rounded-lg font-medium hover:bg-gray-800 inline-block"
        >
          Get started free
        </Link>
      </section>
        
          {/* Features */}
        <section className="max-w-4xl mx-auto px-6 py-20 border-t border-gray-100">
          <div className="grid grid-cols-3 gap-12">
            <div>
              <h3 className="font-semibold text-lg mb-2">Qualifies leads</h3>
              <p className="text-gray-500 text-sm leading-relaxed">
                Asks the right questions to identify serious prospects and filter out time-wasters automatically.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Matches your voice</h3>
              <p className="text-gray-500 text-sm leading-relaxed">
                Trained on your content so every reply sounds like you — not a generic chatbot.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Books discovery calls</h3>
              <p className="text-gray-500 text-sm leading-relaxed">
                Moves qualified leads to your Calendly link at the right moment in the conversation.
              </p>
            </div>
          </div>
        </section>
          
        {/* CTA */}
        <section className="max-w-4xl mx-auto px-6 py-20 border-t border-gray-100 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to automate your DMs?</h2>
          <p className="text-gray-500 mb-8">Join PTs already using PTBot to qualify leads and book more calls.</p>
          <Link
            to="/sign-up"
            className="bg-black text-white px-8 py-3 rounded-lg font-medium hover:bg-gray-800 inline-block"
          >
            Get started free
          </Link>
        </section>
    </div>
  )
}