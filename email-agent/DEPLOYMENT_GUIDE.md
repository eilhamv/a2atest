# 🚀 Railway.app Deployment Guide

## Current Status
✅ Email agent is working locally on http://localhost:5004
⏳ Ready to deploy to Railway.app for remote access

## Step-by-Step Deployment

### Step 1: Create Railway Account (Free)

1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email
4. **Free tier includes**: 500 hours/month, $5 credit

### Step 2: Prepare for Deployment

The email-agent directory already has everything needed:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command
- ✅ `railway.toml` - Railway configuration
- ✅ `__main__.py` - A2A server

### Step 3: Deploy via Railway Dashboard

#### Option A: Deploy from GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   cd /Users/harishankar/Downloads/a2a
   git init  # if not already a git repo
   git add email-agent/
   git commit -m "Add email agent for Railway deployment"
   git push origin main
   ```

2. **Connect to Railway**:
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python and deploy

3. **Configure**:
   - Railway will automatically:
     - Install dependencies from `requirements.txt`
     - Run the command from `Procfile`
     - Assign a public URL

#### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Deploy**:
   ```bash
   cd email-agent
   railway init
   railway up
   ```

### Step 4: Get Your Public URL

After deployment (takes 2-3 minutes):

1. Go to Railway dashboard
2. Click on your project
3. Go to "Settings" → "Domains"
4. You'll see a URL like:
   ```
   https://email-agent-production-xxxx.up.railway.app
   ```

5. **Test it**:
   ```bash
   curl https://email-agent-production-xxxx.up.railway.app/.well-known/agent.json
   ```

### Step 5: Update Agent Configuration

Once you have the Railway URL, update the agent:

1. **Edit `email-agent/__main__.py`**:
   ```python
   agent_card = AgentCard(
       name='email_agent',
       version='1.0.0',
       description='Remote SaaS email service agent',
       url='https://email-agent-production-xxxx.up.railway.app',  # ← Update this!
       protocolVersion='0.3.0',
       # ... rest stays the same
   )
   ```

2. **Redeploy**:
   ```bash
   git add email-agent/__main__.py
   git commit -m "Update agent URL to Railway"
   git push
   # Railway will auto-redeploy
   ```

### Step 6: Register with Context Forge

Now register the REMOTE agent:

```bash
# Set your token
export TOKEN='your-jwt-token'

# Register with Railway URL
curl -X POST http://localhost:4444/a2a \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "name": "email_agent",
      "endpoint_url": "https://email-agent-production-xxxx.up.railway.app",
      "agent_type": "jsonrpc",
      "description": "Remote SaaS email service for sending and tracking emails",
      "tags": ["email", "saas", "remote", "communication"],
      "visibility": "public",
      "metadata": {
        "location": "remote",
        "provider": "railway",
        "type": "saas"
      }
    }
  }'
```

Or use the script:
```bash
# Update endpoint_url in scripts/register_remote_agent.py first
python3 scripts/register_remote_agent.py
```

### Step 7: Test the Remote Agent

```bash
# Test via orchestrator
cd orchestrator
python orchestrator.py

# Query the remote agent
Query> Send email to test@example.com with subject Hello and message Testing remote agent
```

The orchestrator will now call your agent on Railway! 🎉

## Troubleshooting

### Railway Build Fails
```bash
# Check logs
railway logs

# Common issues:
# - Missing dependencies: Check requirements.txt
# - Port binding: Railway sets PORT env var automatically
```

### Agent Not Responding
```bash
# Check if service is running
curl https://your-url.railway.app/.well-known/agent.json

# Check Railway logs
railway logs --tail
```

### Update Deployment
```bash
# Any git push will trigger redeploy
git push origin main
```

## Cost Estimate

**Railway Free Tier**:
- 500 execution hours/month
- $5 credit/month
- Perfect for demos and testing

**For this agent**:
- Runs 24/7 = 720 hours/month
- With free tier: ~16 days free
- After that: ~$0.01/hour = ~$7/month

**Tip**: For demo purposes, you can:
- Stop the service when not in use
- Use Railway's sleep feature
- Deploy only when needed

## Alternative Free Platforms

If you want 100% free forever:

1. **Render.com** - Free tier with auto-sleep
2. **Fly.io** - 3 free VMs
3. **Replit** - Always-on with Hacker plan

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Get public URL
3. ✅ Update agent configuration
4. ✅ Register with Context Forge
5. ✅ Test with orchestrator
6. ✅ Update documentation

---

**Questions?** Check the main [README.md](README.md) or Railway docs at https://docs.railway.app