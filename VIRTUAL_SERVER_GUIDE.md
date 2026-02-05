# Virtual Server Configuration Guide

## Overview
The orchestrator can now query agents from a **specific virtual server** instead of all agents. This provides domain isolation and better scalability.

## How It Works

### Current Behavior (Default)
✅ **Orchestrator queries virtual server endpoint**
```
GET /servers/travel-suite/agents
```
- Only discovers agents in "travel-suite" virtual server
- Faster discovery (fewer agents)
- Domain-specific routing

### Fallback Behavior
If you set `use_virtual_server=False`, it queries all agents:
```
GET /a2a
```
- Discovers ALL registered agents
- Slower discovery (more agents)
- No domain filtering

## Configuration

### Method 1: Environment Variable (Recommended)
Set the virtual server name via environment variable:

```bash
export VIRTUAL_SERVER="travel-suite"
export TOKEN="your-jwt-token"
```

Then run the orchestrator - it will automatically use the virtual server endpoint.

### Method 2: Code Configuration
Edit `orchestrator/orchestrator.py`:

```python
# Line 11: Change the default virtual server
VIRTUAL_SERVER_NAME = os.getenv("VIRTUAL_SERVER", "travel-suite")  # Change "travel-suite" to your server name
```

### Method 3: Disable Virtual Server (Use All Agents)
To query all agents instead of a specific virtual server:

```python
# When calling discover_agents()
await orchestrator.discover_agents(use_virtual_server=False)
```

## Testing the Configuration

### Test 1: Verify Virtual Server Endpoint is Used
```bash
# Set environment
export VIRTUAL_SERVER="travel-suite"
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

# Run orchestrator
cd orchestrator
python orchestrator.py
```

**Expected Output:**
```
🔍 Discovering agents from Context Forge...
   Using virtual server: travel-suite
✅ Found 3 registered agents
```

### Test 2: Verify All Agents Endpoint (Fallback)
```bash
# Unset virtual server
unset VIRTUAL_SERVER

# Run orchestrator
python orchestrator.py
```

**Expected Output:**
```
🔍 Discovering agents from Context Forge...
   Using all agents endpoint
✅ Found 3 registered agents
```

## Streamlit UI Integration

The Streamlit UI automatically uses the orchestrator's configuration. When you refresh the browser:

1. UI calls `orchestrator.discover_agents()`
2. Orchestrator checks `VIRTUAL_SERVER` environment variable
3. If set, queries `/servers/{VIRTUAL_SERVER}/agents`
4. If not set, queries `/a2a` (all agents)

## Creating Multiple Virtual Servers

### Step 1: Create Virtual Servers in Context Forge

**Travel Suite:**
```bash
curl -X POST http://localhost:4444/servers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": {
      "name": "travel-suite",
      "description": "Travel planning agents",
      "associated_a2a_agents": ["weather_agent_id", "travel_agent_id"]
    }
  }'
```

**Finance Suite:**
```bash
curl -X POST http://localhost:4444/servers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": {
      "name": "finance-suite",
      "description": "Financial services agents",
      "associated_a2a_agents": ["calculator_agent_id", "stock_agent_id"]
    }
  }'
```

### Step 2: Switch Between Virtual Servers

**For Travel Queries:**
```bash
export VIRTUAL_SERVER="travel-suite"
streamlit run ui/streamlit_app.py
```

**For Finance Queries:**
```bash
export VIRTUAL_SERVER="finance-suite"
streamlit run ui/streamlit_app.py
```

## Benefits of Virtual Server Approach

### 1. Domain Isolation
- Travel queries only see travel agents
- Finance queries only see finance agents
- Healthcare queries only see healthcare agents

### 2. Faster Discovery
- Fewer agents to query = faster startup
- Reduced network overhead
- Better performance at scale

### 3. Multi-Tenancy
- Different tenants can have their own virtual servers
- Isolated agent pools per customer
- Better security and data separation

### 4. Environment Separation
- Production virtual server: `prod-agents`
- Staging virtual server: `staging-agents`
- Development virtual server: `dev-agents`

## Troubleshooting

### Issue: "Failed to fetch agents: 404"
**Cause:** Virtual server doesn't exist or wrong name

**Solution:**
1. Check virtual server name: `echo $VIRTUAL_SERVER`
2. List available servers in Context Forge admin UI
3. Verify server name matches exactly (case-sensitive)

### Issue: "Found 0 registered agents"
**Cause:** Virtual server has no associated agents

**Solution:**
1. Go to Context Forge admin: http://localhost:4444/admin
2. Click on your virtual server
3. Add agents to the virtual server
4. Refresh orchestrator

### Issue: Still querying all agents
**Cause:** Environment variable not set or code not updated

**Solution:**
1. Verify: `echo $VIRTUAL_SERVER` (should show server name)
2. Check orchestrator output for "Using virtual server: ..."
3. If shows "Using all agents endpoint", set VIRTUAL_SERVER

## Summary

**Current Implementation:**
- ✅ Orchestrator supports virtual server endpoint
- ✅ Configurable via `VIRTUAL_SERVER` environment variable
- ✅ Falls back to all agents if not configured
- ✅ Streamlit UI automatically uses orchestrator configuration

**To Use Virtual Server:**
```bash
export VIRTUAL_SERVER="travel-suite"
```

**To Use All Agents:**
```bash
unset VIRTUAL_SERVER
# OR
export VIRTUAL_SERVER=""
```

That's it! The orchestrator will now query only agents from your specified virtual server.