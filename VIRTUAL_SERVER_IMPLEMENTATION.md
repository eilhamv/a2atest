# Virtual Server Implementation - Complete Guide

## Overview

The A2A Multi-Agent Orchestrator now supports **virtual server filtering**, allowing you to query agents from a specific logical grouping in Context Forge rather than all registered agents.

## What is a Virtual Server?

A **virtual server** in Context Forge is a logical grouping of A2A agents, similar to how MCP servers group tools. It allows you to:
- Organize agents by domain (e.g., "travel-suite", "finance-suite")
- Query only relevant agents for specific use cases
- Manage agent collections independently

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Context Forge                            │
│  ┌────────────────┐         ┌──────────────────┐           │
│  │  /a2a endpoint │         │ /servers endpoint│           │
│  │  (all agents)  │         │ (virtual servers)│           │
│  └────────────────┘         └──────────────────┘           │
│         │                            │                       │
│         │                            │                       │
│         ▼                            ▼                       │
│  [agent1, agent2,           [server: {                      │
│   agent3, agent4]            name: "travel-suite",          │
│                              associatedA2aAgents: [          │
│                                agent1_id,                    │
│                                agent2_id,                    │
│                                agent3_id                     │
│                              ]}]                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Client-side filtering
                              ▼
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │                  │
                    │ 1. Fetch all     │
                    │    agents        │
                    │ 2. Fetch virtual │
                    │    server        │
                    │ 3. Filter by IDs │
                    └──────────────────┘
```

### Key Changes

#### 1. Dynamic Token Reading
**File**: `orchestrator/orchestrator.py`

Changed from static token loading to dynamic:
```python
# Before
BEARER_TOKEN = os.getenv("TOKEN")

# After
def get_bearer_token():
    """Get bearer token from environment (read dynamically)"""
    return os.getenv("TOKEN")
```

This allows the token to be set after module import, which is essential for testing.

#### 2. Virtual Server Filtering Logic
**File**: `orchestrator/orchestrator.py` (lines 20-69)

The `discover_agents()` method now:
1. Fetches all agents from `/a2a`
2. If virtual server is configured:
   - Fetches virtual servers from `/servers`
   - Finds the target server by name
   - Filters agents by matching IDs in `associatedA2aAgents`
3. Falls back to all agents if virtual server not found

```python
async def discover_agents(self, use_virtual_server=True):
    # Fetch all agents
    all_agents = response.json()
    
    # Filter by virtual server if configured
    if use_virtual_server and VIRTUAL_SERVER_NAME:
        servers_response = await client.get(f"{CONTEXT_FORGE_URL}/servers")
        servers = servers_response.json()
        target_server = next((s for s in servers if s['name'] == VIRTUAL_SERVER_NAME), None)
        
        if target_server and 'associatedA2aAgents' in target_server:
            associated_ids = set(target_server['associatedA2aAgents'])
            registered_agents = [a for a in all_agents if a.get('id') in associated_ids]
```

## Configuration

### Method 1: Environment Variable (Recommended)
```bash
export VIRTUAL_SERVER="travel-suite"
export TOKEN="your-jwt-token"
python orchestrator/orchestrator.py
```

### Method 2: In Code
```python
# orchestrator/orchestrator.py
VIRTUAL_SERVER_NAME = "travel-suite"  # Change this line
```

### Method 3: Disable Virtual Server Filtering
```bash
unset VIRTUAL_SERVER
# or
export VIRTUAL_SERVER=""
```

## Testing

### Test Script
**File**: `scripts/test_virtual_server.py`

This script tests both modes:
1. **With virtual server filtering**: Queries only agents in "travel-suite"
2. **Without virtual server filtering**: Queries all agents

Run the test:
```bash
python3 scripts/test_virtual_server.py
```

### Expected Output
```
============================================================
Testing Virtual Server Filtering
============================================================

🔐 Authenticating with Context Forge...
✅ Authentication successful

