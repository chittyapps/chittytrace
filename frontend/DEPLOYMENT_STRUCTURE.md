# ChittyTrace Deployment Structure

## URL Architecture

ChittyTrace follows the ChittyCorp subdomain pattern:

```
┌─────────────────────────────────────────┐
│        ChittyCorp Domain Structure       │
└─────────────────────────────────────────┘

🌐 Marketing Site
   https://chitty.cc/trace
   ├── Landing page
   ├── Features
   ├── Pricing
   └── Documentation

📱 Application
   https://app.chitty.cc/trace
   ├── React Frontend (this project)
   ├── 9 UI Modules
   ├── Case Management
   └── Team Collaboration

🔧 API/Service
   https://trace.chitty.cc
   ├── Python Backend
   ├── Claude Integration
   ├── Document Processing
   ├── Fund Tracing
   └── Exhibit Generation
```

## Deployment Mapping

### 1. Frontend App → `app.chitty.cc/trace`

**What:** React application (this project)
**Where:** Cloudflare Pages
**Path:** `/trace`

```bash
# Deploy
npm run build
wrangler pages deploy dist --project-name=chittytrace

# Configure in Cloudflare Dashboard
Domain: app.chitty.cc
Path: /trace/*
```

**Configuration:**
```env
VITE_API_URL=https://trace.chitty.cc
VITE_USE_REGISTRY=true
```

### 2. Backend Service → `trace.chitty.cc`

**What:** Python FastAPI backend
**Where:** Cloudflare Workers / Railway / Render
**Subdomain:** `trace`

**Endpoints:**
- `https://trace.chitty.cc/api/query`
- `https://trace.chitty.cc/api/scan`
- `https://trace.chitty.cc/api/trace-funds`
- `https://trace.chitty.cc/api/timeline`
- `https://trace.chitty.cc/api/exhibits`

**CORS Configuration:**
```python
ALLOWED_ORIGINS = [
    "https://app.chitty.cc",
    "https://chitty.cc"
]
```

### 3. Marketing Page → `chitty.cc/trace`

**What:** Marketing/landing page
**Where:** Main ChittyCorp site
**Path:** `/trace`

**Content:**
- Product overview
- Features showcase
- Demo videos
- Pricing plans
- Documentation links
- Sign up / Login buttons → app.chitty.cc/trace

## Cloudflare Pages Configuration

### Project Settings

**Project Name:** `chittytrace`

**Build Configuration:**
```yaml
Build command: npm run build
Build output directory: dist
Root directory: frontend
Node version: 20
```

**Environment Variables:**
```
VITE_API_URL=https://trace.chitty.cc
VITE_API_TOKEN=(secret)
VITE_ENVIRONMENT=production
VITE_USE_REGISTRY=true
VITE_REGISTRY_URL=https://registry.chitty.cc
```

### Custom Domain Setup

1. **Add Custom Domain:**
   - Go to Cloudflare Pages → chittytrace → Custom domains
   - Add: `app.chitty.cc`
   - Subdomain: `app`
   - Path: `/trace`

2. **DNS Configuration:**
   ```
   Type: CNAME
   Name: app
   Target: chittytrace.pages.dev
   Proxy: Yes (orange cloud)
   ```

3. **Page Rules:**
   ```
   URL: app.chitty.cc/trace*
   Setting: Always Use HTTPS
   ```

## Service Deployment (Backend)

### Option 1: Cloudflare Workers

```bash
# Deploy Python backend as Worker
cd ../  # Root directory
wrangler deploy --name chittytrace-api
```

**Custom Domain:**
```toml
# wrangler.toml
name = "chittytrace-api"
route = { pattern = "trace.chitty.cc/*", zone_name = "chitty.cc" }
```

### Option 2: Railway

```bash
# railway.json
{
  "name": "chittytrace-api",
  "domains": ["trace.chitty.cc"]
}
```

### Option 3: Render

```yaml
# render.yaml
services:
  - type: web
    name: chittytrace-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    domains:
      - trace.chitty.cc
```

## GitHub Actions Workflow

### Frontend Deployment

```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build
        env:
          VITE_API_URL: https://trace.chitty.cc
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: chittytrace
          directory: dist
```

## URL Examples

### Production URLs

**Application Access:**
```
https://app.chitty.cc/trace
https://app.chitty.cc/trace/query
https://app.chitty.cc/trace/cases
https://app.chitty.cc/trace/chat
```

**API Endpoints:**
```
https://trace.chitty.cc/api/query
https://trace.chitty.cc/api/scan
https://trace.chitty.cc/api/trace-funds
https://trace.chitty.cc/health
```

**Marketing:**
```
https://chitty.cc/trace
https://chitty.cc/trace/features
https://chitty.cc/trace/pricing
https://chitty.cc/trace/docs
```

## Security

### SSL/TLS
- ✅ Automatic SSL via Cloudflare
- ✅ HTTP → HTTPS redirect
- ✅ HSTS enabled

### CORS Headers

**Frontend (_headers in public/):**
```
/trace/*
  Access-Control-Allow-Origin: https://trace.chitty.cc
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

**Backend:**
```python
ALLOWED_ORIGINS = [
    "https://app.chitty.cc",
    "https://chitty.cc"
]
```

## Monitoring

### Application Monitoring
```
Cloudflare Analytics → app.chitty.cc
Filter: /trace/*
```

### API Monitoring
```
Service Endpoint: trace.chitty.cc
Health Check: /health
Uptime: 99.9% SLA
```

## Rollout Strategy

### Phase 1: Staging (app.staging.chitty.cc/trace)
1. Deploy to staging environment
2. Run integration tests
3. Verify all services
4. Load testing

### Phase 2: Production Deploy
1. Deploy backend to trace.chitty.cc
2. Deploy frontend to app.chitty.cc/trace
3. Update DNS
4. Smoke tests

### Phase 3: Marketing Launch
1. Add marketing page at chitty.cc/trace
2. Public announcement
3. Monitor metrics

## Support

- **Infrastructure:** Cloudflare Support
- **Application:** support@chittycorp.com
- **Documentation:** docs.chitty.cc

## Quick Deploy Commands

```bash
# Deploy Frontend
cd frontend
npm run build
wrangler pages deploy dist --project-name=chittytrace

# Deploy Backend (example for Cloudflare Workers)
cd ../
wrangler deploy --name chittytrace-api

# Verify Deployment
curl https://app.chitty.cc/trace
curl https://trace.chitty.cc/health
```

---

**Deployment Target:**
- Frontend: `app.chitty.cc/trace`
- Backend: `trace.chitty.cc`
- Marketing: `chitty.cc/trace`

**Status:** Ready for Production Deployment 🚀
