# Email Agent - Remote SaaS A2A Agent

A mock email service agent demonstrating **remote SaaS agent** integration with Context Forge. This agent is fully A2A v0.3.0 compliant and can be deployed to Railway.app as a free remote service.

## 🎯 Purpose

This agent showcases how Context Forge can act as a registry for **both local and remote agents**:
- **Local agents**: Running on localhost (weather, calculator, travel)
- **Remote agents**: Deployed to cloud platforms (this email agent)

## 📋 Features

### Skills

1. **Send Email** (`send_email`)
   - Send emails with recipient, subject, and message
   - Example: "Send email to john@example.com with subject Hello and message Hi there"

2. **Validate Email** (`validate_email`)
   - Validate email address format
   - Check domain validity
   - Example: "Validate email john@example.com"

3. **Check Email Status** (`check_email_status`)
   - Track email delivery status
   - View recent sent emails
   - Example: "Check status email_abc12345"

## 🚀 Local Testing

### Prerequisites
- Python 3.8+
- Conda environment: `mcpdemo`

### Run Locally

```bash
# Activate conda environment
conda activate mcpdemo

# Navigate to email-agent directory
cd email-agent

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the agent
python -m email-agent
```

The agent will start on **http://localhost:5004**

### Test the Agent

```bash
# Check AgentCard
curl http://localhost:5004/.well-known/agent.json

# Send a test message
curl -X POST http://localhost:5004 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Send email to test@example.com with subject Test and message Hello World"}],
        "messageId": "test-123"
      }
    },
    "id": "req-123"
  }'
```

## ☁️ Deploy to Railway.app (Free)

### Step 1: Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub (free tier: 500 hours/month)

### Step 2: Deploy from GitHub

#### Option A: Deploy via Railway Dashboard
1. Push this `email-agent` directory to a GitHub repository
2. In Railway dashboard, click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Python and deploy

#### Option B: Deploy via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd email-agent
railway init

# Deploy
railway up
```

### Step 3: Get Your Public URL

After deployment, Railway will provide a public URL like:
```
https://email-agent-production-xxxx.up.railway.app
```

### Step 4: Update AgentCard URL

Edit `__main__.py` and update the URL:
```python
agent_card = AgentCard(
    name='email_agent',
    version='1.0.0',
    description='Remote SaaS email service agent',
    url='https://email-agent-production-xxxx.up.railway.app',  # ← Update this
    protocolVersion='0.3.0',
    # ... rest of config
)
```

Redeploy after updating.

## 📝 Register with Context Forge

Once deployed, register the remote agent:

```bash
# Set your Context Forge token
export TOKEN='your-jwt-token'

# Register the remote agent
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

Or use the updated registration script (see main README).

## 🔧 Configuration

### Environment Variables (Optional)

For production deployment, you can add environment variables in Railway:

```bash
# Railway dashboard > Variables
PORT=5004
LOG_LEVEL=info
```

### Port Configuration

Railway automatically assigns a port via the `PORT` environment variable. Update `__main__.py` if needed:

```python
import os
port = int(os.getenv('PORT', 5004))
uvicorn.run(server.build(), host='0.0.0.0', port=port)
```

## 🧪 Testing Remote Agent

Once deployed and registered:

```bash
# Test via orchestrator
cd ../orchestrator
python orchestrator.py

# Query the remote agent
Query> Send email to john@example.com with subject Test and message Hello from remote agent
```

The orchestrator will:
1. Discover the remote agent from Context Forge
2. Fetch its AgentCard from Railway URL
3. Route the query to the remote agent
4. Display the response

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Context Forge (localhost:4444)              │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Local Agents    │      │  Remote Agents   │        │
│  │  - Weather       │      │  - Email (SaaS)  │        │
│  │  - Calculator    │      │    Railway.app   │        │
│  │  - Travel        │      │                  │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
                    ▲
                    │
            ┌───────┴────────┐
            │  Orchestrator  │
            └────────────────┘
```

## 🎯 Key Benefits

1. **True Remote Agent**: Deployed to cloud, not localhost
2. **A2A Protocol**: Full compliance with A2A v0.3.0
3. **Free Hosting**: Railway.app free tier
4. **Same Interface**: Orchestrator treats local and remote agents identically
5. **Registry Demo**: Shows Context Forge managing hybrid architecture

## 🐛 Troubleshooting

### Agent Not Starting Locally
```bash
# Check if port 5004 is in use
lsof -i :5004

# Kill existing process
kill -9 <PID>
```

### Railway Deployment Issues
```bash
# Check Railway logs
railway logs

# Redeploy
railway up --detach
```

### AgentCard Not Accessible
- Ensure Railway service is running
- Check the public URL is correct
- Verify no authentication blocking the endpoint

## 📚 Resources

- [A2A Protocol](https://a2a-protocol.org/)
- [Railway.app Docs](https://docs.railway.app/)
- [Context Forge Documentation](../MCP_GATEWAY_GUIDE.md)

## 🤝 Integration

This agent integrates seamlessly with the existing A2A orchestrator system. See the main [README.md](../README.md) for complete system documentation.

---

**Built with ❤️ using A2A Protocol v0.3.0 | Deployed on Railway.app**