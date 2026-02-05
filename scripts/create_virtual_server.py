#!/usr/bin/env python3
"""
Create a virtual server in Context Forge and associate all registered agents
"""
import httpx
import asyncio
import os
import sys


CONTEXT_FORGE_URL = "http://localhost:4444"
BEARER_TOKEN = os.getenv("TOKEN")
VIRTUAL_SERVER_NAME = "travel-suite"


async def create_virtual_server():
    """Create virtual server and associate agents"""
    
    if not BEARER_TOKEN:
        print("❌ Error: TOKEN environment variable not set")
        print("Run: export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"email\":\"admin@example.com\",\"password\":\"mvhari123\"}' | jq -r '.access_token')")
        sys.exit(1)
    
    print("🔐 Using authentication token")
    print(f"🌐 Context Forge URL: {CONTEXT_FORGE_URL}")
    print(f"\n🏗️  Creating virtual server: {VIRTUAL_SERVER_NAME}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, get all registered agents
        print("  📋 Fetching registered agents...")
        response = await client.get(
            f"{CONTEXT_FORGE_URL}/a2a",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )
        
        if response.status_code != 200:
            print(f"  ❌ Failed to fetch agents: {response.status_code}")
            sys.exit(1)
        
        agents = response.json()
        agent_names = ["weather_agent", "calculator_agent", "travel_agent"]
        agent_ids = []
        
        for agent in agents:
            if agent.get('name') in agent_names:
                agent_ids.append(agent.get('id'))
                print(f"  ✅ Found {agent.get('name')} (ID: {agent.get('id')})")
        
        if len(agent_ids) != 3:
            print(f"  ⚠️  Warning: Expected 3 agents, found {len(agent_ids)}")
            print("  Make sure all agents are registered first (run register_agents.py)")
        
        # Check if virtual server already exists
        print(f"\n  🔍 Checking if virtual server '{VIRTUAL_SERVER_NAME}' exists...")
        try:
            response = await client.get(
                f"{CONTEXT_FORGE_URL}/servers",
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
            )
            
            if response.status_code == 200:
                servers = response.json()
                existing = next((s for s in servers if s.get('name') == VIRTUAL_SERVER_NAME), None)
                
                if existing:
                    server_id = existing.get('id')
                    print(f"  ✅ Virtual server already exists (ID: {server_id})")
                    
                    # Update associations
                    print(f"  🔄 Updating agent associations...")
                    update_response = await client.put(
                        f"{CONTEXT_FORGE_URL}/servers/{server_id}",
                        headers={
                            "Authorization": f"Bearer {BEARER_TOKEN}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "server": {
                                "name": VIRTUAL_SERVER_NAME,
                                "description": "Travel planning agent collection with weather, calculator, and travel advisor",
                                "associated_a2a_agents": agent_ids
                            }
                        }
                    )
                    
                    if update_response.status_code in [200, 204]:
                        print(f"  ✅ Virtual server updated successfully")
                    else:
                        print(f"  ⚠️  Update status: {update_response.status_code}")
                    
                    return server_id
        except Exception as e:
            print(f"  ⚠️  Could not check existing servers: {e}")
        
        # Create new virtual server
        print(f"\n  🏗️  Creating new virtual server...")
        try:
            response = await client.post(
                f"{CONTEXT_FORGE_URL}/servers",
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "server": {
                        "name": VIRTUAL_SERVER_NAME,
                        "description": "Travel planning agent collection with weather, calculator, and travel advisor",
                        "associated_a2a_agents": agent_ids
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                server_id = result.get('id')
                print(f"  ✅ Virtual server created successfully (ID: {server_id})")
                print(f"\n✨ Setup complete!")
                print(f"   Virtual server: {VIRTUAL_SERVER_NAME}")
                print(f"   Associated agents: {len(agent_ids)}")
                print(f"   Endpoint: {CONTEXT_FORGE_URL}/servers/{VIRTUAL_SERVER_NAME}/agents\n")
                return server_id
            else:
                print(f"  ❌ Failed to create virtual server: {response.status_code}")
                print(f"     Response: {response.text}")
                sys.exit(1)
                
        except Exception as e:
            print(f"  ❌ Error creating virtual server: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_virtual_server())

# Made with Bob
