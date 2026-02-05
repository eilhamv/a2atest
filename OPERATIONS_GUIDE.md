# A2A Multi-Agent Orchestrator - Operations Guide

Complete guide for starting, stopping, and managing the A2A Multi-Agent Orchestrator system.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Components](#system-components)
3. [Starting the System](#starting-the-system)
4. [Stopping the System](#stopping-the-system)
5. [Individual Component Management](#individual-component-management)
6. [Troubleshooting](#troubleshooting)
7. [Configuration](#configuration)
8. [Logs and Monitoring](#logs-and-monitoring)

---

## 🚀 Quick Start

### Start Everything
```bash
cd /Users/harishankar/Downloads/a2a
bash scripts/start_system.sh
```

### Stop Everything
```bash
bash scripts/stop_all.sh
```

### Access the System
- **Streamlit UI**: http://localhost:8501
- **Context Forge Admin**: http://localhost:4444/admin
- **Context Forge API**: http://localhost:4444

---

## 🏗️ System Components

The system consists of 5 main components:

| Component | Port | Description |
|-----------|------|-------------|
| **Context Forge** | 4444 | Central registry and MCP Gateway |
| **Weather Agent** | 5001 | Provides weather information |
| **Calculator Agent** | 5002 | Performs calculations and conversions |
| **Travel Agent** | 5003 | Travel recommendations and tips |
| **Streamlit UI** | 8501 | User interface for queries |

---

## ▶️ Starting the System

### Option 1: Start Everything (Recommended)

```bash
# Navigate to project directory
cd /Users/harishankar/Downloads/a2a

# Create logs directory if it doesn't exist
mkdir -p logs

# Start all services
bash scripts/start_system.sh
```

**What this does:**
1. Activates conda environment (`mcpdemo`)
2. Starts Context Forge (if not running)
3. Gets authentication token
4. Sets virtual server configuration
5. Starts all 3 agents
6. Starts Streamlit UI
7. Displays access URLs and status

**Expected Output:**
```
🚀 Starting A2A Multi-Agent Orchestrator System...

✅ Context Forge started on http://localhost:4444
🔐 Getting authentication token...
✅ Authentication successful
🎯 Virtual server filtering: travel-suite
✅ Agents started:
   - Weather Agent: http://localhost:5001
   - Calculator Agent: http://localhost:5002
   - Travel Agent: http://localhost:5003
✅ Streamlit UI started on http://localhost:8501

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ System started successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Option 2: Start Components Individually

See [Individual Component Management](#individual-component-management) section below.

---

## ⏹️ Stopping the System

### Stop Everything

```bash
bash scripts/stop_all.sh
```

**What this does:**
1. Stops Streamlit UI
2. Stops all agents
3. Stops Context Forge
4. Stops orchestrator (if running)

**Expected Output:**
```
🛑 Stopping A2A Multi-Agent Orchestrator System...

Stopping Streamlit UI...
✅ Streamlit stopped
Stopping agents...
✅ Agents stopped
Stopping Context Forge...
✅ Context Forge stopped
Stopping orchestrator...
ℹ️  Orchestrator not running

✅ All services stopped!
```

---

## 🔧 Individual Component Management

### 1. Context Forge (MCP Gateway)

**Start:**
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
mcpgateway mcpgateway.main:app
```

**Stop:**
```bash
pkill -f "mcpgateway"
```

**Check Status:**
```bash
curl http://localhost:4444/health
```

**Access Admin Panel:**
```
http://localhost:4444/admin
Username: admin@example.com
Password: mvhari123
```

---

### 2. Weather Agent

**Start:**
```bash
cd weather-agent
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 __main__.py
```

**Stop:**
```bash
pkill -f "python3 __main__.py"
```

**Test:**
```bash
curl http://localhost:5001/.well-known/agent-card.json
```

---

### 3. Calculator Agent

**Start:**
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 agents/calculator_agent.py
```

**Stop:**
```bash
pkill -f "calculator_agent.py"
```

**Test:**
```bash
curl http://localhost:5002/.well-known/agent-card.json
```

---

### 4. Travel Agent

**Start:**
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 agents/travel_agent.py
```

**Stop:**
```bash
pkill -f "travel_agent.py"
```

**Test:**
```bash
curl http://localhost:5003/.well-known/agent-card.json
```

---

### 5. Streamlit UI

**Start:**
```bash
# Get authentication token first
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

# Optional: Set virtual server
export VIRTUAL_SERVER="travel-suite"

# Start Streamlit
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
streamlit run ui/streamlit_app.py --server.port 8501
```

**Stop:**
```bash
pkill -f "streamlit run"
```

**Access:**
```
http://localhost:8501
```

---

## 🔍 Troubleshooting

### Problem: "Port already in use"

**Solution:**
```bash
# Find process using the port (e.g., 4444)
lsof -i :4444

# Kill the process
kill -9 <PID>

# Or use the stop script
bash scripts/stop_all.sh
```

---

### Problem: "Authentication failed" or "401 Unauthorized"

**Solution:**
```bash
# Get a fresh token
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

# Verify token
echo $TOKEN
```

---

### Problem: "No agents found"

**Solution:**
```bash
# 1. Check if agents are running
ps aux | grep -E "(weather|calculator|travel)_agent"

# 2. Check if agents are registered
curl -H "Authorization: Bearer $TOKEN" http://localhost:4444/a2a

# 3. Re-register agents if needed
python3 scripts/register_agents.py
```

---

### Problem: "Virtual server not found"

**Solution:**
```bash
# 1. Check available virtual servers
curl -H "Authorization: Bearer $TOKEN" http://localhost:4444/servers

# 2. Create virtual server if missing
python3 scripts/create_virtual_server.py

# 3. Or disable virtual server filtering
unset VIRTUAL_SERVER
```

---

### Problem: Agents not responding

**Solution:**
```bash
# 1. Check agent logs
tail -f logs/agents.log

# 2. Test agent directly
curl http://localhost:5001/.well-known/agent-card.json

# 3. Restart agents
bash scripts/stop_all.sh
bash scripts/start_all_agents.sh
```

---

## ⚙️ Configuration

### Virtual Server Filtering

**Enable (default):**
```bash
export VIRTUAL_SERVER="travel-suite"
```

**Disable:**
```bash
unset VIRTUAL_SERVER
# or
export VIRTUAL_SERVER=""
```

**Change virtual server:**
```bash
export VIRTUAL_SERVER="your-server-name"
```

---

### Authentication

**Default credentials:**
- Email: `admin@example.com`
- Password: `mvhari123`

**Get token programmatically:**
```bash
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')
```

---

### Environment Variables

Create a `.env` file or export these variables:

```bash
# Context Forge
export CONTEXT_FORGE_URL="http://localhost:4444"
export TOKEN="your-jwt-token"

# Virtual Server (optional)
export VIRTUAL_SERVER="travel-suite"

# Agent Ports (optional, defaults shown)
export WEATHER_AGENT_PORT=5001
export CALCULATOR_AGENT_PORT=5002
export TRAVEL_AGENT_PORT=5003

# Streamlit (optional)
export STREAMLIT_PORT=8501
```

---

## 📊 Logs and Monitoring

### Log Files

All logs are stored in the `logs/` directory:

```bash
# Create logs directory
mkdir -p logs

# View Context Forge logs
tail -f logs/context_forge.log

# View agent logs
tail -f logs/agents.log

# View Streamlit logs
tail -f logs/streamlit.log
```

---

### Check System Status

```bash
# Check all running processes
ps aux | grep -E "(mcpgateway|streamlit|agent)" | grep -v grep

# Check specific ports
lsof -i :4444  # Context Forge
lsof -i :5001  # Weather Agent
lsof -i :5002  # Calculator Agent
lsof -i :5003  # Travel Agent
lsof -i :8501  # Streamlit UI
```

---

### Health Checks

```bash
# Context Forge
curl http://localhost:4444/health

# Weather Agent
curl http://localhost:5001/.well-known/agent-card.json

# Calculator Agent
curl http://localhost:5002/.well-known/agent-card.json

# Travel Agent
curl http://localhost:5003/.well-known/agent-card.json

# Streamlit (check if page loads)
curl -I http://localhost:8501
```

---

## 🔄 Common Workflows

### Daily Startup

```bash
cd /Users/harishankar/Downloads/a2a
bash scripts/start_system.sh
# Open browser to http://localhost:8501
```

---

### Daily Shutdown

```bash
bash scripts/stop_all.sh
```

---

### Restart After Changes

```bash
# Stop everything
bash scripts/stop_all.sh

# Wait a moment
sleep 2

# Start everything
bash scripts/start_system.sh
```

---

### Test a Single Query

```bash
# Start system
bash scripts/start_system.sh

# Open Streamlit UI
open http://localhost:8501

# Or use orchestrator directly
cd orchestrator
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')
python3 orchestrator.py
```

---

## 📚 Additional Resources

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Virtual Server Guide**: See [VIRTUAL_SERVER_GUIDE.md](VIRTUAL_SERVER_GUIDE.md)
- **Implementation Details**: See [VIRTUAL_SERVER_IMPLEMENTATION.md](VIRTUAL_SERVER_IMPLEMENTATION.md)
- **Main README**: See [README.md](README.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the logs in `logs/` directory
2. Review the troubleshooting section above
3. Verify all services are running: `ps aux | grep -E "(mcpgateway|streamlit|agent)"`
4. Check port availability: `lsof -i :<port>`
5. Restart the system: `bash scripts/stop_all.sh && bash scripts/start_system.sh`

---

## 📝 Quick Reference

```bash
# Start system
bash scripts/start_system.sh

# Stop system
bash scripts/stop_all.sh

# View logs
tail -f logs/*.log

# Check status
ps aux | grep -E "(mcpgateway|streamlit|agent)" | grep -v grep

# Get token
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

# Access UI
open http://localhost:8501
```

---

**Last Updated**: 2026-02-02