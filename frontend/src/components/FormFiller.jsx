import { useState } from 'react'
import { FileText, Sparkles, Download, CheckCircle } from 'lucide-react'

export default function FormFiller() {
  const [selectedForm, setSelectedForm] = useState('')
  const [filling, setFilling] = useState(false)
  const [filled, setFilled] = useState(false)

  const forms = [
    { id: 'motion-summary', name: 'Motion for Summary Judgment', category: 'Motions' },
    { id: 'complaint', name: 'Complaint for Fraud', category: 'Pleadings' },
    { id: 'affidavit', name: 'Affidavit of Financial Expert', category: 'Evidence' },
    { id: 'discovery', name: 'Interrogatories - Financial', category: 'Discovery' },
    { id: 'subpoena', name: 'Subpoena for Bank Records', category: 'Discovery' }
  ]

  const handleFill = async () => {
    setFilling(true)
    // Simulate AI form filling
    await new Promise(resolve => setTimeout(resolve, 2500))
    setFilling(false)
    setFilled(true)
  }

  const formFields = selectedForm ? [
    { label: 'Case Number', value: '2024-L-001234', aiGenerated: false },
    { label: 'Plaintiff', value: 'John Smith', aiGenerated: false },
    { label: 'Defendant', value: 'ABC Corporation', aiGenerated: false },
    { label: 'Total Amount in Controversy', value: '$250,000', aiGenerated: true },
    { label: 'Key Transactions', value: 'Wire transfers totaling $175,000 between January and March 2024...', aiGenerated: true },
    { label: 'Expert Analysis Summary', value: 'Forensic analysis reveals pattern of suspicious fund movements...', aiGenerated: true }
  ] : []

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Form Filler</h2>
        <p className="text-slate-400">AI-powered court form completion using analyzed data</p>
      </div>

      {/* Form Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Select Court Form
        </label>
        <div className="flex gap-3">
          <select
            value={selectedForm}
            onChange={(e) => {
              setSelectedForm(e.target.value)
              setFilled(false)
            }}
            className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/50 text-white"
          >
            <option value="">Choose a form...</option>
            {forms.map((form) => (
              <option key={form.id} value={form.id}>
                {form.category} - {form.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleFill}
            disabled={!selectedForm || filling || filled}
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            {filling ? 'Filling...' : filled ? 'Filled' : 'Auto-Fill'}
          </button>
        </div>
      </div>

      {/* Form Preview */}
      {selectedForm && (
        <div className="flex-1 overflow-y-auto">
          <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-emerald-400" />
                <h3 className="text-xl font-semibold text-white">
                  {forms.find(f => f.id === selectedForm)?.name}
                </h3>
              </div>
              {filled && (
                <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg font-medium transition-colors flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Download PDF
                </button>
              )}
            </div>

            <div className="space-y-4">
              {formFields.map((field, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    field.aiGenerated && filled
                      ? 'bg-emerald-500/5 border-emerald-500/20'
                      : 'bg-slate-800/50 border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      {field.label}
                    </label>
                    {field.aiGenerated && filled && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 rounded text-xs text-emerald-400">
                        <Sparkles className="w-3 h-3" />
                        AI Generated
                      </span>
                    )}
                  </div>
                  <div className="text-white">
                    {filled ? (
                      <p className={field.value.length > 100 ? 'text-sm' : ''}>
                        {field.value}
                      </p>
                    ) : (
                      <div className="h-6 bg-slate-700/30 rounded animate-pulse"></div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {filled && (
              <div className="mt-6 bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-emerald-400 mb-1">Form Completed</p>
                    <p className="text-xs text-slate-400">
                      All fields have been automatically filled using data from your analyzed documents.
                      Please review for accuracy before filing.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!selectedForm && (
        <div className="flex-1 flex items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800">
          <div className="text-center">
            <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Select a form to get started</p>
          </div>
        </div>
      )}
    </div>
  )
}
