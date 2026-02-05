#!/bin/bash
# Stop all A2A system services

echo "🛑 Stopping A2A Multi-Agent Orchestrator System..."
echo ""

# Stop Streamlit UI
echo "Stopping Streamlit UI..."
pkill -f "streamlit run ui/streamlit_app.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Streamlit stopped"
else
    echo "ℹ️  Streamlit not running"
fi

# Stop all agents
echo "Stopping agents..."
pkill -f "travel_agent.py" 2>/dev/null
pkill -f "calculator_agent.py" 2>/dev/null
pkill -f "weather_agent.py" 2>/dev/null
pkill -f "python3 __main__.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Agents stopped"
else
    echo "ℹ️  Agents not running"
fi

# Stop Context Forge (MCP Gateway)
echo "Stopping Context Forge..."
pkill -9 -f "mcpgateway" 2>/dev/null
sleep 1
if pgrep -f "mcpgateway" > /dev/null 2>&1; then
    echo "⚠️  Some Context Forge processes still running, force killing..."
    pkill -9 -f "mcpgateway" 2>/dev/null
    sleep 1
fi
if pgrep -f "mcpgateway" > /dev/null 2>&1; then
    echo "⚠️  Context Forge still running"
else
    echo "✅ Context Forge stopped"
fi

# Stop orchestrator if running
echo "Stopping orchestrator..."
pkill -f "orchestrator.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Orchestrator stopped"
else
    echo "ℹ️  Orchestrator not running"
fi

echo ""
echo "✅ All services stopped!"

# Made with Bob
