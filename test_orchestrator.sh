#!/bin/bash

# Get fresh token
export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"mvhari123"}' | jq -r '.access_token')

echo "Token obtained: ${TOKEN:0:50}..."

# Run orchestrator with test commands
cd orchestrator
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mcpdemo

# Feed commands to orchestrator
python3 orchestrator.py << 'EOF'
list
What's the weather in San Francisco?
quit
EOF

# Made with Bob
