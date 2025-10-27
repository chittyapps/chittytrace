import { useState, useCallback } from 'react'
import { Upload, FileText, CheckCircle, XCircle, Loader2, Folder } from 'lucide-react'

export default function DocumentScanner() {
  const [files, setFiles] = useState([])
  const [scanning, setScanning] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }, [])

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }

  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      file: file
    }))
    setFiles(prev => [...prev, ...newFiles])
  }

  const scanDocuments = async () => {
    setScanning(true)

    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'pending') continue

      setFiles(prev => prev.map((f, idx) =>
        idx === i ? { ...f, status: 'scanning' } : f
      ))

      // Simulate scanning
      await new Promise(resolve => setTimeout(resolve, 1500))

      try {
        const formData = new FormData()
        formData.append('file', files[i].file)

        const response = await fetch('/api/scan', {
          method: 'POST',
          body: formData
        })

        if (response.ok) {
          setFiles(prev => prev.map((f, idx) =>
            idx === i ? { ...f, status: 'success' } : f
          ))
        } else {
          throw new Error('Scan failed')
        }
      } catch (error) {
        setFiles(prev => prev.map((f, idx) =>
          idx === i ? { ...f, status: 'error' } : f
        ))
      }
    }

    setScanning(false)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Document Scanner</h2>
        <p className="text-slate-400">Upload documents for AI-powered analysis</p>
      </div>

      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragActive
            ? 'border-emerald-500 bg-emerald-500/5'
            : 'border-slate-700 bg-slate-900/50'
        }`}
      >
        <input
          type="file"
          id="file-upload"
          multiple
          onChange={handleChange}
          className="hidden"
          accept=".pdf,.xlsx,.xls,.csv,.txt,.doc,.docx"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-16 h-16 text-slate-500 mx-auto mb-4" />
          <p className="text-xl font-semibold text-white mb-2">
            Drop files here or click to upload
          </p>
          <p className="text-sm text-slate-400">
            Supports PDF, Excel, CSV, Word, and text files
          </p>
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 flex-1 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              Uploaded Files ({files.length})
            </h3>
            <button
              onClick={scanDocuments}
              disabled={scanning || files.every(f => f.status !== 'pending')}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              {scanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Folder className="w-4 h-4" />
                  Scan All
                </>
              )}
            </button>
          </div>

          <div className="space-y-2">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center gap-4 p-4 bg-slate-900 border border-slate-800 rounded-lg"
              >
                <FileText className="w-8 h-8 text-slate-400" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">{file.name}</p>
                  <p className="text-sm text-slate-400">{formatFileSize(file.size)}</p>
                </div>
                <div className="flex items-center gap-2">
                  {file.status === 'pending' && (
                    <span className="text-sm text-slate-400">Pending</span>
                  )}
                  {file.status === 'scanning' && (
                    <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
                  )}
                  {file.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  )}
                  {file.status === 'error' && (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
