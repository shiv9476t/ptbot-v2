import { useEffect, useRef, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch } from '../../lib/api'

const API_URL = import.meta.env.VITE_API_URL
const sans = { fontFamily: 'system-ui, sans-serif' }

function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function randomSenderId() {
  return 'demo_' + Math.random().toString(36).slice(2, 10)
}

export default function DemoPage() {
  const { getToken } = useAuth()
  const [settings, setSettings] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const [senderId, setSenderId] = useState(() => randomSenderId())
  const messagesEndRef = useRef(null)

  useEffect(() => {
    async function fetchSettings() {
      const token = await getToken()
      const data = await apiFetch('/api/dashboard/settings', token)
      setSettings(data)
    }
    fetchSettings()
  }, [])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, typing])

  async function sendMessage() {
    const text = input.trim()
    if (!text || typing) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setTyping(true)
    try {
      const resp = await fetch(`${API_URL}/demo/${settings.slug}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender_id: senderId, message: text }),
      })
      const data = await resp.json()
      setMessages(prev => [...prev, { role: 'bot', text: data.reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: 'Something went wrong. Please try again.' }])
    } finally {
      setTyping(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function resetConversation() {
    setMessages([])
    setSenderId(randomSenderId())
  }

  if (!settings) return <p className="text-gray-500">Loading...</p>

  const initials = getInitials(settings.name)

  return (
    <div>
      <style>{`
        @keyframes typingBounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-2">Test your bot</h1>
          <p className="text-gray-500">This is exactly how your bot will respond to leads on Instagram.</p>
        </div>
        <button
          onClick={resetConversation}
          className="text-sm text-gray-500 hover:text-black border border-gray-200 rounded-lg px-4 py-2"
        >
          Reset conversation
        </button>
      </div>

      <div className="flex justify-center">
        <div style={{
          width: '390px', height: '700px', background: '#000',
          borderRadius: '48px',
          boxShadow: '0 40px 80px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.08)',
          display: 'flex', flexDirection: 'column', overflow: 'hidden', position: 'relative',
        }}>
          {/* Notch */}
          <div style={{
            position: 'absolute', top: '12px', left: '50%', transform: 'translateX(-50%)',
            width: '80px', height: '22px', background: '#000',
            borderRadius: '12px', zIndex: 10,
            boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.1)',
          }} />

          {/* Status bar spacing */}
          <div style={{ height: '44px', flexShrink: 0 }} />

          {/* IG DM header */}
          <div style={{ borderBottom: '1px solid #1a1a1a', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
            <div style={{ ...sans, width: '34px', height: '34px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '12px', fontWeight: 700, flexShrink: 0 }}>{initials}</div>
            <div>
              <p style={{ ...sans, color: '#fff', fontSize: '13px', fontWeight: 600, margin: 0 }}>{settings.name}</p>
              <p style={{ ...sans, color: '#666', fontSize: '11px', margin: 0 }}>Active now</p>
            </div>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                {msg.role === 'bot' && (
                  <div style={{ ...sans, width: '22px', height: '22px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '9px', fontWeight: 700, flexShrink: 0 }}>{initials}</div>
                )}
                <div style={{
                  ...sans, maxWidth: '75%', padding: '8px 12px', fontSize: '12px', lineHeight: '1.5', color: '#fff',
                  background: msg.role === 'user' ? '#0095f6' : '#262626',
                  borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                }}>
                  {msg.text}
                </div>
              </div>
            ))}

            {typing && (
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px' }}>
                <div style={{ ...sans, width: '22px', height: '22px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '9px', fontWeight: 700, flexShrink: 0 }}>{initials}</div>
                <div style={{ background: '#262626', borderRadius: '18px 18px 18px 4px', padding: '10px 14px', display: 'flex', gap: '4px', alignItems: 'center' }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#888', animation: 'typingBounce 1.2s infinite', animationDelay: `${i * 0.2}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{ borderTop: '1px solid #1a1a1a', padding: '12px', display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message..."
              style={{ ...sans, flex: 1, background: '#1a1a1a', border: 'none', borderRadius: '20px', padding: '8px 14px', color: '#fff', fontSize: '13px', outline: 'none' }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || typing}
              style={{ ...sans, background: '#0095f6', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', flexShrink: 0, opacity: (!input.trim() || typing) ? 0.4 : 1 }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M22 2L11 13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
