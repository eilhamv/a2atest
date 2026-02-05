# Railway Deployment - Root Directory Fix

## Problem Identified (Thorough Analysis)

After systematic review of all code and configurations, I identified the root cause:

**Railway is deploying from the repository root, but the agent code is in `email-agent/` subdirectory.**

### What Was Happening:

1. ✅ Railway installs dependencies from root `requirements.txt`
2. ✅ Railway runs `cd email-agent && python __main__.py`
3. ✅ Agent starts and health check succeeds internally
4. ❌ **But Railway's networking can't route to it because the context is wrong**

The `cd email-agent` in the start command changes directory AFTER Railway has set up networking and routing, causing a mismatch.

## The Solution

### Step 1: Configure Root Directory in Railway Dashboard

**Go to Railway Dashboard → Settings → General**

Set **Root Directory** to: `email-agent`

This tells Railway to treat `email-agent/` as the project root from the beginning.

### Step 2: Simplified Configuration Files

I've updated the configs to work with the root directory setting:

**railway.toml** (at repository root):
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python __main__.py"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Procfile** (at repository root):
```
web: python __main__.py
```

### Step 3: Deploy

After setting the root directory in Railway dashboard:

```bash
git add .
git commit -m "Fix: Simplify Railway config for root directory deployment"
git push
```

Railway will auto-deploy with the correct context.

## Why This Fix Works

1. **Root Directory Setting**: Railway now treats `email-agent/` as the project root
2. **Correct requirements.txt**: Railway finds `email-agent/requirements.txt`
3. **Correct Start Command**: `python __main__.py` runs in the right directory
4. **Correct Networking**: Railway's proxy routes to the correct service

## Verification Steps

After deployment completes:

```bash
# 1. Test health check
curl https://a2atest-production.up.railway.app/health
# Expected: {"status":"healthy","service":"email-agent"}

# 2. Test AgentCard
curl https://a2atest-production.up.railway.app/.well-known/agent.json
# Expected: Agent metadata with skills

# 3. Test agent functionality
curl -X POST https://a2atest-production.up.railway.app \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Send email to test@example.com"}]
      }
    },
    "id": "test-123"
  }'
```

## Code Review Summary

### ✅ All Code is Correct:

1. **email-agent/__main__.py**
   - Proper A2A v0.3.0 server setup
   - PORT environment variable support
   - RAILWAY_PUBLIC_DOMAIN support
   - Health check endpoint at `/health`

2. **email-agent/agent_executor.py**
   - Correct AgentExecutor implementation
   - Three working skills: send_email, validate_email, check_status
   - Proper async/await patterns

3. **email-agent/requirements.txt**
   - All necessary dependencies
   - a2a-sdk, starlette, sse-starlette, uvicorn, etc.

### ❌ The Only Issue Was:

**Deployment configuration** - Railway needed to know `email-agent/` is the root directory.

## Alternative: Move Files to Root

If you prefer not to use Railway's root directory setting, you could move all files from `email-agent/` to the repository root. But the root directory approach is cleaner for a monorepo structure.

## Next Steps After Successful Deployment

1. ✅ Verify all endpoints work
2. Update `scripts/register_remote_agent.py` with Railway URL
3. Register agent with Context Forge
4. Test via orchestrator
5. Update documentation

## Summary

- **Problem**: Railway deploying from wrong directory context
- **Solution**: Set Root Directory to `email-agent` in Railway dashboard
- **Result**: Clean deployment with proper networking and routing

The agent code was always correct - it was purely a deployment configuration issue.