# A2A Multi-Agent Orchestrator System

A complete Agent-to-Agent (A2A) multi-agent orchestrator system with Context Forge integration, featuring **local and remote agents** to demonstrate hybrid architecture.

## 🏗️ System Architecture - Hybrid Local + Remote

```
┌──────────────────────────────────────────────────────────────────┐
│                  Context Forge (MCP Gateway)                      │
│                   http://localhost:4444                           │
│                                                                   │
│  ┌─────────────────────────────┐  ┌────────────────────────┐   │
│  │  LOCAL AGENTS               │  │  REMOTE AGENTS (SaaS)  │   │
│  │  Virtual Server: travel     │  │                        │   │
│  │  ┌────────┬────────┬─────┐ │  │  ┌──────────────────┐ │   │
│  │  │Weather │Calc    │Travel│ │  │  │  Email Agent     │ │   │
│  │  │:5001   │:5002   │:5003 │ │  │  │  Railway.app     │ │   │
│  │  └────────┴────────┴─────┘ │  │  │  (Cloud Hosted)  │ │   │
│  └─────────────────────────────┘  │  └──────────────────┘ │   │
│                                    │                        │   │
└──────────────────────────────────────────────────────────────────┘
                            ▲
                            │
                    ┌───────┴────────┐
                    │  Orchestrator  │
                    │  Smart Routing │
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │  Streamlit UI  │
                    │   Port 8501    │
                    └────────────────┘
```

## 🌟 Key Feature: Hybrid Agent Registry

Context Forge acts as a **unified registry** for both:
- **Local Agents**: Running on localhost (Weather, Calculator, Travel)
- **Remote Agents**: Deployed to cloud platforms (Email Agent on Railway.app)

The orchestrator treats both types identically using the A2A protocol!

## 📋 Components

### 1. **Local A2A Agents** (localhost)

#### Weather Agent (Port 5001)
- **Skills:**
  - `get_current_weather`: Current weather for cities
  - `get_forecast`: 5-day weather forecast
  - `recommend_packing`: Packing suggestions based on weather

#### Calculator Agent (Port 5002)
- **Skills:**
  - `calculate`: Basic math operations
  - `convert_currency`: USD, EUR, GBP, JPY conversions
  - `convert_temperature`: Celsius ↔ Fahrenheit

#### Travel Agent (Port 5003)
- **Skills:**
  - `recommend_destination`: Destination suggestions
  - `get_travel_tips`: Safety and cultural tips
  - `estimate_budget`: Trip cost estimates

### 2. **Remote A2A Agent** (Cloud - Railway.app) 🌐

#### Email Agent (Port 5004 local, Railway.app remote)
- **Skills:**
  - `send_email`: Send emails with recipient, subject, and message
  - `validate_email`: Validate email address format
  - `check_email_status`: Track email delivery status
- **Location**: Can run locally OR deployed to Railway.app
- **Purpose**: Demonstrates remote SaaS agent integration
- **Documentation**: See [`email-agent/README.md`](email-agent/README.md)

### 3. **Context Forge (MCP Gateway)**
- Central registry for **both local and remote** A2A agents
- Virtual server grouping: "travel-suite" (local agents)
- Manages agent metadata including location (local/remote)
- Running at: http://localhost:4444

### 4. **Orchestrator**
- **2-Phase Discovery:**
  - Phase 1: Discover agents from Context Forge
  - Phase 2: Fetch AgentCards from each agent
- **Skill-based Routing:** Matches queries to appropriate agents
- **Response Aggregation:** Combines multi-agent responses

### 5. **Streamlit UI**
- Query interface for user interactions
- Agent dashboard showing all registered agents
- Real-time metrics and status

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Conda environment: `mcpdemo`
- Context Forge running at http://localhost:4444

### Installation

```bash
# Install dependencies
conda activate mcpdemo
pip install -r requirements.txt
```

### Setup & Run

#### Step 1: Start Context Forge
```bash
# Already running at http://localhost:4444
```

#### Step 2: Start All Local Agents
```bash
chmod +x scripts/start_all_agents.sh
./scripts/start_all_agents.sh
```

This starts:
- Weather Agent on port 5001
- Calculator Agent on port 5002
- Travel Agent on port 5003

#### Step 2b: Start Email Agent (Local Testing)
```bash
cd email-agent
conda activate mcpdemo
python __main__.py > ../logs/email_agent.log 2>&1 &
cd ..
```

This starts:
- Email Agent on port 5004 (for local testing)
- For remote deployment, see [`email-agent/DEPLOYMENT_GUIDE.md`](email-agent/DEPLOYMENT_GUIDE.md)

#### Step 3: Register Agents with Context Forge
```bash
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

python3 scripts/register_agents.py
```

#### Step 4: Create Virtual Server
```bash
python3 scripts/create_virtual_server.py
```

#### Step 5: Run Orchestrator
```bash
cd orchestrator
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 orchestrator.py
```

## 🌐 Deploy Remote Agent (Optional)

The Email Agent can be deployed to Railway.app to demonstrate remote SaaS agent integration:

### Quick Deploy to Railway

1. **Test locally first** (already running on port 5004)
2. **Deploy to Railway**:
   ```bash
   # See detailed guide
   cat email-agent/DEPLOYMENT_GUIDE.md
   ```
3. **Get Railway URL**: `https://email-agent-production-xxxx.up.railway.app`
4. **Register remote agent**:
   ```bash
   # Update endpoint_url in scripts/register_remote_agent.py
   python3 scripts/register_remote_agent.py
   ```

