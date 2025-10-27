import { useState, useEffect } from 'react'
import { Briefcase, Plus, Search, Calendar, Users, DollarSign, FileText } from 'lucide-react'
import cases from '../lib/chittycases'

export default function CaseManager() {
  const [caseList, setCaseList] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCase, setSelectedCase] = useState(null)

  // Mock cases for demo
  const mockCases = [
    {
      id: 1,
      caseNumber: '2024-L-001234',
      title: 'Smith v. ABC Corporation',
      type: 'Financial Fraud',
      status: 'active',
      plaintiff: 'John Smith',
      defendant: 'ABC Corporation',
      filingDate: '2024-01-15',
      amountInDispute: 250000,
      documentCount: 156,
      eventCount: 24,
      partyCount: 8
    },
    {
      id: 2,
      caseNumber: '2024-L-002456',
      title: 'Johnson Estate Investigation',
      type: 'Estate Fraud',
      status: 'investigation',
      plaintiff: 'Johnson Family Trust',
      defendant: 'Multiple Parties',
      filingDate: '2024-02-20',
      amountInDispute: 500000,
      documentCount: 89,
      eventCount: 18,
      partyCount: 5
    },
    {
      id: 3,
      caseNumber: '2024-L-003789',
      title: 'XYZ Holdings Embezzlement',
      type: 'Embezzlement',
      status: 'pending',
      plaintiff: 'XYZ Holdings LLC',
      defendant: 'Former CFO',
      filingDate: '2024-03-10',
      amountInDispute: 175000,
      documentCount: 234,
      eventCount: 31,
      partyCount: 12
    }
  ]

  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    setLoading(true)
    try {
      // const data = await cases.getCases()
      // setCaseList(data)
      setCaseList(mockCases)
    } catch (error) {
      console.error('Failed to load cases:', error)
      setCaseList(mockCases) // Fallback to mock data
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      case 'investigation': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
      case 'pending': return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      case 'closed': return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
      default: return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const filteredCases = caseList.filter(c =>
    searchTerm === '' ||
    c.caseNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.type.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Case Manager</h2>
        <p className="text-slate-400">Manage and track all legal cases via cases.chitty.cc</p>
      </div>

      {/* Search and Actions */}
      <div className="flex gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search cases by number, title, or type..."
            className="w-full pl-11 pr-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white placeholder:text-slate-500"
          />
        </div>
        <button className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 rounded-lg font-medium transition-colors flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Case
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Total Cases</p>
          <p className="text-2xl font-bold text-white">{caseList.length}</p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Active</p>
          <p className="text-2xl font-bold text-emerald-400">
            {caseList.filter(c => c.status === 'active').length}
          </p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Investigation</p>
          <p className="text-2xl font-bold text-yellow-400">
            {caseList.filter(c => c.status === 'investigation').length}
          </p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Total Amount</p>
          <p className="text-2xl font-bold text-white">
            {formatCurrency(caseList.reduce((sum, c) => sum + c.amountInDispute, 0))}
          </p>
        </div>
      </div>

      {/* Cases List */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        <div className="space-y-4">
          {filteredCases.map((caseItem) => (
            <div
              key={caseItem.id}
              onClick={() => setSelectedCase(caseItem)}
              className="bg-slate-800/50 border border-slate-700 rounded-lg p-5 hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-emerald-500/10 rounded-lg">
                    <Briefcase className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        {caseItem.title}
                      </h3>
                      <span className={`px-3 py-1 border rounded-full text-xs font-medium ${getStatusColor(caseItem.status)}`}>
                        {caseItem.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mb-1">
                      Case #{caseItem.caseNumber} • {caseItem.type}
                    </p>
                    <p className="text-sm text-slate-500">
                      {caseItem.plaintiff} v. {caseItem.defendant}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-white mb-1">
                    {formatCurrency(caseItem.amountInDispute)}
                  </p>
                  <p className="text-xs text-slate-500">Amount in Dispute</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 pt-4 border-t border-slate-700">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  <div>
                    <p className="text-xs text-slate-500">Filed</p>
                    <p className="text-sm text-slate-300">{caseItem.filingDate}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-slate-500" />
                  <div>
                    <p className="text-xs text-slate-500">Documents</p>
                    <p className="text-sm text-slate-300">{caseItem.documentCount}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  <div>
                    <p className="text-xs text-slate-500">Events</p>
                    <p className="text-sm text-slate-300">{caseItem.eventCount}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-slate-500" />
                  <div>
                    <p className="text-xs text-slate-500">Parties</p>
                    <p className="text-sm text-slate-300">{caseItem.partyCount}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {filteredCases.length === 0 && (
            <div className="text-center py-12">
              <Briefcase className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No cases found matching your search</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
