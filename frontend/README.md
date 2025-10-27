# ChittyTrace - AI-Powered Financial Forensics Platform

Modern React frontend for ChittyTrace, built with Vite, React 19, and Tailwind CSS v4.

## Features

### Core Financial Forensics
- 🔍 **Query Interface** - AI-powered document analysis and questioning
- 📄 **Document Scanner** - Upload and process financial documents
- 💰 **Fund Flow Tracer** - Visualize money movement and flag suspicious activity
- ⏱️ **Timeline Viewer** - Chronological view of financial events
- ⚖️ **Exhibit Generator** - Cook County court-ready exhibit packages
- 📝 **Form Filler** - AI-powered court form completion
- 🗂️ **Evidence Browser** - Search and manage all evidence

### Case & Collaboration Management
- 💼 **Case Manager** - Full case lifecycle management via cases.chitty.cc
- 💬 **Team Chat** - Real-time collaboration via ChittyChat with WebSocket support

## Tech Stack

- **React 19** - Latest React with concurrent features
- **Vite 7** - Lightning-fast build tool
- **Tailwind CSS v4** - Modern utility-first CSS
- **Lucide React** - Beautiful icons
- **ChittyConnect** - Custom API client for backend integration

## Getting Started

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_bearer_token_here
VITE_ENVIRONMENT=development
```

## Deployment

### Cloudflare Pages (Recommended)

This project is configured for automatic deployment via GitHub Actions:

1. Set up secrets in your GitHub repository:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `VITE_API_URL`
   - `VITE_API_TOKEN`

2. Push to `main` branch - automatic deployment via GitHub Actions

### Manual Deploy

```bash
# Build
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy dist --project-name=chittytrace
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Sidebar.jsx
│   │   ├── QueryInterface.jsx
│   │   ├── DocumentScanner.jsx
│   │   ├── FundFlowTracer.jsx
│   │   ├── TimelineViewer.jsx
│   │   ├── ExhibitGenerator.jsx
│   │   ├── FormFiller.jsx
│   │   ├── EvidenceBrowser.jsx
│   │   ├── CaseManager.jsx      # NEW: Case management
│   │   └── ChatInterface.jsx    # NEW: Team collaboration
│   ├── lib/
│   │   ├── api.js               # ChittyConnect API client
│   │   ├── registry.js          # Service registry client
│   │   ├── chittycases.js       # Case management integration
│   │   └── chittychat.js        # Real-time chat integration
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── .github/
│   └── workflows/        # CI/CD pipelines
├── dist/                 # Build output
└── package.json
```

## API Integration

The app uses multiple specialized clients for ChittyCorp services:

### ChittyConnect - Main API
```javascript
import api from './lib/api'

// Query documents
const result = await api.query('Show me all wire transfers over $10,000')

// Scan document
await api.scanDocument(file)

// Trace funds
const flows = await api.traceFunds('Account 1234')

// Generate exhibits
await api.generatePackage([1, 2, 3])
```

### ChittyCases - Case Management
```javascript
import cases from './lib/chittycases'

// Get all cases
const allCases = await cases.getCases()

// Create new case
const newCase = await cases.createCase({
  title: 'Smith v. ABC Corp',
  type: 'Financial Fraud'
})

// Add document to case
await cases.addDocument(caseId, documentData)

// Analyze funds for case
await cases.analyzeFunds(caseId)
```

### ChittyChat - Real-time Communication
```javascript
import chat from './lib/chittychat'

// Connect to chat
await chat.connect(userId)

// Listen for messages
chat.on('message', (data) => {
  console.log('New message:', data)
})

// Send message
await chat.sendMessage(roomId, 'Hello team!')

// Join a room
await chat.joinRoom(roomId)
```

## ChittyCorp Services Integration

ChittyTrace integrates with the full ChittyCorp ecosystem:

- **ChittyOS** - Operating system integration via @chittyos/core
- **ChittyConnect** - API communication layer (`src/lib/api.js`)
- **ChittyCases** - Case management system (`cases.chitty.cc`)
- **ChittyChat** - Real-time communication (`chat.chitty.cc`)
- **ChittyAuth** - Authentication and authorization (`auth.chitty.cc`)
- **Service Registry** - Dynamic service discovery (`registry.chitty.cc`)
- **Cloudflare Workers** - Email ingestion (nick@chitty.cc)
- **Neon PostgreSQL** - Vector database with semantic search

### Service Architecture

All services support both direct URL configuration and automatic discovery via `registry.chitty.cc`:

```javascript
// Direct configuration
VITE_CASES_URL=https://cases.chitty.cc

// Or use service registry
VITE_USE_REGISTRY=true
VITE_REGISTRY_URL=https://registry.chitty.cc
```

The system automatically falls back to direct URLs when the registry is unavailable.

For more information on ChittyCorp services:
- **Website**: https://chittycorp.com
- **Support**: support@chittycorp.com

## Contributing

This is part of the ChittyCorp ecosystem. For issues and feature requests, visit:
- **GitHub**: https://github.com/ChittyApps/flow-of-funds-analyzer
- **Email**: support@chittycorp.com

## License

MIT © ChittyCorp LLC
