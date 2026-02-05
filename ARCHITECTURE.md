# A2A Multi-Agent Orchestrator - Architecture Documentation

## 🎯 High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit UI<br/>Port 8501]
    end
    
    subgraph "Orchestration Layer"
        ORCH[Orchestrator<br/>Smart Routing Engine]
        ORCH_DISC[Discovery Module]
        ORCH_ROUTE[Routing Module]
        ORCH_EXEC[Execution Module]
    end
    
    subgraph "Registry Layer - Context Forge"
        CF[Context Forge<br/>MCP Gateway<br/>Port 4444]
        CF_REG[Agent Registry<br/>/a2a endpoint]
        CF_VS[Virtual Server Registry<br/>/servers endpoint]
    end
    
    subgraph "Virtual Server: travel-suite"
        VS[Virtual Server<br/>Logical Grouping]
    end
    
    subgraph "Agent Layer"
        WA[Weather Agent<br/>Port 5001]
        CA[Calculator Agent<br/>Port 5002]
        TA[Travel Agent<br/>Port 5003]
    end
    
    subgraph "A2A Protocol"
        AC1[AgentCard<br/>/.well-known/agent-card.json]
        AC2[AgentCard<br/>/.well-known/agent-card.json]
        AC3[AgentCard<br/>/.well-known/agent-card.json]
    end
    
    %% User Flow
    UI -->|1. User Query| ORCH
    
    %% Discovery Phase
    ORCH --> ORCH_DISC
    ORCH_DISC -->|2. GET /a2a<br/>Fetch all agents| CF_REG
    CF_REG -->|3. Return agent list| ORCH_DISC
    ORCH_DISC -->|4. GET /.well-known/agent-card.json| AC1
    ORCH_DISC -->|4. GET /.well-known/agent-card.json| AC2
    ORCH_DISC -->|4. GET /.well-known/agent-card.json| AC3
    AC1 -->|5. AgentCard with skills| ORCH_DISC
    AC2 -->|5. AgentCard with skills| ORCH_DISC
    AC3 -->|5. AgentCard with skills| ORCH_DISC
    
    %% Routing Phase
    ORCH_DISC --> ORCH_ROUTE
    ORCH_ROUTE -->|6. Match query to skills<br/>Keyword analysis| ORCH_ROUTE
    
    %% Execution Phase
    ORCH_ROUTE --> ORCH_EXEC
    ORCH_EXEC -->|7. JSON-RPC 2.0<br/>POST /| WA
    ORCH_EXEC -->|7. JSON-RPC 2.0<br/>POST /| CA
    ORCH_EXEC -->|7. JSON-RPC 2.0<br/>POST /| TA
    
    %% Response Flow
    WA -->|8. Response| ORCH_EXEC
    CA -->|8. Response| ORCH_EXEC
    TA -->|8. Response| ORCH_EXEC
    ORCH_EXEC -->|9. Aggregated Result| UI
    
    %% Virtual Server Association
    VS -.->|Associated with| WA
    VS -.->|Associated with| CA
    VS -.->|Associated with| TA
    CF_VS -.->|Manages| VS
    
    style UI fill:#e1f5ff
    style ORCH fill:#fff4e1
    style CF fill:#f0e1ff
    style VS fill:#e1ffe1
    style WA fill:#ffe1e1
    style CA fill:#ffe1e1
    style TA fill:#ffe1e1
```

## 📋 Detailed Flow Explanation

### Phase 1: Discovery (Lines 19-83 in orchestrator.py)

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant CF as Context Forge
    participant WA as Weather Agent
    participant CA as Calculator Agent
    participant TA as Travel Agent
    
    Note over O: Discovery Phase Starts
    O->>CF: GET /a2a (with Bearer token)
    CF-->>O: [weather_agent, calculator_agent, travel_agent]
    
    loop For each agent
        O->>WA: GET /.well-known/agent-card.json
        WA-->>O: AgentCard {skills: [get_weather, get_forecast, ...]}
        
        O->>CA: GET /.well-known/agent-card.json
        CA-->>O: AgentCard {skills: [calculate, convert_currency, ...]}
        
        O->>TA: GET /.well-known/agent-card.json
        TA-->>O: AgentCard {skills: [recommend_destination, ...]}
    end
    
    Note over O: Build skill index:<br/>{skill_id: agent_name}
```

**Key Points:**
- Orchestrator queries Context Forge's `/a2a` endpoint to get ALL registered agents
- For each agent, fetches AgentCard from `/.well-known/agent-card.json`
- Builds local cache: `{agent_name: {endpoint, skills, card}}`
- Creates skill index for fast lookup

### Phase 2: Query Routing (Lines 85-105 in orchestrator.py)

