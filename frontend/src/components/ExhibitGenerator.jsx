import { useState } from 'react'
import { Scale, Plus, Download, FileText, CheckSquare } from 'lucide-react'

export default function ExhibitGenerator() {
  const [exhibits, setExhibits] = useState([
    {
      id: 1,
      number: 'A',
      title: 'Bank Statements - Chase Account *1234',
      pageCount: 24,
      dateRange: 'Jan 2024 - Mar 2024',
      status: 'ready',
      authenticated: true
    },
    {
      id: 2,
      number: 'B',
      title: 'Wire Transfer Documentation',
      pageCount: 8,
      dateRange: 'Feb 2024',
      status: 'ready',
      authenticated: true
    },
    {
      id: 3,
      number: 'C',
      title: 'Email Correspondence',
      pageCount: 15,
      dateRange: 'Jan 2024 - Mar 2024',
      status: 'pending',
      authenticated: false
    }
  ])

  const [generating, setGenerating] = useState(false)

  const generatePackage = async () => {
    setGenerating(true)
    // Simulate package generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    setGenerating(false)
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Exhibit Generator</h2>
        <p className="text-slate-400">Create court-ready exhibit packages per Cook County requirements</p>
      </div>

      {/* Package Info */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-5">
          <p className="text-sm text-slate-400 mb-1">Total Exhibits</p>
          <p className="text-3xl font-bold text-white">{exhibits.length}</p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-5">
          <p className="text-sm text-slate-400 mb-1">Total Pages</p>
          <p className="text-3xl font-bold text-white">
            {exhibits.reduce((sum, e) => sum + e.pageCount, 0)}
          </p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-5">
          <p className="text-sm text-slate-400 mb-1">Ready to File</p>
          <p className="text-3xl font-bold text-emerald-400">
            {exhibits.filter(e => e.status === 'ready').length}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        <button className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-lg font-medium transition-colors flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Exhibit
        </button>
        <button
          onClick={generatePackage}
          disabled={generating || exhibits.filter(e => e.status === 'ready').length === 0}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:text-slate-600 border border-slate-700 rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          {generating ? 'Generating...' : 'Generate Package'}
        </button>
      </div>

      {/* Exhibits List */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-xl p-6 border border-slate-800">
        <div className="space-y-4">
          {exhibits.map((exhibit) => (
            <div
              key={exhibit.id}
              className="bg-slate-800/50 border border-slate-700 rounded-lg p-5"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="p-3 bg-emerald-500/10 rounded-lg">
                    <FileText className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-3 py-1 bg-slate-700 rounded text-sm font-bold text-white">
                        Exhibit {exhibit.number}
                      </span>
                      {exhibit.authenticated && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded text-xs text-emerald-400">
                          <CheckSquare className="w-3 h-3" />
                          Authenticated
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {exhibit.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-slate-400">
                      <span>{exhibit.pageCount} pages</span>
                      <span>•</span>
                      <span>{exhibit.dateRange}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    exhibit.status === 'ready'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                  }`}>
                    {exhibit.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Court Requirements Note */}
      <div className="mt-6 bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Scale className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-400 mb-1">Cook County Requirements</p>
            <p className="text-xs text-slate-400">
              All exhibits automatically formatted with 1" margins, Times New Roman 12pt, double spacing,
              exhibit stickers, and authentication affidavits.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
