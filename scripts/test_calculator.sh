#!/bin/bash

echo "🧮 Testing Calculator Agent..."
echo ""

# Start calculator agent in background
cd agents
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 calculator_agent.py &
CALC_PID=$!

# Wait for agent to start
sleep 3

echo "1. Testing AgentCard endpoint..."
curl -s http://localhost:5002/.well-known/agent.json | jq '.'

echo ""
echo "2. Testing calculation: 15 * 4 + 10"
curl -s -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "15 * 4 + 10"}],
        "messageId": "test1"
      }
    },
    "id": "req1"
  }' | jq '.'

echo ""
echo "3. Testing currency conversion: 100 USD to EUR"
curl -s -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "100 USD to EUR"}],
        "messageId": "test2"
      }
    },
    "id": "req2"
  }' | jq '.'

echo ""
echo "4. Testing temperature conversion: 12°C to F"
curl -s -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "12°C to F"}],
        "messageId": "test3"
      }
    },
    "id": "req3"
  }' | jq '.'

# Cleanup
echo ""
echo "Stopping calculator agent..."
kill $CALC_PID
wait $CALC_PID 2>/dev/null

echo "✅ Calculator agent test complete!"

# Made with Bob
