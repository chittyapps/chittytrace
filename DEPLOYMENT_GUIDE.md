# Flow of Funds Analyzer - Deployment Guide

## 🚀 Free Deployment Options

### Option 1: Replit (Recommended - Easiest & Free)

1. **Create Replit Account**:
   - Go to [replit.com](https://replit.com)
   - Sign up for free account

2. **Import Project**:
   ```bash
   # In Replit, create new Python repl
   # Upload all files from flow_analyzer/ directory
   # Or clone from GitHub if you push there first
   ```

3. **Configure Environment**:
   - In Replit secrets tab, add:
     - `ANTHROPIC_API_KEY`: Your Claude API key
     - `ARIAS_DATABASE_URL`: Your Neon database URL (format: `postgresql://user:pass@host/db`)
     - `CLOUDFLARE_WORKER_URL`: (optional) Email ingestion endpoint

4. **Run Application**:
   ```bash
   # Replit will auto-install dependencies from requirements.txt
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

5. **Access**: Replit will provide a public URL automatically

### Option 2: Cloudflare Workers (API Only - Free Tier 100k requests/day)

1. **Install Wrangler**:
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**:
   ```bash
   wrangler login
   ```

3. **Deploy**:
   ```bash
   cd flow_analyzer
   npm install
   wrangler deploy
   ```

4. **Set Environment Variables**:
   ```bash
   wrangler secret put ANTHROPIC_API_KEY
   wrangler secret put ARIAS_DATABASE_URL
   ```

5. **Access**: Your worker will be available at `https://flow-analyzer.your-subdomain.workers.dev`

### Option 3: Railway (Free $5 monthly credit)

1. **Create Railway Account**:
   - Go to [railway.app](https://railway.app)
   - Connect GitHub account

2. **Deploy from GitHub**:
   - Push code to GitHub repository
   - Create new Railway project from GitHub repo
   - Railway auto-detects Python and deploys

3. **Environment Variables**:
   - In Railway dashboard, add environment variables:
     - `ANTHROPIC_API_KEY`
     - `ARIAS_DATABASE_URL`
     - `PORT=8501`

### Option 4: Render (Free Tier)

1. **Create Render Account**:
   - Go to [render.com](https://render.com)
   - Sign up for free

2. **Deploy Web Service**:
   - Connect GitHub repository
   - Choose "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Environment Variables**:
   - Add in Render dashboard:
     - `ANTHROPIC_API_KEY`
     - `ARIAS_DATABASE_URL`

## 📊 Neon Database Integration

### Connecting to Existing Arias v Bianchi Database

The system is configured to connect to your existing Arias v Bianchi Neon database:

1. **Database URL Format**:
   ```
   postgresql://username:password@ep-database-name.us-east-1.aws.neon.tech/database_name?sslmode=require
   ```

2. **Environment Variable**:
   ```bash
   # Set this in your deployment platform
   ARIAS_DATABASE_URL=postgresql://your_user:your_password@your_host.neon.tech/arias_v_bianchi
   ```

3. **Automatic Cross-Reference**:
   - System automatically searches existing data
   - Links new documents to existing timeline events
   - Cross-references transaction amounts and dates
   - Identifies related case documents

### Database Verification

The system will automatically:
- Verify connection to correct Arias v Bianchi database
- Check for existing case-related documents
- Log verification results in console

## 🔧 Configuration

### Required Environment Variables

```bash
# Core API
ANTHROPIC_API_KEY=sk-ant-api03-xxx  # Your Claude API key

# Database (Existing Arias v Bianchi)
ARIAS_DATABASE_URL=postgresql://user:pass@host.neon.tech/arias_v_bianchi

# Optional - Email Integration
CLOUDFLARE_WORKER_URL=https://your-worker.workers.dev/email-ingestion
CLOUDFLARE_WORKER_TOKEN=your_auth_token

# Optional - API Security
API_TOKENS=token1,token2,token3
```

### Platform-Specific Setup

#### Replit
- Add variables in "Secrets" tab
- No additional configuration needed

#### Cloudflare Workers
```bash
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put ARIAS_DATABASE_URL
```

#### Railway/Render
- Add variables in platform dashboard
- Set `PORT=8501` for Streamlit

## 🎯 Quick Start Commands

### For Replit (Copy-Paste Ready)
```bash
# After uploading files to Replit
pip install -r requirements.txt
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### For Cloudflare Workers
```bash
npm install
wrangler login
wrangler deploy
```

### For Local Development
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
streamlit run app.py
```

## 🔍 Testing Database Connection

Add this test script to verify Arias database connection:

```python
# test_connection.py
import asyncio
from neon_integration import AriasNeonIntegration

async def test_connection():
    db = AriasNeonIntegration()
    await db.initialize()
    
    # Test query
    docs = await db.search_case_documents("bianchi")
    print(f"Found {len(docs)} related documents")
    
    timeline = await db.get_case_timeline()
    print(f"Found {len(timeline)} timeline events")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

## 📱 Access URLs

After deployment, your application will be available at:

- **Replit**: `https://your-repl-name.your-username.repl.co`
- **Cloudflare Workers**: `https://flow-analyzer.your-subdomain.workers.dev`
- **Railway**: `https://your-app-name.up.railway.app`
- **Render**: `https://your-app-name.onrender.com`

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Verify `ARIAS_DATABASE_URL` format
   - Check Neon database is running
   - Ensure SSL mode is enabled

2. **Claude API Errors**:
   - Verify `ANTHROPIC_API_KEY` is correct
   - Check API quota limits

3. **Port Issues**:
   - Ensure `PORT=8501` environment variable
   - Use `--server.address=0.0.0.0` for external access

4. **Import Errors**:
   - Verify all files uploaded correctly
   - Check `requirements.txt` dependencies installed

### Debugging

Check logs in your deployment platform:
- Replit: Console tab
- Cloudflare: `wrangler tail`
- Railway/Render: Logs section in dashboard

## Professional Deployment

For enterprise deployments, ChittyCorp offers:
- Custom deployment assistance
- White-label solutions
- Commercial licensing
- Professional support

Contact: support@chittycorp.com

## 💰 Cost Breakdown (Free Tiers)

- **Replit**: Free (with some compute limits)
- **Cloudflare Workers**: 100k requests/day free
- **Railway**: $5/month credit (usually sufficient)
- **Render**: 750 hours/month free
- **Neon Database**: 1 database free forever

**Total Cost**: $0-5/month depending on usage

## 🚀 Recommended Quick Deployment

**For immediate deployment, use Replit**:

1. Go to replit.com → Create Python repl
2. Upload all files from `flow_analyzer/` folder
3. Add secrets: `ANTHROPIC_API_KEY` and `ARIAS_DATABASE_URL`
4. Run: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
5. Share the generated URL

This will give you a working deployment in under 10 minutes!