import { useState } from 'react'
import { Database, Search, FileText, Image, Mail, DollarSign, Filter } from 'lucide-react'

export default function EvidenceBrowser() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')

  const evidence = [
    {
      id: 1,
      type: 'document',
      title: 'Bank Statement - January 2024',
      description: 'Chase Bank Account *****1234',
      date: '2024-01-31',
      size: '2.4 MB',
      pages: 12,
      tags: ['financial', 'bank'],
      relevance: 'high'
    },
    {
      id: 2,
      type: 'email',
      title: 'RE: Property Transaction',
      description: 'Email chain discussing real estate purchase',
      date: '2024-02-15',
      size: '156 KB',
      pages: 4,
      tags: ['communication', 'real-estate'],
      relevance: 'medium'
    },
    {
      id: 3,
      type: 'transaction',
      title: 'Wire Transfer Receipt',
      description: 'Transfer of $50,000 to offshore account',
      date: '2024-03-01',
      size: '89 KB',
      pages: 1,
      tags: ['financial', 'flagged'],
      relevance: 'critical'
    },
    {
      id: 4,
      type: 'document',
      title: 'Purchase Agreement',
      description: 'Real estate purchase contract',
      date: '2024-02-20',
      size: '1.8 MB',
      pages: 24,
      tags: ['legal', 'real-estate'],
      relevance: 'high'
    },
    {
      id: 5,
      type: 'image',
      title: 'Property Photos',
      description: 'Images of purchased property',
      date: '2024-02-18',
      size: '5.2 MB',
      pages: 8,
      tags: ['evidence', 'real-estate'],
      relevance: 'low'
    }
  ]

  const getIcon = (type) => {
    switch (type) {
      case 'email': return Mail
      case 'transaction': return DollarSign
      case 'image': return Image
      default: return FileText
    }
  }

  const getRelevanceColor = (relevance) => {
    switch (relevance) {
      case 'critical': return 'bg-red-500/10 text-red-400 border-red-500/20'
      case 'high': return 'bg-orange-500/10 text-orange-400 border-orange-500/20'
      case 'medium': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
      default: return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    }
  }

  const filteredEvidence = evidence.filter(item => {
    const matchesSearch = searchTerm === '' ||
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === 'all' || item.type === selectedType
    return matchesSearch && matchesType
  })

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Evidence Browser</h2>
        <p className="text-slate-400">Search and manage all analyzed documents and evidence</p>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search evidence by title, description, or tags..."
            className="w-full pl-11 pr-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white placeholder:text-slate-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-slate-400" />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white"
          >
            <option value="all">All Types</option>
            <option value="document">Documents</option>
            <option value="email">Emails</option>
            <option value="transaction">Transactions</option>
            <option value="image">Images</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Total Items</p>
          <p className="text-2xl font-bold text-white">{evidence.length}</p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Documents</p>
          <p className="text-2xl font-bold text-white">
            {evidence.filter(e => e.type === 'document').length}
          </p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Emails</p>
          <p className="text-2xl font-bold text-white">
            {evidence.filter(e => e.type === 'email').length}
          </p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
          <p className="text-sm text-slate-400 mb-1">Critical</p>
          <p className="text-2xl font-bold text-red-400">
            {evidence.filter(e => e.relevance === 'critical').length}
          </p>
        </div>
      </div>

      {/* Evidence List */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        <div className="space-y-3">
          {filteredEvidence.map((item) => {
            const Icon = getIcon(item.type)
            return (
              <div
                key={item.id}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-slate-700/30 rounded-lg">
                    <Icon className="w-6 h-6 text-slate-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        {item.title}
                      </h3>
                      <span className={`px-2 py-1 border rounded-full text-xs font-medium ${getRelevanceColor(item.relevance)}`}>
                        {item.relevance}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mb-3">{item.description}</p>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span>{item.date}</span>
                      <span>•</span>
                      <span>{item.pages} page{item.pages !== 1 ? 's' : ''}</span>
                      <span>•</span>
                      <span>{item.size}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-3">
                      {item.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-slate-700/50 rounded text-xs text-slate-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}

          {filteredEvidence.length === 0 && (
            <div className="text-center py-12">
              <Database className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No evidence found matching your criteria</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