```mermaid
flowchart TD
    A[User Query:<br/>'Convert 100 USD to EUR'] --> B[Extract Keywords]
    B --> C{Filter Stop Words}
    C --> D[Keywords:<br/>convert, usd, eur]
    D --> E[Match Against<br/>Agent Keywords]
    
    E --> F{Weather Agent?}
    F -->|Keywords: weather,<br/>temperature, forecast| G[Score: 0]
    
    E --> H{Calculator Agent?}
    H -->|Keywords: convert,<br/>currency, usd, eur| I[Score: 40]
    
    E --> J{Travel Agent?}
    J -->|Keywords: travel,<br/>destination, trip| K[Score: 0]
    
    G --> L[Filter: Score > 5]
    I --> L
    K --> L
    
    L --> M[Matched Agents:<br/>calculator_agent only]
    
    style I fill:#90EE90
    style M fill:#90EE90
```

**Routing Algorithm:**
1. **Stop Word Filtering**: Remove common words (to, in, a, the, etc.)
2. **Keyword Extraction**: Extract meaningful words from query
3. **Agent-Specific Matching**: Check against predefined keyword dictionaries
4. **Skill Description Matching**: Match keywords in skill descriptions
5. **Scoring**: Assign scores based on match quality
6. **Filtering**: Only return agents with score > 5

### Phase 3: Execution (Lines 107-159 in orchestrator.py)

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant CA as Calculator Agent
    
    Note over O: Matched: calculator_agent
    O->>CA: POST / (JSON-RPC 2.0)
    Note over O,CA: {<br/>  "jsonrpc": "2.0",<br/>  "method": "message/send",<br/>  "params": {<br/>    "message": {<br/>      "role": "user",<br/>      "parts": [{"text": "Convert 100 USD to EUR"}]<br/>    }<br/>  }<br/>}
    
    CA->>CA: Process query
    CA-->>O: JSON-RPC Response
    Note over O,CA: {<br/>  "result": {<br/>    "parts": [{"text": "100.0 USD = 92.00 EUR"}]<br/>  }<br/>}
    
    O->>O: Extract text from response
    O-->>UI: "100.0 USD = 92.00 EUR"
```

## 🔄 Virtual Server Concept

### Current Setup: Single Virtual Server

```mermaid
graph TB
    subgraph "Context Forge Registry"
        CF[Context Forge]
        VS1[Virtual Server:<br/>travel-suite]
    end
    
    subgraph "Agents"
        WA[Weather Agent]
        CA[Calculator Agent]
        TA[Travel Agent]
    end
    
    CF -->|Manages| VS1
    VS1 -.->|Groups| WA
    VS1 -.->|Groups| CA
    VS1 -.->|Groups| TA
    
    style VS1 fill:#e1ffe1
```

**Current Behavior:**
- Orchestrator queries: `GET /a2a` → Returns ALL agents
- Virtual server "travel-suite" is a **logical grouping** only
- No filtering by virtual server in current implementation

### Multi-Virtual Server Architecture

```mermaid
graph TB
    subgraph "Context Forge Registry"
        CF[Context Forge]
        VS1[Virtual Server:<br/>travel-suite]
        VS2[Virtual Server:<br/>finance-suite]
        VS3[Virtual Server:<br/>healthcare-suite]
    end
    
    subgraph "Travel Agents"
        WA[Weather Agent]
        TA[Travel Agent]
        HA[Hotel Agent]
    end
    
    subgraph "Finance Agents"
        CA[Calculator Agent]
        SA[Stock Agent]
        BA[Banking Agent]
    end
    
    subgraph "Healthcare Agents"
        MA[Medical Agent]
        PA[Pharmacy Agent]
        AA[Appointment Agent]
    end
    
    CF -->|Manages| VS1
    CF -->|Manages| VS2
    CF -->|Manages| VS3
    
    VS1 -.->|Groups| WA
    VS1 -.->|Groups| TA
    VS1 -.->|Groups| HA
    
    VS2 -.->|Groups| CA
    VS2 -.->|Groups| SA
    VS2 -.->|Groups| BA
    
    VS3 -.->|Groups| MA
    VS3 -.->|Groups| PA
    VS3 -.->|Groups| AA
    
    style VS1 fill:#e1ffe1
    style VS2 fill:#ffe1e1
    style VS3 fill:#e1e1ff
```

### How to Use Virtual Servers

#### Option 1: Query Specific Virtual Server (Recommended)

**Modify orchestrator to query virtual server endpoint:**

```python
# Current (queries ALL agents):
response = await client.get(f"{CONTEXT_FORGE_URL}/a2a")

