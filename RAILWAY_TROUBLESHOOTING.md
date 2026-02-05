# Railway Deployment Troubleshooting Guide

## Current Issue Analysis

### Problem
Agent runs successfully (logs show "Uvicorn running on http://0.0.0.0:5004") but Railway returns 404 "Application not found" when accessing the URL.

### Root Cause
The agent is hardcoded to port 5004, but Railway assigns a dynamic PORT environment variable (usually 3000 or random). Railway's proxy can't route traffic because the app isn't listening on the expected port.

## Solution Applied

### 1. Fixed Port Binding (✅ DONE)
Updated `email-agent/__main__.py` to:
- Read `PORT` from environment variable
- Read `RAILWAY_PUBLIC_DOMAIN` for the public URL
- Dynamically configure the AgentCard URL

```python
port = int(os.getenv('PORT', '5004'))
railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
base_url = f'https://{railway_url}' if railway_url else f'http://localhost:{port}'
```

### 2. Simplified Configuration (✅ DONE)
- Removed conflicting config files (railway.json, railway.toml, multiple Procfiles)
- Created single `Procfile` at root: `web: cd email-agent && python __main__.py`
- This is Railway's standard deployment method

### 3. Requirements (✅ VERIFIED)
Both `requirements.txt` files (root and email-agent/) contain all necessary dependencies:
- a2a-sdk
- starlette
- sse-starlette
- uvicorn
- httpx, httpx-sse
- pydantic, typing-extensions
- google-api-core, protobuf

## Next Steps to Deploy

### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix Railway deployment: use PORT env variable and simplify config"
git push
```

### Step 2: Railway Will Auto-Deploy
Railway should automatically detect the push and redeploy.

### Step 3: Verify Deployment
Wait 2-3 minutes, then test:

```bash
# Test AgentCard
curl https://a2atest-production.up.railway.app/.well-known/agent.json

# Should return agent metadata with skills
```

### Step 4: Test Agent Functionality
```bash
curl -X POST https://a2atest-production.up.railway.app \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Send email to test@example.com with subject Test"}]
      }
    },
    "id": "test-123"
  }'
```

## Alternative: Manual Railway Configuration

If auto-deploy doesn't work, configure in Railway dashboard:

1. **Settings → Deploy**
   - Start Command: `cd email-agent && python __main__.py`
   - Build Command: (leave empty, Nixpacks handles it)

2. **Settings → Environment**
   - Verify `PORT` is set (Railway sets this automatically)
   - Verify `RAILWAY_PUBLIC_DOMAIN` is set

3. **Settings → Networking**
   - Ensure public networking is enabled
   - Note the public domain

## Verification Checklist

- [ ] Code changes committed and pushed
- [ ] Railway shows "Deployed" status (not "Deploying")
- [ ] Logs show: `Uvicorn running on http://0.0.0.0:XXXX` (where XXXX is Railway's PORT)
- [ ] Logs show: `Deployed on Railway: https://a2atest-production.up.railway.app`
- [ ] AgentCard endpoint returns 200 OK with JSON
- [ ] Can invoke agent skills via JSON-RPC

## Common Issues

### Issue: Still getting 404
**Solution**: Check Railway logs for the actual PORT being used. The app must bind to `0.0.0.0:$PORT`

### Issue: Module not found errors
**Solution**: Ensure `requirements.txt` is at the root level where Railway can find it

### Issue: Agent starts but immediately crashes
**Solution**: Check Railway logs for Python errors. May need to add missing dependencies.

## Files Changed

1. ✅ `email-agent/__main__.py` - Added PORT and RAILWAY_PUBLIC_DOMAIN support
2. ✅ `Procfile` - Created at root with correct start command
3. ✅ Removed: `railway.json`, `main.py`, `email-agent/railway.toml`, `email-agent/Procfile`

## Expected Behavior After Fix

```
📧 Email Agent (Remote SaaS) starting on https://a2atest-production.up.railway.app
📋 AgentCard: https://a2atest-production.up.railway.app/.well-known/agent.json
✨ This agent simulates a remote SaaS email service
🚀 Deployed on Railway: https://a2atest-production.up.railway.app
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
```

Note: Port will be whatever Railway assigns (usually 3000), not 5004.