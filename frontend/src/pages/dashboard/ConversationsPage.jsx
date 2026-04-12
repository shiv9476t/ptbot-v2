import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { apiFetch } from '../../lib/api'

export default function ConversationsPage() {
  const { getToken } = useAuth()
  const [contacts, setContacts] = useState([])
  const [selectedContact, setSelectedContact] = useState(null)
  const [messages, setMessages] = useState([])

  useEffect(() => {
    async function fetchContacts() {
      const token = await getToken()
      const data = await apiFetch('/api/dashboard/contacts', token)
      setContacts(data)
    }
    fetchContacts()
  }, [])

  useEffect(() => {
    if (!selectedContact) return
    async function fetchMessages() {
      const token = await getToken()
      const data = await apiFetch(`/api/dashboard/contacts/${selectedContact.id}/messages`, token)
      setMessages(data)
    }
    fetchMessages()
  }, [selectedContact])

  return (
    <div className="flex h-full gap-4">
      
      {/* Contact list */}
      <div className="w-64 flex-shrink-0">
        <h2 className="text-lg font-bold mb-4">Leads</h2>
        {contacts.length === 0 && (
          <p className="text-gray-400 text-sm">No leads yet.</p>
        )}
        {contacts.map(contact => (
          <div
            key={contact.id}
            onClick={() => setSelectedContact(contact)}
            className={`p-3 rounded-lg mb-2 cursor-pointer text-sm ${
              selectedContact?.id === contact.id
                ? 'bg-blue-600'
                : 'bg-gray-900 hover:bg-gray-800'
            }`}
          >
            <div className="font-medium">{contact.sender_id}</div>
            <div className="text-xs text-gray-400 mt-1">{contact.status}</div>
          </div>
        ))}
      </div>

      {/* Message history */}
      <div className="flex-1">
        {!selectedContact && (
          <p className="text-gray-400 text-sm">Select a lead to view the conversation.</p>
        )}
        {selectedContact && (
          <>
            <h2 className="text-lg font-bold mb-4">{selectedContact.sender_id}</h2>
            <div className="flex flex-col gap-3">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`max-w-lg p-3 rounded-lg text-sm ${
                    message.role === 'user'
                      ? 'bg-gray-900 self-start'
                      : 'bg-blue-600 self-end'
                  }`}
                >
                  <div className="text-xs text-gray-400 mb-1">{message.role}</div>
                  {message.content}
                </div>
              ))}
            </div>
          </>
        )}
      </div>

    </div>
  )
}