🧪 TEST 1: With Virtual Server Filtering (travel-suite)
------------------------------------------------------------
🔍 Discovering agents from Context Forge...
   Filtering by virtual server: travel-suite
   ✅ Found 3 agents in virtual server
✅ Discovered 3 agents total

Discovered agents: ['travel_agent', 'calculator_agent', 'weather_agent']
Total agents: 3

🧪 TEST 2: Without Virtual Server Filtering (all agents)
------------------------------------------------------------
🔍 Discovering agents from Context Forge...
   Using all agents
✅ Discovered 3 agents total

Discovered agents: ['travel_agent', 'calculator_agent', 'weather_agent']
Total agents: 3
```

## Virtual Server Data Structure

### Context Forge Response
```json
{
  "id": "e619bba24407430089cffb2c1e2430f5",
  "name": "travel-suite",
  "description": "Travel planning agent collection",
  "associatedA2aAgents": [
    "78a0289ac10b4104893176642e64eadb",  // weather_agent
    "a30a0ddaed4a45a5a62ef6700bad141b",  // calculator_agent
    "b6403f074ee44fd689dcfe3f74623a82"   // travel_agent
  ],
  "createdAt": "2026-01-29T18:03:58.000Z",
  "updatedAt": "2026-01-29T18:03:58.000Z"
}
```

## Use Cases

### 1. Domain-Specific Queries
```bash
# Travel domain
export VIRTUAL_SERVER="travel-suite"
# Queries only: weather_agent, calculator_agent, travel_agent

# Finance domain
export VIRTUAL_SERVER="finance-suite"
# Queries only: stock_agent, currency_agent, tax_agent
```

### 2. Multi-Tenant Systems
```bash
# Customer A's agents
export VIRTUAL_SERVER="customer-a-agents"

# Customer B's agents
export VIRTUAL_SERVER="customer-b-agents"
```

### 3. Development vs Production
```bash
# Development agents
export VIRTUAL_SERVER="dev-agents"

# Production agents
export VIRTUAL_SERVER="prod-agents"
```

## Troubleshooting

### Issue: "Virtual server not found"
**Cause**: The virtual server name doesn't exist in Context Forge

**Solution**:
1. Check available virtual servers:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" http://localhost:4444/servers
   ```
2. Verify the name matches exactly (case-sensitive)
3. Create the virtual server if needed:
   ```bash
   python scripts/create_virtual_server.py
   ```

### Issue: "No agents found in virtual server"
**Cause**: The virtual server has no associated agents

**Solution**:
1. Check the virtual server's `associatedA2aAgents` array
2. Register agents with the virtual server:
   ```bash
   python scripts/register_agents.py
   ```

### Issue: "401 Unauthorized"
**Cause**: Invalid or missing authentication token

**Solution**:
1. Get a fresh token:
   ```bash
   export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')
   ```

## Benefits

1. **Performance**: Query only relevant agents, reducing discovery time
2. **Organization**: Logical grouping of agents by domain/purpose
3. **Security**: Isolate agent collections for different users/teams
4. **Flexibility**: Easy to switch between virtual servers or disable filtering
5. **Scalability**: As agent count grows, virtual servers keep queries efficient

## Future Enhancements

1. **Multi-Virtual Server Support**: Query multiple virtual servers simultaneously
2. **Dynamic Virtual Server Selection**: Choose virtual server based on query intent
3. **Virtual Server Caching**: Cache virtual server metadata for faster lookups
4. **Virtual Server Hierarchies**: Support nested virtual servers (parent/child relationships)

## Related Documentation

- [VIRTUAL_SERVER_GUIDE.md](VIRTUAL_SERVER_GUIDE.md) - User guide for virtual server configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [README.md](README.md) - Project setup and usage

## Summary

The virtual server implementation provides a powerful way to organize and query A2A agents in Context Forge. By filtering agents at the orchestrator level, we maintain flexibility while improving performance and organization. The implementation uses client-side filtering since Context Forge doesn't provide a direct `/servers/{name}/agents` endpoint, but this approach works efficiently and provides the same benefits.