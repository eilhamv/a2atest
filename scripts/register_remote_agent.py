#!/usr/bin/env python3
"""
Register the remote Email Agent with Context Forge (MCP Gateway)
This demonstrates registering a remote SaaS agent alongside local agents
"""
import httpx
import asyncio
import os
import sys


CONTEXT_FORGE_URL = "http://localhost:4444"
BEARER_TOKEN = os.getenv("TOKEN")

# Remote agent configuration
# NOTE: Update endpoint_url after deploying to Railway.app
REMOTE_AGENT = {
    "name": "email_agent",
    "endpoint_url": "http://localhost:5004",  # Change to Railway URL after deployment
    "agent_type": "jsonrpc",
    "description": "Remote SaaS email service for sending, validating, and tracking emails",
    "tags": ["email", "saas", "remote", "communication"],
    "visibility": "public",
    "metadata": {
        "location": "remote",  # Distinguishes from local agents
        "provider": "railway",  # Hosting provider
        "type": "saas",        # Agent type
        "deployment": "cloud"  # Deployment type
    }
}


async def register_remote_agent():
    """Register the remote email agent with Context Forge"""
    
    if not BEARER_TOKEN:
        print("❌ Error: TOKEN environment variable not set")
        print("Run: export TOKEN=$(curl -s -X POST http://localhost:4444/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"email\":\"admin@example.com\",\"password\":\"mvhari123\"}' | jq -r '.access_token')")
        sys.exit(1)
    
    print("🔐 Using authentication token")
    print(f"🌐 Context Forge URL: {CONTEXT_FORGE_URL}")
    print(f"\n📝 Registering remote agent: {REMOTE_AGENT['name']}...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        agent_name = REMOTE_AGENT["name"]
        
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
                    print(f"  ℹ️  {agent_name} already registered (ID: {agent_id})")
                    print(f"  📍 Endpoint: {existing.get('endpoint_url') or existing.get('endpointUrl')}")
                    
                    # Ask if user wants to update
                    print(f"\n  💡 To update, delete the existing agent first:")
                    print(f"     curl -X DELETE {CONTEXT_FORGE_URL}/a2a/{agent_id} \\")
                    print(f"       -H 'Authorization: Bearer $TOKEN'")
                    return
            
            # Register new agent
            print(f"  📤 Registering {agent_name} as remote SaaS agent...")
            response = await client.post(
                f"{CONTEXT_FORGE_URL}/a2a",
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"agent": REMOTE_AGENT}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                agent_id = result.get('id')
                print(f"  ✅ {agent_name} registered successfully!")
                print(f"  📧 Agent ID: {agent_id}")
                print(f"  📍 Endpoint: {REMOTE_AGENT['endpoint_url']}")
                print(f"  🏷️  Tags: {', '.join(REMOTE_AGENT['tags'])}")
                print(f"  🌐 Location: {REMOTE_AGENT['metadata']['location']}")
                print(f"  ☁️  Provider: {REMOTE_AGENT['metadata']['provider']}")
                
                # Save agent ID
                with open('.agent_ids', 'a') as f:
                    f.write(f"{agent_name}={agent_id}\n")
                print(f"\n  💾 Agent ID saved to .agent_ids")
                
                print(f"\n  🎯 Next Steps:")
                print(f"     1. Test locally: curl http://localhost:5004/.well-known/agent.json")
                print(f"     2. Deploy to Railway.app (see email-agent/DEPLOYMENT_GUIDE.md)")
                print(f"     3. Update endpoint_url in this script to Railway URL")
                print(f"     4. Re-register with updated URL")
                
            else:
                print(f"  ❌ Failed to register {agent_name}: {response.status_code}")
                print(f"     Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error registering {agent_name}: {e}")


if __name__ == "__main__":
    print("="*60)
    print("🚀 Remote Agent Registration")
    print("="*60)
    asyncio.run(register_remote_agent())
    print("\n" + "="*60)
    print("✨ Registration complete!")
    print("="*60)

# Made with Bob
