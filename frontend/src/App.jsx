import { useState } from 'react'
import { FileSearch, TrendingUp, Clock, FileText, Scale, Upload, Database, Briefcase, MessageCircle } from 'lucide-react'
import Sidebar from './components/Sidebar'
import DocumentScanner from './components/DocumentScanner'
import QueryInterface from './components/QueryInterface'
import FundFlowTracer from './components/FundFlowTracer'
import TimelineViewer from './components/TimelineViewer'
import ExhibitGenerator from './components/ExhibitGenerator'
import FormFiller from './components/FormFiller'
import EvidenceBrowser from './components/EvidenceBrowser'
import CaseManager from './components/CaseManager'
import ChatInterface from './components/ChatInterface'

function App() {
  const [activeView, setActiveView] = useState('query')

  const views = {
    query: { component: QueryInterface, icon: FileSearch, label: 'Query' },
    scanner: { component: DocumentScanner, icon: Upload, label: 'Scanner' },
    flow: { component: FundFlowTracer, icon: TrendingUp, label: 'Fund Flow' },
    timeline: { component: TimelineViewer, icon: Clock, label: 'Timeline' },
    exhibits: { component: ExhibitGenerator, icon: Scale, label: 'Exhibits' },
    forms: { component: FormFiller, icon: FileText, label: 'Forms' },
    browser: { component: EvidenceBrowser, icon: Database, label: 'Browser' },
    cases: { component: CaseManager, icon: Briefcase, label: 'Cases' },
    chat: { component: ChatInterface, icon: MessageCircle, label: 'Chat' },
  }

  const ActiveComponent = views[activeView].component

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      <Sidebar
        views={views}
        activeView={activeView}
        setActiveView={setActiveView}
      />
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto p-8">
          <ActiveComponent />
        </div>
      </main>
    </div>
  )
}

export default App
