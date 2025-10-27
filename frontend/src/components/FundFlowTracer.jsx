import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, ArrowRight, DollarSign } from 'lucide-react'

export default function FundFlowTracer() {
  const [searchTerm, setSearchTerm] = useState('')
  const [flows, setFlows] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchTerm.trim()) return

    setLoading(true)
    try {
      const response = await fetch('/api/trace-funds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchTerm })
      })

      const data = await response.json()
      setFlows(data.flows || [])
    } catch (error) {
      console.error('Error tracing funds:', error)
    } finally {
      setLoading(false)
    }
  }

  // Mock data for demo
  const mockFlows = [
    {
      id: 1,
      from: 'Account *****1234',
      to: 'Account *****5678',
      amount: 50000,
      date: '2024-03-15',
      type: 'wire',
      status: 'completed',
      description: 'Real estate purchase deposit'
    },
    {
      id: 2,
      from: 'Account *****5678',
      to: 'Account *****9012',
      amount: 25000,
      date: '2024-03-20',
      type: 'transfer',
      status: 'completed',
      description: 'Partial distribution'
    },
    {
      id: 3,
      from: 'Account *****9012',
      to: 'External Entity',
      amount: 15000,
      date: '2024-03-25',
      type: 'wire',
      status: 'flagged',
      description: 'Suspicious transfer - offshore account'
    }
  ]

  const displayFlows = flows.length > 0 ? flows : mockFlows

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Fund Flow Tracer</h2>
        <p className="text-slate-400">Trace money movement across accounts and entities</p>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter account number, entity name, or transaction ID..."
              className="w-full pl-11 pr-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white placeholder:text-slate-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors"
          >
            {loading ? 'Tracing...' : 'Trace'}
          </button>
        </div>
      </form>

      {/* Flow Visualization */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        <div className="space-y-6">
          {displayFlows.map((flow, idx) => (
            <div key={flow.id} className="relative">
              {/* Flow Card */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-500/10 rounded-lg">
                      <DollarSign className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">
                        {formatCurrency(flow.amount)}
                      </p>
                      <p className="text-sm text-slate-400">{flow.date}</p>
                    </div>
                  </div>
                  <div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      flow.status === 'flagged'
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      {flow.status}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-4 mb-4">
                  <div className="flex-1">
                    <p className="text-xs text-slate-500 mb-1">From</p>
                    <p className="font-medium text-white">{flow.from}</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-slate-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs text-slate-500 mb-1">To</p>
                    <p className="font-medium text-white">{flow.to}</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-700">
                  <p className="text-sm text-slate-300">{flow.description}</p>
                  <p className="text-xs text-slate-500 mt-2">Type: {flow.type}</p>
                </div>
              </div>

              {/* Connector Line */}
              {idx < displayFlows.length - 1 && (
                <div className="flex justify-center py-3">
                  <TrendingDown className="w-6 h-6 text-slate-600" />
                </div>
              )}
            </div>
          ))}
        </div>

        {displayFlows.length === 0 && !loading && (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No fund flows to display. Start by tracing an account or transaction.</p>
          </div>
        )}
      </div>
    </div>
  )
}
