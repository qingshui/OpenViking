import React, { useState, useEffect } from 'react'
import { sessionService } from '../services/sessions'

interface Session {
  session_id: string
  created_at: string
  message_count: number
}

const SessionManagement: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedSession, setSelectedSession] = useState<string | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [newMessage, setNewMessage] = useState('')

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await sessionService.list()
      setSessions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  const loadSessionMessages = async (session_id: string) => {
    try {
      const data = await sessionService.get(session_id)
      setSelectedSession(session_id)
      setMessages(data?.messages || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages')
    }
  }

  const handleAddMessage = async () => {
    if (!selectedSession || !newMessage.trim()) return
    try {
      await sessionService.addMessage(selectedSession, 'user', newMessage)
      setNewMessage('')
      loadSessionMessages(selectedSession)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add message')
    }
  }

  const handleDelete = async (session_id: string) => {
    if (!window.confirm('Delete this session?')) return
    try {
      await sessionService.delete(session_id)
      loadSessions()
      setSelectedSession(null)
      setMessages([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session')
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Session Management</h2>
        <button
          onClick={loadSessions}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <div className="p-4 border-b">
              <h3 className="font-semibold">Sessions</h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-gray-500">Loading...</div>
              ) : sessions.length === 0 ? (
                <div className="p-4 text-center text-gray-500">No sessions</div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.session_id}
                    onClick={() => loadSessionMessages(session.session_id)}
                    className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                      selectedSession === session.session_id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="text-sm font-medium">{session.session_id}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(session.created_at).toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {session.message_count} messages
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(session.session_id)
                      }}
                      className="text-xs text-red-600 hover:text-red-800 mt-2"
                    >
                      Delete
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="md:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="font-semibold mb-4">Messages</h3>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg ${
                    msg.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'
                  }`}
                >
                  <div className="text-sm font-medium text-gray-700 mb-1">
                    {msg.role}
                  </div>
                  <div className="text-gray-900">{msg.content}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddMessage()}
                placeholder="Type a message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
              />
              <button
                onClick={handleAddMessage}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SessionManagement