# Modified (queries specific virtual server):
VIRTUAL_SERVER_NAME = "travel-suite"
response = await client.get(
    f"{CONTEXT_FORGE_URL}/servers/{VIRTUAL_SERVER_NAME}/agents"
)
```

**Benefits:**
- ✅ Only discovers agents in that virtual server
- ✅ Faster discovery (fewer agents to query)
- ✅ Domain-specific routing (travel queries only go to travel agents)
- ✅ Better isolation between domains

#### Option 2: Filter After Discovery

```python
# Discover all agents
all_agents = await client.get(f"{CONTEXT_FORGE_URL}/a2a")

# Filter by virtual server
virtual_server_id = "travel-suite-id"
filtered_agents = [
    agent for agent in all_agents 
    if virtual_server_id in agent.get('virtual_servers', [])
]
```

### Virtual Server Use Cases

#### Use Case 1: Domain Isolation
```
travel-suite: Weather, Travel, Hotel agents
finance-suite: Calculator, Stock, Banking agents
healthcare-suite: Medical, Pharmacy, Appointment agents
```

**Query Flow:**
```
User: "What's the weather in Paris?"
→ Orchestrator queries: /servers/travel-suite/agents
→ Only discovers: Weather, Travel, Hotel agents
→ Routes to: Weather agent
```

#### Use Case 2: Multi-Tenant Architecture
```
tenant-acme-corp: Custom agents for Acme Corp
tenant-globex: Custom agents for Globex
tenant-initech: Custom agents for Initech
```

**Query Flow:**
```
User (Acme Corp): "Generate report"
→ Orchestrator queries: /servers/tenant-acme-corp/agents
→ Only discovers: Acme Corp's custom agents
→ Routes to: Acme's Report Generator agent
```

#### Use Case 3: Environment Separation
```
production-suite: Production-ready agents
staging-suite: Testing agents
development-suite: Development agents
```

## 🔧 Implementation Changes for Virtual Server Support

### Current Code (orchestrator/orchestrator.py):
```python
async def discover_agents(self):
    """Discover agents from Context Forge registry"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Gets ALL agents
        response = await client.get(
            f"{CONTEXT_FORGE_URL}/a2a",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
```

### Modified Code (with virtual server support):
```python
async def discover_agents(self, virtual_server_name=None):
    """Discover agents from Context Forge registry
    
    Args:
        virtual_server_name: Optional virtual server to query.
                           If None, queries all agents.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if virtual_server_name:
            # Query specific virtual server
            endpoint = f"{CONTEXT_FORGE_URL}/servers/{virtual_server_name}/agents"
        else:
            # Query all agents
            endpoint = f"{CONTEXT_FORGE_URL}/a2a"
        
        response = await client.get(
            endpoint,
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
```

### Usage:
```python
# Discover all agents (current behavior)
await orchestrator.discover_agents()

# Discover only travel-suite agents
await orchestrator.discover_agents(virtual_server_name="travel-suite")

# Discover only finance-suite agents
await orchestrator.discover_agents(virtual_server_name="finance-suite")
```

## 📊 System Components

### 1. Context Forge (MCP Gateway)
- **Port**: 4444
- **Role**: Central registry for agents and virtual servers
- **Endpoints**:
  - `GET /a2a` - List all agents
  - `POST /a2a` - Register new agent
  - `GET /servers` - List all virtual servers
  - `POST /servers` - Create virtual server
  - `GET /servers/{name}/agents` - Get agents in virtual server

### 2. Orchestrator
- **Role**: Discovery, routing, and execution coordinator
- **Key Functions**:
  - `discover_agents()` - Phase 1: Fetch agents and AgentCards
  - `match_query_to_skills()` - Phase 2: Smart routing
  - `invoke_agent()` - Phase 3: Execute agent calls

### 3. A2A Agents
- **Protocol**: A2A v0.3.0 (JSON-RPC 2.0)
- **Required Endpoints**:
  - `GET /.well-known/agent-card.json` - AgentCard
  - `POST /` - Message handling (JSON-RPC)

### 4. Streamlit UI
- **Port**: 8501
- **Features**:
  - Query interface with smart routing
  - Agent dashboard with metrics
  - Example queries for testing

## 🎯 Key Takeaways

1. **Virtual Servers are Logical Groupings**: They don't change agent behavior, just how they're discovered
2. **Current Implementation**: Queries ALL agents via `/a2a` endpoint
3. **Virtual Server Support**: Would query specific endpoint `/servers/{name}/agents`
4. **Smart Routing**: Happens AFTER discovery, filters agents based on query keywords
5. **Scalability**: Virtual servers enable domain isolation and multi-tenancy

## 🚀 Next Steps for Virtual Server Support

To fully leverage virtual servers:

1. **Add virtual_server_name parameter** to orchestrator
2. **Modify discovery endpoint** to use `/servers/{name}/agents`
3. **Update Streamlit UI** to allow virtual server selection
4. **Create multiple virtual servers** for different domains
5. **Test cross-domain isolation** to ensure proper filtering