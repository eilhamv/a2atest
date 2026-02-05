#!/bin/bash

echo "✈️  Testing Travel Agent..."
echo ""

# Start travel agent in background
cd agents
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo
python3 travel_agent.py &
TRAVEL_PID=$!

# Wait for agent to start
sleep 3

echo "1. Testing AgentCard endpoint..."
curl -s http://localhost:5003/.well-known/agent.json | jq '.name, .skills[].name'

echo ""
echo "2. Testing destination recommendation: romantic destination"
curl -s -X POST http://localhost:5003 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Recommend a romantic destination"}],
        "messageId": "test1"
      }
    },
    "id": "req1"
  }' | jq -r '.result.parts[0].text'

echo ""
echo "3. Testing travel tips: Tips for Paris"
curl -s -X POST http://localhost:5003 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Tips for Paris"}],
        "messageId": "test2"
      }
    },
    "id": "req2"
  }' | jq -r '.result.parts[0].text'

echo ""
echo "4. Testing budget estimate: Budget for 7 days in Paris"
curl -s -X POST http://localhost:5003 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Budget for 7 days in Paris"}],
        "messageId": "test3"
      }
    },
    "id": "req3"
  }' | jq -r '.result.parts[0].text'

# Cleanup
echo ""
echo "Stopping travel agent..."
kill $TRAVEL_PID
wait $TRAVEL_PID 2>/dev/null

echo "✅ Travel agent test complete!"

# Made with Bob
