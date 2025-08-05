import { Hono } from 'hono'
import { cors } from 'hono/cors'
import Anthropic from '@anthropic-ai/sdk'

const app = new Hono()

// Enable CORS
app.use('/*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization'],
}))

// Initialize Anthropic client
const getAnthropicClient = (apiKey) => {
  return new Anthropic({ apiKey })
}

// Health check
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'Flow Analyzer API'
  })
})

// Document analysis endpoint
app.post('/api/analyze', async (c) => {
  try {
    const { query, context, apiKey } = await c.req.json()
    
    if (!apiKey) {
      return c.json({ error: 'API key required' }, 401)
    }

    const anthropic = getAnthropicClient(apiKey)
    
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      temperature: 0,
      messages: [{
        role: 'user',
        content: `Analyze the following financial documents and answer the query:

Query: ${query}

Context: ${context || 'No additional context provided'}

Please provide a detailed analysis with specific references to the documents.`
      }]
    })

    return c.json({
      analysis: response.content[0].text,
      metadata: {
        model: 'claude-3-5-sonnet-20241022',
        timestamp: new Date().toISOString(),
        tokens_used: response.usage
      }
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// Timeline extraction endpoint
app.post('/api/timeline', async (c) => {
  try {
    const { documents, dateRange, apiKey } = await c.req.json()
    
    if (!apiKey) {
      return c.json({ error: 'API key required' }, 401)
    }

    const anthropic = getAnthropicClient(apiKey)
    
    const prompt = `Extract timeline events from these documents:

Documents: ${JSON.stringify(documents.slice(0, 5))} // Limit for token usage

Date Range: ${dateRange?.start || 'Any'} to ${dateRange?.end || 'Any'}

Extract:
1. Wire transfers with amounts, dates, accounts
2. Property purchases
3. Legal filings
4. Bank transactions over $10,000
5. Corporate events

Return as JSON array with fields: date, type, description, amount, source_account, destination_account`
    
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      temperature: 0,
      messages: [{ role: 'user', content: prompt }]
    })

    // Try to parse JSON, fallback to raw response
    let timeline
    try {
      timeline = JSON.parse(response.content[0].text)
    } catch {
      timeline = { raw_response: response.content[0].text }
    }

    return c.json({
      timeline,
      metadata: {
        documents_processed: documents.length,
        timestamp: new Date().toISOString()
      }
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// Exhibit generation endpoint
app.post('/api/exhibits', async (c) => {
  try {
    const { documents, caseInfo, purpose, apiKey } = await c.req.json()
    
    if (!apiKey) {
      return c.json({ error: 'API key required' }, 401)
    }

    const anthropic = getAnthropicClient(apiKey)
    
    const prompt = `Generate a Cook County court-compliant exhibit package:

Case: ${caseInfo.caption}
Case Number: ${caseInfo.case_number}
Purpose: ${purpose}

Documents to include: ${JSON.stringify(documents)}

Create:
1. Cover letter
2. Table of contents
3. Exhibit authentication affidavits
4. Certificate of service
5. Formatting instructions per Cook County requirements

Format with:
- 8.5" x 11" pages
- 1" margins
- Times New Roman 12pt
- Double spacing
- Sequential exhibit numbering`
    
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      temperature: 0,
      messages: [{ role: 'user', content: prompt }]
    })

    return c.json({
      exhibit_package: response.content[0].text,
      case_info: caseInfo,
      documents_count: documents.length,
      generated_at: new Date().toISOString()
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// Form filling endpoint
app.post('/api/forms/fill', async (c) => {
  try {
    const { template, data, formType, apiKey } = await c.req.json()
    
    if (!apiKey) {
      return c.json({ error: 'API key required' }, 401)
    }

    const anthropic = getAnthropicClient(apiKey)
    
    const prompt = `Fill this form template with the provided data:

Template:
${template}

Data:
${JSON.stringify(data, null, 2)}

Instructions:
1. Replace all placeholders with appropriate data
2. Ensure legal formatting
3. Add current date where needed
4. Verify all fields are completed`
    
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      temperature: 0,
      messages: [{ role: 'user', content: prompt }]
    })

    return c.json({
      filled_form: response.content[0].text,
      form_type: formType,
      filled_at: new Date().toISOString()
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// Command execution endpoint
app.post('/api/commands', async (c) => {
  try {
    const { command, parameters, apiKey } = await c.req.json()
    
    if (!apiKey) {
      return c.json({ error: 'API key required' }, 401)
    }

    const anthropic = getAnthropicClient(apiKey)
    
    const commandPrompts = {
      trace_funds: `Trace fund flow from ${parameters.source_account} to ${parameters.destination}. 
                   Include all intermediate steps, amounts, dates, and institutions.`,
      
      analyze_transactions: `Analyze transactions for ${parameters.account}. 
                           Look for patterns, anomalies, and compliance issues.`,
      
      detect_patterns: `Detect financial patterns in the data. 
                       Look for structured transactions, unusual timing, related parties.`,
      
      cross_reference_database: `Cross-reference with connected database. 
                             Find matching transactions, property records, legal filings.`
    }
    
    const prompt = commandPrompts[command] || `Execute command: ${command} with parameters: ${JSON.stringify(parameters)}`
    
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      temperature: 0,
      messages: [{ role: 'user', content: prompt }]
    })

    return c.json({
      command,
      result: response.content[0].text,
      parameters,
      executed_at: new Date().toISOString()
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// Email ingestion endpoint (for nick@chitty.cc)
app.post('/api/emails/ingest', async (c) => {
  try {
    const { email, dateRange, apiKey } = await c.req.json()
    
    // This would integrate with Email Workers API or similar
    // For now, return a placeholder response
    
    return c.json({
      message: 'Email ingestion endpoint - requires Email Workers integration',
      email,
      date_range: dateRange,
      status: 'placeholder'
    })
  } catch (error) {
    return c.json({ error: error.message }, 500)
  }
})

// API documentation endpoint
app.get('/api/docs', (c) => {
  return c.json({
    title: 'ChittyTrace API',
    version: '1.0.0',
    endpoints: {
      'POST /api/analyze': 'Analyze documents with natural language queries',
      'POST /api/timeline': 'Extract timeline events from documents',
      'POST /api/exhibits': 'Generate Cook County court exhibits',
      'POST /api/forms/fill': 'Fill form templates with data',
      'POST /api/commands': 'Execute analysis commands',
      'POST /api/emails/ingest': 'Ingest emails for analysis',
      'GET /health': 'Health check endpoint'
    },
    authentication: 'Bearer token in Authorization header or apiKey in request body',
    note: 'All endpoints require ANTHROPIC_API_KEY for Claude integration'
  })
})

export default app