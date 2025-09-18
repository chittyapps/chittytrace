import React, { useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './components/dashboard/Dashboard';
import { DocumentProcessor } from './components/documents/DocumentProcessor';
import { FundFlowVisualization } from './components/analysis/FundFlowVisualization';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'documents':
        return <DocumentProcessor />;
      case 'flow':
        return <FundFlowVisualization />;
      case 'query':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              AI Query Interface
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Coming soon - AI-powered document analysis and querying
            </p>
          </div>
        );
      case 'timeline':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Timeline Visualization
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Coming soon - Interactive timeline of financial events
            </p>
          </div>
        );
      case 'exhibits':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Exhibit Package Generator
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Coming soon - Cook County court-ready exhibit packages
            </p>
          </div>
        );
      case 'database':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Database Integration
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Coming soon - Neon PostgreSQL database management
            </p>
          </div>
        );
      case 'settings':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Settings
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Coming soon - Application settings and preferences
            </p>
          </div>
        );
      case 'help':
        return (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Help & Support
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Contact support@chittycorp.com for assistance
            </p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeSection={activeSection} onSectionChange={setActiveSection}>
      {renderContent()}
    </Layout>
  );
}

export default App;