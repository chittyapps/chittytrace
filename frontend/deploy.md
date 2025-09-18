# Deploy Modern React App to Cloudflare Workers AI

## Option 1: Manual Deployment (Recommended)

### Download the Project
1. Download these files to your local machine:
   - `worker.js` - Main Cloudflare Worker
   - `wrangler.toml` - Configuration file
   - `package.json` - Dependencies

### Deploy Locally
```bash
# Install Wrangler globally
npm install -g wrangler

# Authenticate with Cloudflare (interactive)
wrangler login

# Deploy the worker
wrangler deploy
```

## Option 2: Copy & Paste Deployment

### Step 1: Create Worker in Cloudflare Dashboard
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to Workers & Pages
3. Create a new Worker
4. Copy the contents of `worker.js` into the editor

### Step 2: Enable AI Binding
1. In Worker settings, go to "Variables and Secrets"
2. Add AI binding named "AI"
3. Save and deploy

## Option 3: GitHub Actions (Automated)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloudflare Workers
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: cloudflare/wrangler-action@v3
      with:
        apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        workingDirectory: 'frontend'
```

## What You Get After Deployment

- **Live URL**: `https://modern-react-app.your-subdomain.workers.dev`
- **AI Endpoints**:
  - `/api/ai/generate` - Text generation
  - `/api/ai/classify` - Image classification
  - `/api/health` - Health check
- **Global Edge**: Runs on 200+ locations worldwide
- **AI-Powered UI**: Interactive React app with AI features

## Local Testing

The worker is ready to test locally:
```bash
wrangler dev --local
```

Visit `http://localhost:8787` to see your app in action!