**Full deployment guide**: [`email-agent/DEPLOYMENT_GUIDE.md`](email-agent/DEPLOYMENT_GUIDE.md)

## 📝 Example Queries

### 1. Simple Weather Query
```
Query> What's the weather in Dallas?
```
**Expected:** Routes to weather_agent, returns current conditions

### 2. Multi-Agent Query
```
Query> What's the weather in Tokyo in Fahrenheit?
```
**Expected:** Routes to weather_agent + calculator_agent for conversion

### 3. Complex Travel Query
```
Query> I want to visit Paris for 7 days. What's the weather, what should I pack, and what's the budget?
```
**Expected:** Routes to weather_agent + travel_agent, combines responses

### 4. Currency Conversion
```
Query> Convert 100 USD to EUR
```
**Expected:** Routes to calculator_agent

### 5. Travel Recommendation
```
Query> Recommend a romantic destination
```
**Expected:** Routes to travel_agent

## 🧪 Testing

### Test Individual Agents

```bash
# Test Calculator Agent
bash scripts/test_calculator.sh

# Test Travel Agent
bash scripts/test_travel.sh

# Weather Agent (already tested)
curl http://localhost:5001/.well-known/agent.json
```

### Test Orchestrator

```bash
# Run test script
bash test_orchestrator_dallas.sh
```

## 📁 Project Structure

```
a2a-orchestrator/
├── agents/
│   ├── calculator_agent.py      # Calculator agent implementation
│   └── travel_agent.py          # Travel agent implementation
├── weather-agent/
│   ├── __main__.py              # Weather agent entry point
│   └── agent_executor.py        # Weather agent logic
├── email-agent/                 # 🌐 REMOTE AGENT (Railway.app)
│   ├── __main__.py              # Email agent entry point
│   ├── agent_executor.py        # Email agent logic
│   ├── requirements.txt         # Dependencies for deployment
│   ├── Procfile                 # Railway start command
│   ├── railway.toml             # Railway configuration
│   ├── README.md                # Email agent documentation
│   └── DEPLOYMENT_GUIDE.md      # Step-by-step Railway deployment
├── orchestrator/
│   └── orchestrator.py          # Main orchestrator with discovery
├── scripts/
│   ├── register_agents.py       # Register local agents
│   ├── register_remote_agent.py # Register remote email agent
│   ├── create_virtual_server.py # Create virtual server
│   ├── start_all_agents.sh      # Start all local agents
│   ├── test_calculator.sh       # Test calculator agent
│   └── test_travel.sh           # Test travel agent
├── ui/
│   └── streamlit_app.py         # Streamlit UI
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Context Forge
export CONTEXT_FORGE_URL=http://localhost:4444
export TOKEN='your-jwt-token'

# Virtual Server
export VIRTUAL_SERVER_NAME=travel-suite

# Orchestrator
export CACHE_REFRESH_INTERVAL=3600  # 1 hour
```

### Agent Ports

**Local Agents:**
- Weather Agent: 5001
- Calculator Agent: 5002
- Travel Agent: 5003
- Email Agent (local testing): 5004

**Remote Agents:**
- Email Agent (Railway): https://your-app.railway.app

**System:**
- Orchestrator: 5010
- Streamlit UI: 8501

## 🎯 Features

### Implemented ✅
- [x] 3 local A2A agents with proper protocol implementation
- [x] 1 remote A2A agent (Email Agent) ready for cloud deployment
- [x] **Hybrid architecture**: Local + Remote agent registry
- [x] Agent registration with Context Forge
- [x] Virtual server creation
- [x] Orchestrator with 2-phase discovery
- [x] Skill-based query routing
- [x] Multi-agent response aggregation
- [x] Test scripts for all components
- [x] Streamlit UI with query interface
- [x] Agent dashboard with metrics
- [x] Railway.app deployment configuration

### To Be Implemented 🚧
- [ ] Advanced LLM-based intent classification
- [ ] Parallel agent execution
- [ ] Response caching
- [ ] Error retry logic with exponential backoff
- [ ] Authentication for remote agents
- [ ] Rate limiting for SaaS agents

## 🐛 Troubleshooting

### Agents Not Starting
```bash
# Kill existing processes
pkill -f "calculator_agent.py"
pkill -f "travel_agent.py"
pkill -f "weather-agent"

# Restart
./scripts/start_all_agents.sh
```

### Token Expired
```bash
# Get fresh token
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')
```

### Agent Not Registered
```bash
# Re-register agents
python3 scripts/register_agents.py
```

## 📚 API Documentation

### AgentCard Endpoints
- Weather: http://localhost:5001/.well-known/agent.json
- Calculator: http://localhost:5002/.well-known/agent.json
- Travel: http://localhost:5003/.well-known/agent.json

### Context Forge API
- List Agents: `GET http://localhost:4444/a2a`
- Register Agent: `POST http://localhost:4444/a2a`
- List Servers: `GET http://localhost:4444/servers`
- Create Server: `POST http://localhost:4444/servers`

### Orchestrator Commands
- `list` - Show all agents and skills
- `refresh` - Rediscover agents
- `quit` - Exit orchestrator

## 🤝 Contributing

This is a demonstration project for A2A multi-agent orchestration. Feel free to extend with:
- Additional agents
- Enhanced routing logic
- UI improvements
- Performance optimizations

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- A2A Protocol: https://a2a-protocol.org/
- A2A Python SDK: https://github.com/a2aproject/a2a-python
- Context Forge (MCP Gateway)

---

**Built with ❤️ using A2A Protocol v0.3.0**