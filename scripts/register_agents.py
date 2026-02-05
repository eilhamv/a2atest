#!/usr/bin/env python3
"""
Register all A2A agents with Context Forge (MCP Gateway)
"""
import httpx
import asyncio
import os
import sys


CONTEXT_FORGE_URL = "http://localhost:4444"
BEARER_TOKEN = os.getenv("TOKEN")

AGENTS = [
    {
        "name": "weather_agent",
        "endpoint_url": "http://localhost:5001",
        "agent_type": "jsonrpc",
        "description": "Provides weather information and forecasts for cities worldwide",
        "tags": ["weather", "travel", "forecast"],
        "visibility": "public"
    },
    {
        "name": "calculator_agent",
        "endpoint_url": "http://localhost:5002",
        "agent_type": "jsonrpc",
        "description": "Performs calculations, currency conversions, and temperature conversions",
        "tags": ["calculator", "math", "currency", "temperature"],
        "visibility": "public"
    },
    {
        "name": "travel_agent",
        "endpoint_url": "http://localhost:5003",
        "agent_type": "jsonrpc",
        "description": "Travel advisor providing destination recommendations, tips, and budget estimates",
        "tags": ["travel", "destinations", "budget", "tips"],
        "visibility": "public"
    }
]


async def register_agents():
    """Register all agents with Context Forge"""
    
    if not BEARER_TOKEN:
        print("❌ Error: TOKEN environment variable not set")
        print("Run: export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"email\":\"admin@example.com\",\"password\":\"mvhari123\"}' | jq -r '.access_token')")
        sys.exit(1)
    
    print("🔐 Using authentication token")
    print(f"🌐 Context Forge URL: {CONTEXT_FORGE_URL}")
    print(f"\n📝 Registering {len(AGENTS)} agents...\n")
    
    registered_ids = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for agent in AGENTS:
            agent_name = agent["name"]
            print(f"  📋 Registering {agent_name}...")
            
            try:
                # Check if agent already exists
                response = await client.get(
                    f"{CONTEXT_FORGE_URL}/a2a",
                    headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
                )
                
                if response.status_code == 200:
                    existing_agents = response.json()
                    existing = next((a for a in existing_agents if a.get('name') == agent_name), None)
                    
                    if existing:
                        agent_id = existing.get('id')
                        print(f"  ✅ {agent_name} already registered (ID: {agent_id})")
                        registered_ids[agent_name] = agent_id
                        continue
                
                # Register new agent
                response = await client.post(
                    f"{CONTEXT_FORGE_URL}/a2a",
                    headers={
                        "Authorization": f"Bearer {BEARER_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={"agent": agent}
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    agent_id = result.get('id')
                    registered_ids[agent_name] = agent_id
                    print(f"  ✅ {agent_name} registered successfully (ID: {agent_id})")
                else:
                    print(f"  ❌ Failed to register {agent_name}: {response.status_code}")
                    print(f"     Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error registering {agent_name}: {e}")
    
    print(f"\n✨ Registration complete: {len(registered_ids)}/{len(AGENTS)} agents registered\n")
    
    # Save agent IDs for virtual server creation
    if len(registered_ids) == len(AGENTS):
        with open('.agent_ids', 'w') as f:
            for name, agent_id in registered_ids.items():
                f.write(f"{name}={agent_id}\n")
        print("💾 Agent IDs saved to .agent_ids\n")
    
    return registered_ids


if __name__ == "__main__":
    asyncio.run(register_agents())

# Made with Bob
