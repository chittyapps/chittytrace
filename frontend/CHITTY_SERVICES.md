# ChittyCorp Services Integration

Complete integration of the ChittyCorp ecosystem in ChittyTrace frontend.

## Installed Packages

### Real NPM Packages
- ✅ `@chittyos/core` (v2.1.0) - Core ChittyOS functionality
- ✅ `@chittyos/chittyid-client` (v1.0.1) - ChittyID minting and validation
- ✅ `@chittyos/brand` (v1.0.0) - Official brand system
- ✅ `@chittyos/types` (v1.0.0) - Shared TypeScript types

## Integrated Services

### Core Services
| Service | URL | Client Library | Status |
|---------|-----|----------------|--------|
| **ChittyConnect** | `http://localhost:8000` | `src/lib/api.js` | ✅ Active |
| **ChittyCases** | `cases.chitty.cc` | `src/lib/chittycases.js` | ✅ Active |
| **ChittyChat** | `chat.chitty.cc` | `src/lib/chittychat.js` | ✅ Active |

### Foundation Services
| Service | URL | Client Library | Status |
|---------|-----|----------------|--------|
| **ChittyID** | `id.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittySchema** | `schema.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittyCertify** | `certify.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittyChain** | `chain.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittyTrust** | `trust.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittyVerify** | `verify.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |

### Apps Services
| Service | URL | Client Library | Status |
|---------|-----|----------------|--------|
| **ChittyLedger** | `ledger.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |
| **ChittyScore** | `score.chitty.cc` | `src/lib/chittyservices.js` | ✅ Integrated |

### Infrastructure
| Service | URL | Description |
|---------|-----|-------------|
| **Service Registry** | `registry.chitty.cc` | Dynamic service discovery |
| **ChittyAuth** | `auth.chitty.cc` | Authentication & authorization |
| **ChittyStorage** | `storage.chitty.cc` | File storage |
| **ChittyAI** | `ai.chitty.cc` | AI/ML services |

## Usage Examples

### ChittyID - Identity Management
```javascript
import { chittyID } from './lib/chittyservices'

// Mint new ChittyID (using real @chittyos/chittyid-client)
const newId = chittyID.mint({ type: 'user' })

// Validate ChittyID
const isValid = chittyID.validate('chitty_abc123')

// Get identity from API
const identity = await chittyID.getIdentity('user-123')
```

### ChittyCases - Case Management
```javascript
import cases from './lib/chittycases'

// Get all cases
const allCases = await cases.getCases()

// Create new case
const newCase = await cases.createCase({
  title: 'Smith v. ABC Corp',
  type: 'Financial Fraud',
  amountInDispute: 250000
})

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
await chat.sendMessage(roomId, 'Analysis complete!')
```

### ChittyLedger - Blockchain Transactions
```javascript
import { chittyLedger } from './lib/chittyservices'

// Record transaction on blockchain
await chittyLedger.recordTransaction({
  from: 'account-123',
  to: 'account-456',
  amount: 50000,
  type: 'wire'
})

// Get audit trail
const trail = await chittyLedger.getAuditTrail(entityId)

// Analyze transaction patterns
const analysis = await chittyLedger.analyzeTransactionPattern({
  accountId: 'account-123',
  timeRange: '30d'
})
```

### ChittyCertify - Document Certification
```javascript
import { chittyCertify } from './lib/chittyservices'

// Certify document for court
await chittyCertify.certifyForCourt(documentId, 'Cook County')

// Record chain of custody
await chittyCertify.recordCustody(documentId, {
  custodian: 'Evidence Room A',
  timestamp: new Date().toISOString()
})
```

### ChittyScore - Risk & Fraud Analysis
```javascript
import { chittyScore } from './lib/chittyservices'

// Get credit score
const credit = await chittyScore.getCreditScore(entityId)

// Analyze fraud risk
const fraudAnalysis = await chittyScore.analyzeFraudRisk({
  transactionId: 'tx-123',
  amount: 100000,
  pattern: 'unusual'
})

