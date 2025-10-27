import { Scale } from 'lucide-react'
import clsx from 'clsx'

export default function Sidebar({ views, activeView, setActiveView }) {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      {/* Logo/Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-lg">
            <Scale className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">ChittyTrace</h1>
            <p className="text-xs text-slate-400">Financial Forensics</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {Object.entries(views).map(([key, { icon: Icon, label }]) => (
            <li key={key}>
              <button
                onClick={() => setActiveView(key)}
                className={clsx(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                  'hover:bg-slate-800/50',
                  activeView === key
                    ? 'bg-emerald-500/10 text-emerald-400 shadow-lg shadow-emerald-500/5'
                    : 'text-slate-300'
                )}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="text-xs text-slate-500 space-y-1">
          <p className="font-semibold text-slate-400">ChittyCorp LLC</p>
          <p>support@chittycorp.com</p>
        </div>
      </div>
    </aside>
  )
}
