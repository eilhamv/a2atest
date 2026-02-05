# 🚀 Deploy Email Agent to Railway - Step by Step

## Current Status
✅ Email agent is working locally on http://localhost:5004
⏳ Let's deploy it to Railway.app now!

---

## Step 1: Create Railway Account (2 minutes)

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Click **"Login with GitHub"** (easiest option)
4. Authorize Railway to access your GitHub
5. ✅ You now have a Railway account with **$5 free credit**!

---

## Step 2: Prepare the Code (1 minute)

The email-agent directory is already ready! It has everything Railway needs:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command
- ✅ `railway.toml` - Configuration

**But first, we need to push it to GitHub.**

### Option A: If you already have a GitHub repo

```bash
cd /Users/harishankar/Downloads/a2a

# Add the email-agent files
git add email-agent/
git commit -m "Add email agent for Railway deployment"
git push origin main
```

### Option B: If you DON'T have a GitHub repo yet

```bash
cd /Users/harishankar/Downloads/a2a

# Initialize git repo
git init
git add .
git commit -m "Initial commit with email agent"

# Create repo on GitHub (go to github.com/new)
# Then connect and push:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy to Railway (3 minutes)

### Method 1: Deploy from GitHub (Recommended)

1. **In Railway Dashboard**:
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your repository
   - Railway will detect Python automatically

2. **Configure the service**:
   - Railway will show "Building..."
   - Wait 2-3 minutes for build to complete
   - You'll see "Deployed" when ready

3. **Get your public URL**:
   - Click on your project
   - Go to **"Settings"** tab
   - Click **"Generate Domain"** under "Networking"
   - You'll get a URL like: `https://email-agent-production-xxxx.up.railway.app`

### Method 2: Deploy via Railway CLI (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd email-agent
railway init
railway up
```

---

## Step 4: Test Your Deployed Agent (1 minute)

Once deployed, test it:

```bash
# Replace with YOUR Railway URL
export RAILWAY_URL="https://email-agent-production-xxxx.up.railway.app"

# Test AgentCard
curl $RAILWAY_URL/.well-known/agent.json

# Test sending email
curl -X POST $RAILWAY_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Send email to test@example.com with subject Hello and message Testing from Railway"}],
        "messageId": "test-123"
      }
    },
    "id": "req-123"
  }'
```

You should see a successful email response! 🎉

---

## Step 5: Update Agent Configuration (2 minutes)

Now update the agent to use the Railway URL:

1. **Edit `email-agent/__main__.py`**:

```python
# Find this line (around line 58):
url='http://localhost:5004',

# Change to your Railway URL:
url='https://email-agent-production-xxxx.up.railway.app',
```

2. **Commit and push**:

```bash
git add email-agent/__main__.py
git commit -m "Update agent URL to Railway"
git push
```

Railway will automatically redeploy! (takes 1-2 minutes)

---

## Step 6: Register with Context Forge (1 minute)

Now register the remote agent:

1. **Update the registration script**:

Edit `scripts/register_remote_agent.py`:

```python
# Find this line (around line 18):
"endpoint_url": "http://localhost:5004",

# Change to your Railway URL:
"endpoint_url": "https://email-agent-production-xxxx.up.railway.app",
```

2. **Run the registration**:

```bash
# Make sure TOKEN is set
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

# Register the remote agent
python3 scripts/register_remote_agent.py
```

You should see:
```
✅ email_agent registered successfully!
📍 Endpoint: https://email-agent-production-xxxx.up.railway.app
🌐 Location: remote
☁️  Provider: railway
```

---

## Step 7: Test via Orchestrator (1 minute)

Now test the complete system:

```bash
cd orchestrator
python3 orchestrator.py

# When it starts, try:
Query> Send email to john@example.com with subject Test and message Hello from remote agent

# You should see:
# 🎯 Matched 1 agent(s):
#    • email_agent.send_email
# 🔄 Calling email_agent...
# ✅ email_agent: Email sent successfully!
```

**The orchestrator just called your agent on Railway.app!** 🎉

---

## 🎉 Success!

You now have:
- ✅ Email agent deployed to Railway.app
- ✅ Public URL accessible from anywhere
- ✅ Registered with Context Forge as a remote agent
- ✅ Orchestrator routing queries to the remote agent

## 📊 What You've Achieved

```
Context Forge (localhost:4444)
    ├── Local Agents
    │   ├── Weather (localhost:5001)
    │   ├── Calculator (localhost:5002)
    │   └── Travel (localhost:5003)
    │
    └── Remote Agents
        └── Email (Railway.app) ← YOU JUST DEPLOYED THIS! 🌐
```

---

## 🐛 Troubleshooting

### Railway build fails
```bash
# Check logs in Railway dashboard
# Or via CLI:
railway logs
```

### Agent not responding
```bash
# Check if service is running in Railway dashboard
# Test the URL directly:
curl https://your-url.railway.app/.well-known/agent.json
```

### Can't access Railway URL
- Make sure you generated a domain in Railway settings
- Check if the service is running (not sleeping)

---

## 💰 Cost

**Railway Free Tier**:
- $5 credit/month
- 500 execution hours/month
- Perfect for this demo!

**This agent uses**:
- ~$0.01/hour if running 24/7
- ~$7/month for always-on
- **But**: You can stop it when not in use to save credits

---

## 🎯 Next Steps

1. ✅ Deploy to Railway (you're doing this now!)
2. ⏳ Test the remote agent
3. ⏳ Try hybrid queries (local + remote agents)
4. ⏳ Show off your hybrid A2A system!

---

**Need help?** Check the full guide: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)