// Financial health assessment
const health = await chittyScore.analyzeFinancialHealth(entityId, {
  statements: financialData
})
```

### ChittyVerify - KYC/AML
```javascript
import { chittyVerify } from './lib/chittyservices'

// Perform KYC check
const kyc = await chittyVerify.performKYC({
  name: 'John Smith',
  dob: '1980-01-01',
  ssn: '***-**-1234'
})

// AML screening
const aml = await chittyVerify.performAMLCheck(entityId)

// Verify document authenticity
const verified = await chittyVerify.verifyDocument(documentData)
```

### ChittyChain - Blockchain Evidence
```javascript
import { chittyChain } from './lib/chittyservices'

// Store evidence on blockchain
await chittyChain.storeEvidence({
  documentId: 'doc-123',
  hash: 'sha256:abc...',
  metadata: { type: 'bank statement' }
})

// Verify evidence integrity
const verified = await chittyChain.verifyEvidence(evidenceId)

// Generate cryptographic proof
const proof = await chittyChain.generateProof(dataHash)
```

### ChittyTrust - Reputation Management
```javascript
import { chittyTrust } from './lib/chittyservices'

// Get trust score
const trust = await chittyTrust.getTrustScore(entityId)

// Get reputation data
const reputation = await chittyTrust.getReputation(entityId)

// Endorse entity
await chittyTrust.endorseEntity(entityId, {
  endorsementType: 'financial-integrity',
  score: 95
})
```

## Service Discovery

All services support both direct URL configuration and automatic discovery via `registry.chitty.cc`:

### Direct Configuration
```env
VITE_CASES_URL=https://cases.chitty.cc
VITE_CHAT_URL=https://chat.chitty.cc
VITE_ID_URL=https://id.chitty.cc
VITE_SCHEMA_URL=https://schema.chitty.cc
VITE_CERTIFY_URL=https://certify.chitty.cc
VITE_LEDGER_URL=https://ledger.chitty.cc
VITE_CHAIN_URL=https://chain.chitty.cc
VITE_TRUST_URL=https://trust.chitty.cc
VITE_SCORE_URL=https://score.chitty.cc
VITE_VERIFY_URL=https://verify.chitty.cc
```

### Service Registry
```env
VITE_USE_REGISTRY=true
VITE_REGISTRY_URL=https://registry.chitty.cc
```

The system automatically falls back to direct URLs when the registry is unavailable.

## Architecture

```
ChittyTrace Frontend
├── Core API (ChittyConnect)
│   └── Main financial forensics API
├── Cases (ChittyCases)
│   └── Case lifecycle management
├── Chat (ChittyChat)
│   └── Real-time collaboration
├── Identity (ChittyID)
│   ├── @chittyos/chittyid-client (NPM)
│   └── Identity management API
├── Blockchain Infrastructure
│   ├── ChittyLedger (Transaction ledger)
│   └── ChittyChain (Evidence storage)
├── Verification & Compliance
│   ├── ChittyVerify (KYC/AML)
│   ├── ChittyCertify (Document certification)
│   └── ChittySchema (Data validation)
└── Trust & Scoring
    ├── ChittyTrust (Reputation)
    └── ChittyScore (Credit/Risk/Fraud)
```

## Components

### 9 UI Modules
1. **Query Interface** - AI document Q&A
2. **Document Scanner** - File upload & processing
3. **Fund Flow Tracer** - Money movement visualization
4. **Timeline Viewer** - Chronological events
5. **Exhibit Generator** - Court packages
6. **Form Filler** - AI form completion
7. **Evidence Browser** - Document management
8. **Case Manager** - Full case management (ChittyCases)
9. **Chat Interface** - Team collaboration (ChittyChat)

## Build Output

```
dist/index.html           0.46 kB
dist/assets/index.css    50.33 kB (gzip: 8.10 kB)
dist/assets/index.js    249.53 kB (gzip: 72.68 kB)
```

## Support

- **Website**: https://chittycorp.com
- **Support**: support@chittycorp.com
- **GitHub**: https://github.com/ChittyApps/flow-of-funds-analyzer
