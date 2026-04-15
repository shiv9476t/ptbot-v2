import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../../components/shared/Navbar'

const CONVERSATION = [
  { role: 'lead', text: 'Hi, could you help me lose fat?' },
  { role: 'bot', text: "Hey! Absolutely, that's exactly what Tom specialises in. What's the main thing that's been frustrating you about fat loss lately?" },
  { role: 'lead', text: "I've been eating clean and exercising, but the scale isn't going down" },
  { role: 'bot', text: "That's frustrating as hell — doing everything 'right' but not seeing it reflected on the scale. How long have you been at it?" },
  { role: 'lead', text: "Been on and off for around a year now, I get demotivated when I don't see results" },
  { role: 'bot', text: "Makes complete sense — that cycle of starting strong then hitting a wall is brutal. What does your typical clean eating and exercise look like?" },
  { role: 'lead', text: 'Salads, protein shakes, fruits and veg, and I lift weights or run 3-4 times per week' },
  { role: 'bot', text: "Right, so you're putting in real effort — that's not a motivation problem. Sounds like you're eating the right foods but maybe not tracking the actual numbers?" },
  { role: 'lead', text: "Honestly, I hear a lot of conflicting information online, so I just try to stick to basic health advice. It's difficult to stick to though when I don't see results" },
  { role: 'bot', text: "Yeah, the internet is a nightmare for fitness advice. That constant start-stop cycle tells me you need a proper system, not just 'eat healthy and exercise.' What's your day-to-day look like — working, studying?" },
  { role: 'lead', text: 'Working full-time in finance, so busy but I manage to get workouts in' },
  { role: 'bot', text: "Finance — long hours and stress. Makes sense why you need something that actually works without the guesswork. Tom works specifically with busy professionals stuck in that exact cycle. Would you be up for a quick chat with him?" },
  { role: 'lead', text: "Not sure tbh, I had a coach a couple years ago but didn't enjoy working with him" },
  { role: 'bot', text: "Fair enough — a bad coaching experience will put anyone off. What went wrong — was it the approach, communication, or something else?" },
  { role: 'lead', text: "His approach wasn't flexible to my lifestyle. I wanted to skip breakfast but he didn't allow it" },
  { role: 'bot', text: "Ah — he was forcing you into his one-size-fits-all system instead of building around how you actually live. That's exactly the opposite of how Tom approaches it. His thing is making the programme fit your life, not the other way around. It's just a casual chat — no pressure, no pitch. Worth hearing how his approach would work around your finance schedule?" },
  { role: 'lead', text: "Yeah that makes sense, it's worth a try" },
  { role: 'bot', text: "Spot on. Here's Tom's booking link: calendly.com/holman-tom. It's just 20-30 minutes and he'll walk through exactly how he'd approach your situation." },
  { role: 'lead', text: 'Thank you, just booked in' },
  { role: 'bot', text: "Perfect — Tom will sort you out. Looking forward to hearing how it goes!" },
]

function useInView() {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setInView(true); observer.disconnect() } },
      { threshold: 0.1 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])
  return [ref, inView]
}

function FadeIn({ children, delay = 0 }) {
  const [ref, inView] = useInView()
  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={`transition-all duration-700 ${inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}`}
    >
      {children}
    </div>
  )
}

const serif = { fontFamily: "'DM Serif Display', serif" }
const sans = { fontFamily: 'system-ui, sans-serif' }

