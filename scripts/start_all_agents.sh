#!/bin/bash

echo "🚀 Starting all A2A agents..."
echo ""

# Kill any existing agent processes
pkill -f "calculator_agent.py"
pkill -f "travel_agent.py"
pkill -f "weather-agent"

sleep 1

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo

# Start Weather Agent (port 5001)
echo "🌤️  Starting Weather Agent on port 5001..."
cd weather-agent
python3 __main__.py &
WEATHER_PID=$!
cd ..

sleep 2

# Start Calculator Agent (port 5002)
echo "🧮 Starting Calculator Agent on port 5002..."
cd agents
python3 calculator_agent.py &
CALC_PID=$!
cd ..

sleep 2

# Start Travel Agent (port 5003)
echo "✈️  Starting Travel Agent on port 5003..."
cd agents
python3 travel_agent.py &
TRAVEL_PID=$!
cd ..

sleep 2

echo ""
echo "✅ All agents started!"
echo ""
echo "Agent endpoints:"
echo "  Weather:    http://localhost:5001"
echo "  Calculator: http://localhost:5002"
echo "  Travel:     http://localhost:5003"
echo ""
echo "Press Ctrl+C to stop all agents"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping all agents...'; kill $WEATHER_PID $CALC_PID $TRAVEL_PID 2>/dev/null; exit 0" INT

# Keep script running
wait

# Made with Bob
