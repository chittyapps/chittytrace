# 🚀 ChittyTrace Deployment Commands

## Quick Deploy (5 minutes)

### 1. Deploy to Cloudflare Pages

```bash
# From frontend directory
cd /home/runner/workspace/frontend

# Build for production
npm run build

# Deploy to app.chitty.cc/trace
npx wrangler pages deploy dist \
  --project-name=chittytrace \
  --branch=main

# Get deployment URL
# Will be: chittytrace.pages.dev (temp)
# Configure custom domain: app.chitty.cc
```

### 2. Configure Custom Domain

```bash
# Via Cloudflare Dashboard:
# 1. Go to Pages → chittytrace → Custom domains
# 2. Add domain: app.chitty.cc
# 3. Add path: /trace
# 4. DNS auto-configured

# Or via CLI:
wrangler pages deployment create chittytrace \
  --project-name=chittytrace \
  --custom-domain=app.chitty.cc
```

### 3. Set Environment Variables

```bash
# Via CLI
wrangler pages deployment env set \
  --project-name=chittytrace \
  VITE_API_URL=https://trace.chitty.cc \
  VITE_USE_REGISTRY=true \
  VITE_REGISTRY_URL=https://registry.chitty.cc

# Or via Dashboard:
# Pages → chittytrace → Settings → Environment variables
```

## Complete Deployment URLs

```
Frontend:  https://app.chitty.cc/trace
Backend:   https://trace.chitty.cc
Marketing: https://chitty.cc/trace
```

## GitHub Actions (Automatic)

### Setup Once

```bash
# Add GitHub secrets
gh secret set CLOUDFLARE_API_TOKEN
gh secret set CLOUDFLARE_ACCOUNT_ID
gh secret set VITE_API_TOKEN

# Push to trigger deployment
git add .
git commit -m "ChittyTrace production ready"
git push origin main
```

### Every Push After

```bash
git add .
git commit -m "Update feature"
git push
# Auto-deploys to app.chitty.cc/trace
```

## Verification Commands

```bash
# Check deployment status
wrangler pages deployment list --project-name=chittytrace

# Test endpoints
curl https://app.chitty.cc/trace
curl https://trace.chitty.cc/health

# View logs
wrangler pages deployment tail --project-name=chittytrace
```

## DNS Configuration

```bash
# If using Cloudflare DNS (automatic)
# Already configured

# If using external DNS:
Type: CNAME
Name: app
Value: chittytrace.pages.dev
Proxy: Yes
```

## Rollback

```bash
# List deployments
wrangler pages deployment list --project-name=chittytrace

# Rollback to previous
wrangler pages deployment promote <deployment-id> \
  --project-name=chittytrace
```

## Backend Deployment (trace.chitty.cc)

### Option A: Cloudflare Workers

```bash
# From root directory
cd /home/runner/workspace

# Deploy Python backend
wrangler deploy --name chittytrace-api

# Configure custom domain
wrangler route create trace.chitty.cc/* \
  --service chittytrace-api
```

### Option B: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Add custom domain in dashboard
# Domain: trace.chitty.cc
```

### Option C: Render

```bash
# Create render.yaml (already exists)
git push origin main

# In Render Dashboard:
# 1. New Web Service
# 2. Connect repository
# 3. Add domain: trace.chitty.cc
```

## Production Checklist

- [ ] Frontend built successfully
- [ ] Backend deployed to trace.chitty.cc
- [ ] Environment variables configured
- [ ] Custom domains configured
- [ ] HTTPS enabled (automatic via Cloudflare)
- [ ] CORS configured in backend
- [ ] Health checks passing
- [ ] Analytics enabled
- [ ] Monitoring configured

## Quick Test

```bash
# Test frontend
curl -I https://app.chitty.cc/trace
# Expected: 200 OK

# Test backend
curl https://trace.chitty.cc/health
# Expected: {"status":"ok"}

# Test service registry
curl https://registry.chitty.cc/services/chitty-trace-api
# Expected: Service info JSON
```

## Common Issues

### Issue: "Module not found"
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: "CORS error"
**Solution:** Add origin to backend:
```python
ALLOWED_ORIGINS = ["https://app.chitty.cc"]
```

### Issue: "API not responding"
**Solution:** Check backend health:
```bash
curl https://trace.chitty.cc/health
```

## Monitoring URLs

```bash
# Cloudflare Analytics
https://dash.cloudflare.com/pages/chittytrace/analytics

# Deployment logs
https://dash.cloudflare.com/pages/chittytrace/deployments

# Custom domain status
https://dash.cloudflare.com/pages/chittytrace/domains
```

## Update Deployment

```bash
# Make changes
# git commit

# Rebuild
npm run build

# Redeploy
npx wrangler pages deploy dist --project-name=chittytrace

# Or let GitHub Actions handle it
git push origin main
```

## Environment-Specific Builds

```bash
# Development
npm run dev

# Production preview
npm run build
npm run preview

# Production deploy
npm run build
wrangler pages deploy dist --project-name=chittytrace
```

## Success Indicators

✅ **Frontend Live:**
```bash
$ curl -I https://app.chitty.cc/trace
HTTP/2 200
content-type: text/html
```

✅ **Backend Live:**
```bash
$ curl https://trace.chitty.cc/health
{"status":"ok","version":"1.0.0"}
```

✅ **Service Registry:**
```bash
$ curl https://registry.chitty.cc/services/chitty-trace-api
{"url":"https://trace.chitty.cc","status":"active"}
```

## Support

- **Cloudflare:** https://dash.cloudflare.com
- **Wrangler Docs:** https://developers.cloudflare.com/workers/wrangler/
- **ChittyCorp:** support@chittycorp.com

---

**Next Step:** Run the deploy command above! 🚀
