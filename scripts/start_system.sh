#!/bin/bash
# Start the complete A2A Multi-Agent Orchestrator System

echo "🚀 Starting A2A Multi-Agent Orchestrator System..."
echo ""

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo

# Check if Context Forge is already running
if pgrep -f "mcpgateway" > /dev/null; then
    echo "✅ Context Forge already running"
else
    echo "Starting Context Forge (MCP Gateway)..."
    nohup mcpgateway mcpgateway.main:app > logs/context_forge.log 2>&1 &
    
    # Wait for Context Forge to be ready
    echo "Waiting for Context Forge to start..."
    for i in {1..30}; do
        if curl -s http://localhost:4444/health > /dev/null 2>&1; then
            echo "✅ Context Forge started on http://localhost:4444"
            break
        fi
        sleep 1
    done
    
    if ! curl -s http://localhost:4444/health > /dev/null 2>&1; then
        echo "❌ Context Forge failed to start. Check logs/context_forge.log"
        exit 1
    fi
fi

# Get authentication token
echo ""
echo "🔐 Getting authentication token..."
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Failed to get authentication token"
    echo "Make sure Context Forge is running and credentials are correct"
    exit 1
fi
echo "✅ Authentication successful"

# Set virtual server (optional - comment out to disable filtering)
export VIRTUAL_SERVER="travel-suite"
echo "🎯 Virtual server filtering: $VIRTUAL_SERVER"

# Start all agents
echo ""
echo "Starting A2A agents..."
bash scripts/start_all_agents.sh > logs/agents.log 2>&1 &
sleep 3
echo "✅ Agents started:"
echo "   - Weather Agent: http://localhost:5001"
echo "   - Calculator Agent: http://localhost:5002"
echo "   - Travel Agent: http://localhost:5003"

# Start Streamlit UI
echo ""
echo "Starting Streamlit UI..."
nohup streamlit run ui/streamlit_app.py --server.port 8501 > logs/streamlit.log 2>&1 &
sleep 3
echo "✅ Streamlit UI started on http://localhost:8501"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ System started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access Points:"
echo "   • Streamlit UI:      http://localhost:8501"
echo "   • Context Forge:     http://localhost:4444"
echo "   • Context Forge Admin: http://localhost:4444/admin"
echo ""
echo "📊 Agent Endpoints:"
echo "   • Weather Agent:     http://localhost:5001"
echo "   • Calculator Agent:  http://localhost:5002"
echo "   • Travel Agent:      http://localhost:5003"
echo ""
echo "🎯 Virtual Server: $VIRTUAL_SERVER"
echo ""
echo "📝 Logs:"
echo "   • Context Forge: logs/context_forge.log"
echo "   • Agents:        logs/agents.log"
echo "   • Streamlit:     logs/streamlit.log"
echo ""
echo "To stop all services: bash scripts/stop_all.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Made with Bob
