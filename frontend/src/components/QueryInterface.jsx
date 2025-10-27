import { useState } from 'react'
import { Send, Loader2, FileText, AlertCircle } from 'lucide-react'

export default function QueryInterface() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setLoading(true)

    try {
      // TODO: Connect to backend API
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Connection error. Make sure the backend API is running.'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Query Interface</h2>
        <p className="text-slate-400">Ask questions about your financial documents</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-6 bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No messages yet. Start by asking a question.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-emerald-500/10 border border-emerald-500/20'
                    : msg.role === 'error'
                    ? 'bg-red-500/10 border border-red-500/20 flex items-start gap-2'
                    : 'bg-slate-800/50 border border-slate-700'
                }`}
              >
                {msg.role === 'error' && <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />}
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about transactions, patterns, or generate analysis..."
          className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white placeholder:text-slate-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <Send className="w-5 h-5" />
          Send
        </button>
      </form>
    </div>
  )
}