export default function HomePage() {
  const chatRef = useRef(null)
  const [form, setForm] = useState({ name: '', instagram: '', email: '' })

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [])

  function handleDemoSubmit(e) {
    e.preventDefault()
    const body = `Name: ${form.name}\nInstagram: @${form.instagram}\nEmail: ${form.email}`
    window.location.href = `mailto:shiv9476t@gmail.com?subject=PTBot Demo Request&body=${encodeURIComponent(body)}`
  }

  return (
    <div className="min-h-screen bg-white text-black">
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap');`}</style>

      <Navbar />

      {/* HERO */}
      <section className="max-w-7xl mx-auto px-6 pt-24 pb-20 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div>
          <h1 style={serif} className="text-5xl lg:text-6xl font-normal leading-tight mb-6">
            Every minute you don't reply, you're losing the lead.
          </h1>
          <p style={sans} className="text-lg text-gray-500 mb-10 leading-relaxed">
            PTBot qualifies your Instagram DMs, nurtures prospects, and books discovery calls — automatically, in your own voice.
          </p>
          <Link
            to="/sign-up"
            style={sans}
            className="bg-black text-white px-8 py-4 rounded-lg font-medium hover:bg-gray-800 inline-block text-base"
          >
            Start your free 14-day trial
          </Link>
        </div>

        {/* Instagram DM mockup */}
        <div className="rounded-2xl overflow-hidden shadow-2xl border border-gray-800" style={{ background: '#000' }}>
          <div className="px-4 py-3 border-b border-gray-800 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0" style={sans}>TH</div>
            <div>
              <p style={sans} className="text-white text-sm font-semibold">Tom Holman</p>
              <p style={sans} className="text-gray-500 text-xs">Active now</p>
            </div>
          </div>
          <div ref={chatRef} className="h-[480px] overflow-y-auto px-4 py-4 flex flex-col gap-3">
            {CONVERSATION.map((msg, i) => (
              <div key={i} className={`flex items-end gap-2 ${msg.role === 'lead' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'bot' && (
                  <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-white flex-shrink-0" style={{ ...sans, fontSize: '10px', fontWeight: 700 }}>TH</div>
                )}
                <div
                  className="max-w-[75%] px-3 py-2 text-sm leading-relaxed text-white"
                  style={{
                    ...sans,
                    background: msg.role === 'lead' ? '#0095f6' : '#262626',
                    borderRadius: msg.role === 'lead' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                  }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* STATS */}
      <section style={{ background: '#0a0a0a' }} className="py-24 text-white text-center">
        <FadeIn>
          <div className="max-w-3xl mx-auto px-6">
            <p style={serif} className="text-4xl lg:text-5xl font-normal leading-tight mb-6">
              Leads contacted within 5 minutes are 21x more likely to convert.
            </p>
            <p style={sans} className="text-gray-400 text-lg">
              The average PT takes hours to reply to a DM. PTBot responds instantly, 24/7.
            </p>
          </div>
        </FadeIn>
      </section>

      {/* WHY AUTOMATE */}
      <section className="py-24 bg-white">
        <div className="max-w-5xl mx-auto px-6">
          <FadeIn>
            <h2 style={serif} className="text-4xl font-normal mb-16 text-center">Stop leaving money in your inbox.</h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { title: 'Stop losing leads to slow replies', body: 'Every hour you don\u2019t reply, your prospect is talking to someone else. PTBot responds instantly, any time of day.' },
              { title: 'Only talk to serious prospects', body: 'PTBot qualifies leads before they reach you, so your calendar fills with people who are ready to invest.' },
              { title: 'Focus on coaching, not admin', body: 'Spend your time doing what you\u2019re good at. Let PTBot handle the repetitive first conversations.' },
            ].map((item, i) => (
              <FadeIn key={i} delay={i * 100}>
                <div className="border-t-2 border-black pt-6">
                  <h3 style={serif} className="text-xl font-normal mb-3">{item.title}</h3>
                  <p style={sans} className="text-gray-500 leading-relaxed text-sm">{item.body}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* WHY PTBOT */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-5xl mx-auto px-6">
          <FadeIn>
            <h2 style={serif} className="text-4xl font-normal mb-16 text-center">Why PTBot beats everything else.</h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { label: 'vs. doing it yourself', body: 'You can\u2019t reply to every DM instantly. PTBot can. And it never gets tired, forgets to follow up, or has an off day.' },
              { label: 'vs. generic DM tools', body: 'ManyChat and similar tools send scripted sequences. PTBot holds a real conversation, in your voice, trained on your content.' },
              { label: 'vs. hiring a VA', body: 'A VA costs more, works fewer hours, and needs managing. PTBot works 24/7 for a flat monthly fee.' },
            ].map((item, i) => (
              <FadeIn key={i} delay={i * 100}>
                <div className="bg-white rounded-2xl p-8 border border-gray-200">
                  <p style={{ ...sans, fontSize: '11px' }} className="font-semibold text-gray-400 uppercase tracking-widest mb-4">{item.label}</p>
                  <p style={sans} className="text-gray-700 leading-relaxed">{item.body}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section className="py-24 bg-white text-center">
        <div className="max-w-md mx-auto px-6">
          <FadeIn>
            <h2 style={serif} className="text-4xl font-normal mb-12">Simple pricing.</h2>
            <div className="border-2 border-black rounded-2xl p-10">
              <p style={serif} className="text-2xl font-normal mb-1">PTBot Pro</p>
              <p style={sans} className="text-gray-400 text-sm mb-6">14-day free trial, then</p>
              <p style={serif} className="text-6xl font-normal mb-1">£99</p>
              <p style={sans} className="text-gray-400 text-sm mb-8">per month</p>
              <ul style={sans} className="text-left space-y-3 mb-10">
                {[
                  'Unlimited DM conversations',
                  'Trained on your voice and content',
                  'Qualifies leads automatically',
                  'Books calls to your Calendly',
                  'Dashboard to track your leads',
                ].map((f, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-700 text-sm">
                    <span className="text-black font-bold">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link
                to="/sign-up"
                style={sans}
                className="block bg-black text-white px-8 py-4 rounded-lg font-medium hover:bg-gray-800 text-sm"
              >
                Start your free 14-day trial
              </Link>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* DEMO REQUEST */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-xl mx-auto px-6 text-center">
          <FadeIn>
            <h2 style={serif} className="text-4xl font-normal mb-4">Want to see PTBot in action on your own content?</h2>
            <p style={sans} className="text-gray-500 mb-10">
              We'll build a personalised demo trained on your Instagram content so you can see exactly how it would sound as you.
            </p>
            <form onSubmit={handleDemoSubmit} className="flex flex-col gap-4 text-left" style={sans}>
              <input
                type="text" required placeholder="Your name"
                value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm outline-none focus:border-black"
              />
              <input
                type="text" required placeholder="Instagram handle"
                value={form.instagram} onChange={e => setForm({ ...form, instagram: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm outline-none focus:border-black"
              />
              <input
                type="email" required placeholder="Email"
                value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm outline-none focus:border-black"
              />
              <button type="submit" className="bg-black text-white px-8 py-3 rounded-lg font-medium hover:bg-gray-800 text-sm">
                Request a demo
              </button>
            </form>
          </FadeIn>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ ...sans, background: '#000' }} className="text-white py-8 text-center text-sm">
        PTBot © 2026
      </footer>
    </div>
  )
}
