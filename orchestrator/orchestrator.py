import httpx
import asyncio
import os
from uuid import uuid4
from a2a.client.client import Client
from a2a.client.card_resolver import A2ACardResolver
from a2a.types import MessageSendParams, SendMessageRequest

# Configuration
CONTEXT_FORGE_URL = "http://localhost:4444"
VIRTUAL_SERVER_NAME = os.getenv("VIRTUAL_SERVER", "travel-suite")  # Virtual server to query

def get_bearer_token():
    """Get bearer token from environment (read dynamically)"""
    return os.getenv("TOKEN")

class Orchestrator:
    """Orchestrator that discovers and routes tasks to A2A agents via Context Forge"""
    
    def __init__(self):
        self.agents = {}  # {agent_name: {id, endpoint_url, card, skills}}
        
    async def discover_agents(self, use_virtual_server=True):
        """Discover agents from Context Forge registry
        
        Args:
            use_virtual_server: If True, filters agents by virtual server.
                              If False, queries all agents.
        """
        print("\n🔍 Discovering agents from Context Forge...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get all agents first
            token = get_bearer_token()
            response = await client.get(
                f"{CONTEXT_FORGE_URL}/a2a",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch agents: {response.status_code}")
                return
            
            all_agents = response.json()
            
            # Filter by virtual server if configured
            if use_virtual_server and VIRTUAL_SERVER_NAME:
                print(f"   Filtering by virtual server: {VIRTUAL_SERVER_NAME}")
                
                # Get virtual server details
                token = get_bearer_token()
                servers_response = await client.get(
                    f"{CONTEXT_FORGE_URL}/servers",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if servers_response.status_code == 200:
                    servers = servers_response.json()
                    target_server = next((s for s in servers if s['name'] == VIRTUAL_SERVER_NAME), None)
                    
                    if target_server and 'associatedA2aAgents' in target_server:
                        associated_ids = set(target_server['associatedA2aAgents'])
                        registered_agents = [a for a in all_agents if a.get('id') in associated_ids]
                        print(f"   ✅ Found {len(registered_agents)} agents in virtual server")
                    else:
                        print(f"   ⚠️  Virtual server '{VIRTUAL_SERVER_NAME}' not found or has no agents")
                        print(f"   Falling back to all agents")
                        registered_agents = all_agents
                else:
                    print(f"   ⚠️  Failed to fetch virtual servers, using all agents")
                    registered_agents = all_agents
            else:
                print(f"   Using all agents")
                registered_agents = all_agents
            
            print(f"✅ Discovered {len(registered_agents)} agents total\n")
            
            # Fetch AgentCard from each agent
            for agent in registered_agents:
                agent_id = agent.get('id')
                agent_name = agent.get('name')
                # Handle both snake_case and camelCase
                endpoint_url = agent.get('endpoint_url') or agent.get('endpointUrl')
                
                if not endpoint_url:
                    print(f"  ⚠️  Skipping {agent_name}: No endpoint URL")
                    continue
                
                try:
                    print(f"  📋 Fetching AgentCard from {agent_name}")
                    
                    # Use A2A SDK to fetch AgentCard
                    async with httpx.AsyncClient() as httpx_client:
                        resolver = A2ACardResolver(
                            httpx_client=httpx_client,
                            base_url=endpoint_url,
                        )
                        
                        # This fetches from /.well-known/agent.json
                        agent_card = await resolver.get_agent_card()
                        
                        # Store agent info
                        self.agents[agent_name] = {
                            'id': agent_id,
                            'endpoint_url': endpoint_url,
                            'card': agent_card,
                            'skills': {
                                skill.id: {
                                    'name': skill.name,
                                    'description': skill.description,
                                    'examples': skill.examples
                                }
                                for skill in agent_card.skills
                            }
                        }
                        
                        skill_count = len(agent_card.skills)
                        print(f"  ✅ Loaded {agent_name}: {skill_count} skills")
                        
                except Exception as e:
                    print(f"  ❌ Failed to load {agent_name}: {e}")
        
        total_skills = sum(len(info['skills']) for info in self.agents.values())
        print(f"\n✨ Discovery complete: {len(self.agents)} agents, {total_skills} skills\n")
    
    def match_query_to_skills(self, query: str):
        """Match user query to agent skills using improved keyword matching"""
        query_lower = query.lower()
        matched = []
        
        # Define stop words to ignore
        stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'what', 'when', 'where', 'who', 'how', 'i', 'you', 'me', 'my', 'your'}
        
        # Extract meaningful keywords from query (filter out stop words and numbers)
        query_words = [w for w in query_lower.split() if w not in stop_words and not w.replace('.', '').replace('-', '').isdigit()]
        
        # Define strong keyword mappings for each agent type
        agent_keywords = {
            'weather_agent': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy', 'pack', 'packing', 'climate'],
            'calculator_agent': ['calculate', 'convert', 'currency', 'usd', 'eur', 'gbp', 'jpy', 'fahrenheit', 'celsius', 'math', 'add', 'subtract', 'multiply', 'divide'],
            'travel_agent': ['travel', 'destination', 'recommend', 'trip', 'visit', 'budget', 'tips', 'romantic', 'adventure', 'vacation']
        }
        
        for agent_name, agent_info in self.agents.items():
            agent_score = 0
            matched_skills = []
            
            # Check if query contains agent-specific keywords
            if agent_name in agent_keywords:
                for keyword in agent_keywords[agent_name]:
                    if keyword in query_lower:
                        agent_score += 10  # Strong match
            
            # Check each skill
            for skill_id, skill in agent_info['skills'].items():
                skill_score = 0
                desc_lower = skill['description'].lower()
                name_lower = skill['name'].lower()
                
                # Check skill name and description for meaningful keywords
                for word in query_words:
                    if len(word) > 2:  # Only consider words longer than 2 chars
                        if word in name_lower:
                            skill_score += 5
                        if word in desc_lower:
                            skill_score += 3
                
                # If skill has a good score, add it
                if skill_score > 0:
                    matched_skills.append({
                        'skill_id': skill_id,
                        'skill_name': skill['name'],
                        'score': skill_score
                    })
            
            # If agent has matched skills or strong keyword match, add to results
            if matched_skills or agent_score > 0:
                total_score = agent_score + sum(s['score'] for s in matched_skills)
                matched.append({
                    'agent_name': agent_name,
                    'skill_id': matched_skills[0]['skill_id'] if matched_skills else list(agent_info['skills'].keys())[0],
                    'skill_name': matched_skills[0]['skill_name'] if matched_skills else list(agent_info['skills'].values())[0]['name'],
                    'endpoint': agent_info['endpoint_url'],
                    'score': total_score
                })
        
        # Sort by score (highest first) and return only high-scoring matches
        matched.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter: only return matches with score > 5 (meaningful matches)
        return [m for m in matched if m['score'] > 5]
    
    async def invoke_agent(self, agent_name: str, query: str):
        """Invoke an agent using direct JSON-RPC 2.0 call"""
        agent_info = self.agents.get(agent_name)
        if not agent_info:
            return f"Agent {agent_name} not found"
        
        endpoint_url = agent_info['endpoint_url']
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create JSON-RPC 2.0 request
                payload = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"type": "text", "text": query}],
                            "messageId": uuid4().hex
                        }
                    },
                    "id": uuid4().hex
                }
                
                # Send request to agent (root endpoint for A2A agents)
                response = await client.post(
                    endpoint_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    return f"HTTP {response.status_code}: {response.text}"
                
                result = response.json()
                
                # Extract text from JSON-RPC response
                if 'result' in result:
                    result_data = result['result']
                    if isinstance(result_data, dict) and 'parts' in result_data:
                        texts = []
                        for part in result_data['parts']:
                            if isinstance(part, dict) and 'text' in part:
                                texts.append(part['text'])
                        return ' '.join(texts) if texts else "No text in response"
                    return str(result_data)
                elif 'error' in result:
                    return f"Agent error: {result['error']}"
                
                return "Unexpected response format"
                
        except Exception as e:
            return f"Error invoking {agent_name}: {str(e)}"
    
    async def route_query(self, query: str):
        """Route user query to appropriate agent(s)"""
        print(f"\n📥 Query: {query}")
        
        # Match query to agent skills
        matches = self.match_query_to_skills(query)
        
        if not matches:
            return "❌ No agent found to handle this request"
        
        print(f"🎯 Matched {len(matches)} agent(s):")
        for match in matches:
            print(f"   • {match['agent_name']}.{match['skill_id']}")
        
        # Invoke matched agents
        results = []
        for match in matches:
            agent_name = match['agent_name']
            print(f"\n🔄 Calling {agent_name}...")
            
            result = await self.invoke_agent(agent_name, query)
            results.append(f"{agent_name}: {result}")
            print(f"✅ {agent_name}: {result}")
        
        return "\n".join(results)


async def main():
    """Main interactive loop"""
    # Check for bearer token
    token = get_bearer_token()
    if not token:
        print("❌ Error: TOKEN environment variable not set")
        print("Run: export TOKEN='your-jwt-token'")
        return
    
    orchestrator = Orchestrator()
    
    # Initial discovery
    await orchestrator.discover_agents()
    
    print("="*60)
    print("🤖 Orchestrator Ready")
    print("="*60)
    print("Commands:")
    print("  - Type your query to route to agents")
    print("  - 'refresh' - Rediscover agents")
    print("  - 'list' - Show all agents and skills")
    print("  - 'quit' - Exit")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("Query> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'refresh':
                orchestrator.agents = {}
                await orchestrator.discover_agents()
                continue
            
            if user_input.lower() == 'list':
                print("\n📋 Available Agents and Skills:")
                for agent_name, info in orchestrator.agents.items():
                    print(f"\n  🤖 {agent_name} ({info['endpoint_url']})")
                    for skill_id, skill in info['skills'].items():
                        print(f"    • {skill['name']}: {skill['description']}")
                        if skill.get('examples'):
                            print(f"      Examples: {', '.join(skill['examples'][:2])}")
                print()
                continue
            
            # Route query
            response = await orchestrator.route_query(user_input)
            print(f"\n💬 Response:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
