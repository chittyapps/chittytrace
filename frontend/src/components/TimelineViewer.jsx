import { useState } from 'react'
import { Calendar, Clock, Filter, Download } from 'lucide-react'

export default function TimelineViewer() {
  const [filter, setFilter] = useState('all')

  // Mock timeline events
  const events = [
    {
      id: 1,
      date: '2024-01-15',
      time: '09:30 AM',
      type: 'transaction',
      title: 'Wire transfer initiated',
      description: 'Transfer of $50,000 from Account ending in 1234',
      source: 'Bank Statement - Page 3',
      severity: 'normal'
    },
    {
      id: 2,
      date: '2024-01-18',
      time: '02:15 PM',
      type: 'communication',
      title: 'Email correspondence',
      description: 'Discussion regarding property purchase agreement',
      source: 'Email Thread - RE: Property Deal',
      severity: 'normal'
    },
    {
      id: 3,
      date: '2024-02-01',
      time: '11:00 AM',
      type: 'transaction',
      title: 'Large cash deposit',
      description: 'Cash deposit of $75,000 - no clear source documentation',
      source: 'Bank Statement - Page 12',
      severity: 'flagged'
    },
    {
      id: 4,
      date: '2024-02-15',
      time: '04:45 PM',
      type: 'document',
      title: 'Contract signed',
      description: 'Real estate purchase agreement executed',
      source: 'Purchase Agreement.pdf',
      severity: 'normal'
    },
    {
      id: 5,
      date: '2024-03-01',
      time: '10:30 AM',
      type: 'transaction',
      title: 'Offshore transfer',
      description: 'Wire to account in Cayman Islands - $30,000',
      source: 'Wire Transfer Receipt',
      severity: 'critical'
    }
  ]

  const filteredEvents = filter === 'all'
    ? events
    : events.filter(e => e.type === filter)

  const getEventColor = (severity) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-500/5'
      case 'flagged': return 'border-yellow-500 bg-yellow-500/5'
      default: return 'border-emerald-500 bg-emerald-500/5'
    }
  }

  const getEventIcon = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400'
      case 'flagged': return 'bg-yellow-500/20 text-yellow-400'
      default: return 'bg-emerald-500/20 text-emerald-400'
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Timeline Viewer</h2>
        <p className="text-slate-400">Chronological view of financial events and activities</p>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-slate-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white"
          >
            <option value="all">All Events</option>
            <option value="transaction">Transactions</option>
            <option value="communication">Communications</option>
            <option value="document">Documents</option>
          </select>
        </div>

        <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg font-medium transition-colors flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export Timeline
        </button>
      </div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-700"></div>

          <div className="space-y-8">
            {filteredEvents.map((event) => (
              <div key={event.id} className="relative pl-20">
                {/* Timeline dot */}
                <div className={`absolute left-5 w-6 h-6 rounded-full border-2 ${getEventColor(event.severity)} flex items-center justify-center`}>
                  <div className={`w-3 h-3 rounded-full ${getEventIcon(event.severity)}`}></div>
                </div>

                {/* Event card */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {event.title}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {event.date}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {event.time}
                        </span>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-slate-700 rounded-full text-xs font-medium text-slate-300 capitalize">
                      {event.type}
                    </span>
                  </div>

                  <p className="text-slate-300 mb-3">{event.description}</p>

                  <div className="pt-3 border-t border-slate-700">
                    <p className="text-xs text-slate-500">
                      Source: <span className="text-emerald-400">{event.source}</span>
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
