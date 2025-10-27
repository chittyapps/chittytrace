import { useState, useEffect, useRef } from 'react'
import { MessageCircle, Send, Users, Hash, Plus, Settings } from 'lucide-react'
import chat from '../lib/chittychat'

export default function ChatInterface() {
  const [rooms, setRooms] = useState([])
  const [activeRoom, setActiveRoom] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [connected, setConnected] = useState(false)
  const messagesEndRef = useRef(null)

  // Mock rooms for demo
  const mockRooms = [
    { id: 1, name: 'Case #2024-L-001234', type: 'case', unread: 3, members: 5 },
    { id: 2, name: 'Financial Analysis Team', type: 'team', unread: 0, members: 8 },
    { id: 3, name: 'Document Review', type: 'team', unread: 1, members: 4 },
    { id: 4, name: 'General', type: 'general', unread: 0, members: 12 }
  ]

  // Mock messages
  const mockMessages = [
    {
      id: 1,
      roomId: 1,
      userId: 'user-2',
      userName: 'Sarah Johnson',
      content: 'I reviewed the bank statements from January. Found some discrepancies.',
      timestamp: '2024-10-27T14:30:00Z',
      type: 'message'
    },
    {
      id: 2,
      roomId: 1,
      userId: 'user-1',
      userName: 'You',
      content: 'Can you share which accounts specifically?',
      timestamp: '2024-10-27T14:32:00Z',
      type: 'message'
    },
    {
      id: 3,
      roomId: 1,
      userId: 'user-2',
      userName: 'Sarah Johnson',
      content: 'Account ending in 1234. Multiple large cash deposits with no clear source.',
      timestamp: '2024-10-27T14:35:00Z',
      type: 'message'
    },
    {
      id: 4,
      roomId: 1,
      userId: 'user-3',
      userName: 'Mike Chen',
      content: 'I can run that through our fraud detection analysis.',
      timestamp: '2024-10-27T14:38:00Z',
      type: 'message'
    }
  ]

  useEffect(() => {
    loadRooms()
    // connectToChat()

    return () => {
      chat.disconnect()
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadRooms = async () => {
    try {
      // const data = await chat.getRooms()
      // setRooms(data)
      setRooms(mockRooms)
      if (mockRooms.length > 0) {
        setActiveRoom(mockRooms[0])
        setMessages(mockMessages.filter(m => m.roomId === mockRooms[0].id))
      }
    } catch (error) {
      console.error('Failed to load rooms:', error)
      setRooms(mockRooms)
    }
  }

  const connectToChat = async () => {
    try {
      await chat.connect('current-user-id')
      setConnected(true)

      chat.on('message', (data) => {
        setMessages(prev => [...prev, data])
      })

      chat.on('disconnected', () => {
        setConnected(false)
      })
    } catch (error) {
      console.error('Failed to connect to chat:', error)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !activeRoom) return

    const message = {
      id: Date.now(),
      roomId: activeRoom.id,
      userId: 'user-1',
      userName: 'You',
      content: newMessage,
      timestamp: new Date().toISOString(),
      type: 'message'
    }

    setMessages(prev => [...prev, message])
    setNewMessage('')

    try {
      // await chat.sendMessage(activeRoom.id, newMessage)
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Team Chat</h2>
        <p className="text-slate-400">Real-time collaboration via ChittyChat</p>
      </div>

      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* Rooms Sidebar */}
        <div className="w-64 bg-slate-900/50 rounded-xl border border-slate-800 p-4 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Rooms</h3>
            <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
              <Plus className="w-4 h-4 text-slate-400" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2">
            {rooms.map((room) => (
              <button
                key={room.id}
                onClick={() => {
                  setActiveRoom(room)
                  setMessages(mockMessages.filter(m => m.roomId === room.id))
                }}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeRoom?.id === room.id
                    ? 'bg-emerald-500/10 border border-emerald-500/20'
                    : 'bg-slate-800/50 border border-transparent hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Hash className="w-4 h-4 text-slate-400" />
                  <span className="font-medium text-white truncate">{room.name}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">{room.members} members</span>
                  {room.unread > 0 && (
                    <span className="px-2 py-0.5 bg-emerald-500 text-white rounded-full">
                      {room.unread}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex items-center gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-slate-500'}`}></div>
              <span className="text-slate-400">{connected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 bg-slate-900/50 rounded-xl border border-slate-800 flex flex-col">
          {activeRoom ? (
            <>
              {/* Room Header */}
              <div className="p-4 border-b border-slate-800">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <Hash className="w-5 h-5 text-slate-400" />
                      {activeRoom.name}
                    </h3>
                    <p className="text-sm text-slate-400">{activeRoom.members} members</p>
                  </div>
                  <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                    <Settings className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.userName === 'You' ? 'justify-end' : ''}`}
                  >
                    {message.userName !== 'You' && (
                      <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-sm font-medium text-white">
                          {message.userName.charAt(0)}
                        </span>
                      </div>
                    )}
                    <div className={`flex-1 max-w-[70%] ${message.userName === 'You' ? 'text-right' : ''}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-white">{message.userName}</span>
                        <span className="text-xs text-slate-500">{formatTime(message.timestamp)}</span>
                      </div>
                      <div className={`inline-block p-3 rounded-lg ${
                        message.userName === 'You'
                          ? 'bg-emerald-500/10 border border-emerald-500/20'
                          : 'bg-slate-800 border border-slate-700'
                      }`}>
                        <p className="text-sm text-slate-200">{message.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-800">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder={`Message #${activeRoom.name}`}
                    className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white placeholder:text-slate-500"
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors flex items-center gap-2"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <MessageCircle className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a room to start chatting</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
