# ChittyTrace Deployment Guide

## Quick Deploy to Cloudflare Pages

### Prerequisites
- Cloudflare account
- Wrangler CLI installed globally or use npx

### Option 1: Manual Deploy (Fastest)

```bash
# Build the app
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy dist --project-name=chittytrace

# Or if you have wrangler installed globally
wrangler pages deploy dist --project-name=chittytrace
```

### Option 2: GitHub Actions (Automatic)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "ChittyTrace with full ChittyCorp ecosystem"
   git push origin main
   ```

2. **Set GitHub Secrets:**
   Go to Settings → Secrets and variables → Actions → New repository secret

   Add these secrets:
   ```
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   CLOUDFLARE_ACCOUNT_ID=your_account_id
   VITE_API_URL=https://your-api-domain.com
   VITE_API_TOKEN=your_bearer_token
   ```

3. **Automatic Deployment:**
   - Every push to `main` triggers deployment
   - Pull requests create preview deployments

### Option 3: Connect Cloudflare Pages to Git

1. Go to Cloudflare Dashboard → Pages
2. Click "Create a project"
3. Connect your GitHub repository
4. Configure build settings:
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Root directory:** `frontend`

5. Set environment variables:
   ```
   VITE_API_URL=https://your-api-domain.com
   VITE_API_TOKEN=your_bearer_token
   VITE_ENVIRONMENT=production
   VITE_USE_REGISTRY=true
   VITE_REGISTRY_URL=https://registry.chitty.cc
   ```

## Configuration

### Environment Variables for Production

Create a `.env.production` file:

```env
# Main API
VITE_API_URL=https://api.chittytrace.com

# Service Registry (recommended)
VITE_USE_REGISTRY=true
VITE_REGISTRY_URL=https://registry.chitty.cc

# Authentication
VITE_API_TOKEN=production_token_here

# Environment
VITE_ENVIRONMENT=production

# Optional: Direct service URLs (if not using registry)
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

## Custom Domain

### Add Custom Domain to Cloudflare Pages

1. Go to your Pages project → Custom domains
2. Add your domain (e.g., `chittytrace.com`)
3. Follow DNS configuration instructions
4. SSL certificate auto-provisioned

## Performance Optimization

### Enable Production Features

The build is already optimized:
- ✅ Code splitting
- ✅ Tree shaking
- ✅ Minification
- ✅ Gzip compression
- ✅ CSS extraction

### Cloudflare Optimizations

1. **Enable Cloudflare Cache:**
   - Static assets cached at edge
   - Automatic cache invalidation on deploy

2. **Enable Cloudflare CDN:**
   - Global distribution
   - Fast load times worldwide

3. **Enable Workers:**
   - API proxying
   - Edge authentication

## Monitoring

### Set up Cloudflare Analytics

1. Enable Web Analytics in Cloudflare Dashboard
2. Add tracking code (automatically included)
3. Monitor:
   - Page views
   - Performance metrics
   - Geographic distribution

## Security

### HTTPS & Security Headers

Cloudflare Pages automatically provides:
- ✅ Free SSL/TLS certificates
- ✅ HTTP/2 and HTTP/3
- ✅ DDoS protection
- ✅ WAF (Web Application Firewall)

### Content Security Policy

Add to `_headers` file in `public/`:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self' https://chitty.cc https://*.chitty.cc; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
```

## Rollback

### Rollback to Previous Deployment

```bash
# List deployments
wrangler pages deployment list --project-name=chittytrace

# Rollback to specific deployment
wrangler pages deployment tail <deployment-id>
```

Or use Cloudflare Dashboard:
1. Go to Deployments tab
2. Click on previous deployment
3. Click "Rollback to this deployment"

## Backend Integration

### Connect to Python Backend

Your Python backend (running on port 8000) needs to be deployed separately.

**Options:**
1. **Cloudflare Workers** - Serverless Python
2. **Render** - Easy Python hosting
3. **Railway** - Full-stack deployments
4. **DigitalOcean App Platform** - Traditional hosting

Update `VITE_API_URL` to point to deployed backend.

### CORS Configuration

Ensure your backend allows requests from your Cloudflare Pages domain:

```python
# In your Python backend
ALLOWED_ORIGINS = [
    "https://chittytrace.pages.dev",
    "https://chittytrace.com",  # Your custom domain
]
```

## Testing

### Test Deployment

```bash
# Preview build locally
npm run build
npm run preview

# Opens preview at http://localhost:4173
```

### Test Production Build

```bash
# Test with production environment variables
VITE_API_URL=https://api.production.com npm run build
npm run preview
```

## Troubleshooting

### Build Fails

**Issue:** Build fails with module errors
**Solution:** Clear node_modules and reinstall
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API Connection Issues

**Issue:** Can't connect to backend API
**Solution:** Check CORS, verify VITE_API_URL is correct

### Service Registry Fails

**Issue:** Service discovery not working
**Solution:** Services fall back to direct URLs automatically. Verify fallback URLs in `.env`

## Post-Deployment

### Update DNS

If using custom domain, update DNS:
```
Type: CNAME
Name: chittytrace (or @)
Value: <project-name>.pages.dev
```

### Enable Analytics

Monitor usage via:
- Cloudflare Analytics
- Cloudflare Web Analytics
- Custom analytics integration

## Support

- **Cloudflare Docs:** https://developers.cloudflare.com/pages/
- **ChittyCorp Support:** support@chittycorp.com
- **GitHub Issues:** https://github.com/ChittyApps/flow-of-funds-analyzer/issues

## Next Steps

1. ✅ Build completed (`npm run build`)
2. 🚀 Deploy to Cloudflare Pages
3. 🌐 Configure custom domain
4. 🔐 Set environment variables
5. 📊 Enable monitoring
6. 🎉 Launch!
