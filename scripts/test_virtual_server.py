#!/usr/bin/env python3
"""Test script to verify virtual server filtering in orchestrator"""

import asyncio
import sys
import os
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from orchestrator.orchestrator import Orchestrator

async def get_auth_token():
    """Get authentication token from Context Forge"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:4444/auth/login",
            json={
                "email": "admin@example.com",
                "password": "mvhari123"
            }
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Failed to authenticate: {response.status_code}")

async def test_virtual_server():
    """Test virtual server filtering"""
    
    print("=" * 60)
    print("Testing Virtual Server Filtering")
    print("=" * 60)
    
    # Get authentication token
    print("\n🔐 Authenticating with Context Forge...")
    token = await get_auth_token()
    print("✅ Authentication successful")
    
    # Set token in environment (orchestrator reads from TOKEN env var)
    os.environ["TOKEN"] = token
    
    orchestrator = Orchestrator()
    
    # Test 1: With virtual server filtering
    print("\n🧪 TEST 1: With Virtual Server Filtering (travel-suite)")
    print("-" * 60)
    await orchestrator.discover_agents(use_virtual_server=True)
    print(f"Discovered agents: {list(orchestrator.agents.keys())}")
    print(f"Total agents: {len(orchestrator.agents)}")
    
    # Test 2: Without virtual server filtering (all agents)
    print("\n🧪 TEST 2: Without Virtual Server Filtering (all agents)")
    print("-" * 60)
    orchestrator.agents = {}  # Reset
    await orchestrator.discover_agents(use_virtual_server=False)
    print(f"Discovered agents: {list(orchestrator.agents.keys())}")
    print(f"Total agents: {len(orchestrator.agents)}")
    
    print("\n" + "=" * 60)
    print("✅ Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_virtual_server())

# Made with Bob
