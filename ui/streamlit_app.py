import streamlit as st
import httpx
import asyncio
import os
from datetime import datetime

# Configuration
CONTEXT_FORGE_URL = os.getenv("CONTEXT_FORGE_URL", "http://localhost:4444")
BEARER_TOKEN = os.getenv("TOKEN", "")
VIRTUAL_SERVER = os.getenv("VIRTUAL_SERVER", "travel-suite")

# Import orchestrator routing logic
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from orchestrator.orchestrator import Orchestrator

st.set_page_config(
    page_title="A2A Multi-Agent Orchestrator",
    page_icon="🤖",
    layout="wide"
)

# Sidebar
st.sidebar.title("🤖 A2A Orchestrator")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Query Interface", "Agent Dashboard"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")

# Check if token is set
if not BEARER_TOKEN:
    st.sidebar.error("⚠️ TOKEN not set")
    st.sidebar.code("export TOKEN='your-token'")
else:
    st.sidebar.success("✅ Authenticated")

# Show virtual server configuration
st.sidebar.markdown("---")
st.sidebar.markdown("### Virtual Server")
if VIRTUAL_SERVER:
    st.sidebar.info(f"🎯 Filtering: `{VIRTUAL_SERVER}`")
    st.sidebar.caption("Only agents in this virtual server will be queried")
else:
    st.sidebar.warning("⚠️ No filter (all agents)")
    st.sidebar.caption("Querying all registered agents")


async def get_agents():
    """Fetch all registered agents from Context Forge"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CONTEXT_FORGE_URL}/a2a",
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        st.error(f"Error fetching agents: {e}")
        return []


async def get_agent_card(endpoint_url):
    """Fetch AgentCard from an agent"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{endpoint_url}/.well-known/agent.json")
            if response.status_code == 200:
                return response.json()
            return None
    except:
        return None


async def call_agent(endpoint_url, query):
    """Call an agent with a query"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": query}],
                        "messageId": f"ui-{datetime.now().timestamp()}"
                    }
                },
                "id": f"req-{datetime.now().timestamp()}"
            }
            
            response = await client.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and 'parts' in result['result']:
                    texts = []
                    for part in result['result']['parts']:
                        if isinstance(part, dict) and 'text' in part:
                            texts.append(part['text'])
                    return ' '.join(texts) if texts else "No response"
                return "Unexpected response format"
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# Page 1: Query Interface
if page == "Query Interface":
    st.title("🔍 Query Interface")
    st.markdown("Ask questions to the A2A multi-agent system")
    
    # Initialize session state for query
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    
    # Query input
    query = st.text_input(
        "Enter your query:",
        value=st.session_state.current_query,
        placeholder="e.g., What's the weather in Dallas?",
        key="query_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submit = st.button("🚀 Submit", type="primary")
    with col2:
        if st.button("🔄 Refresh Agents"):
            st.rerun()
    
    if submit and query:
        with st.spinner("Processing query..."):
            start_time = datetime.now()
            
            # Initialize orchestrator and discover agents
            orchestrator = Orchestrator()
            asyncio.run(orchestrator.discover_agents())
            
            if not orchestrator.agents:
                st.error("No agents available. Make sure agents are registered.")
            else:
                # Show discovery info
                if VIRTUAL_SERVER:
                    st.info(f"🎯 Found {len(orchestrator.agents)} agents in virtual server '{VIRTUAL_SERVER}'")
                else:
                    st.info(f"Found {len(orchestrator.agents)} registered agents (all)")
                
                # Use smart routing to match query to relevant agents
                matches = orchestrator.match_query_to_skills(query)
                
                if not matches:
                    st.warning("⚠️ No relevant agents found for this query. Showing all agent responses:")
                    # Fallback: call all agents
                    matches = [
                        {
                            'agent_name': name,
                            'endpoint': info['endpoint_url']
                        }
                        for name, info in orchestrator.agents.items()
                    ]
                else:
                    st.success(f"🎯 Matched {len(matches)} relevant agent(s)")
                
                # Show responses from matched agents only
                st.markdown("### 📤 Responses")
                
                for match in matches:
                    agent_name = match['agent_name']
                    endpoint_url = match['endpoint']
                    
                    with st.expander(f"🤖 {agent_name}", expanded=True):
                        response = asyncio.run(call_agent(endpoint_url, query))
                        st.markdown(response)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                st.success(f"✅ Query completed in {duration:.2f}s")
    
    # Example queries
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    
    examples = [
        "What's the weather in Dallas?",
        "Convert 100 USD to EUR",
        "Recommend a romantic destination",
        "21°C to F",
        "Budget for 7 days in Paris"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.current_query = example
                st.rerun()


# Page 2: Agent Dashboard
elif page == "Agent Dashboard":
    st.title("📊 Agent Dashboard")
    st.markdown("Overview of all registered A2A agents")
    
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()
    
    with st.spinner("Loading agents..."):
        agents = asyncio.run(get_agents())
    
    if not agents:
        st.warning("No agents registered. Run the registration script first.")
        st.code("python3 scripts/register_agents.py")
    else:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Agents", len(agents))
        with col2:
            active_count = sum(1 for a in agents if a.get('enabled', False))
            st.metric("Active Agents", active_count)
        with col3:
            total_skills = 0
            for agent in agents:
                endpoint = agent.get('endpointUrl') or agent.get('endpoint_url')
                if endpoint:
                    card = asyncio.run(get_agent_card(endpoint))
                    if card and 'skills' in card:
                        total_skills += len(card['skills'])
            st.metric("Total Skills", total_skills)
        
        st.markdown("---")
        
        # Agent details
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            agent_desc = agent.get('description', 'No description')
            endpoint_url = agent.get('endpointUrl') or agent.get('endpoint_url')
            enabled = agent.get('enabled', False)
            reachable = agent.get('reachable', False)
            
            status_icon = "🟢" if (enabled and reachable) else "🔴"
            
            with st.expander(f"{status_icon} {agent_name}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {agent_desc}")
                    st.markdown(f"**Endpoint:** `{endpoint_url}`")
                    st.markdown(f"**Status:** {'Active' if enabled else 'Inactive'}")
                    
                    # Fetch and display skills
                    if endpoint_url:
                        card = asyncio.run(get_agent_card(endpoint_url))
                        if card and 'skills' in card:
                            st.markdown("**Skills:**")
                            for skill in card['skills']:
                                st.markdown(f"- **{skill.get('name')}**: {skill.get('description')}")
                                if skill.get('examples'):
                                    st.caption(f"  Examples: {', '.join(skill['examples'][:2])}")
                
                with col2:
                    # Metrics
                    metrics = agent.get('metrics', {})
                    if metrics:
                        st.metric("Total Calls", metrics.get('totalExecutions', 0))
                        failure_rate = metrics.get('failureRate', 0)
                        success_rate = (1 - failure_rate) * 100 if failure_rate is not None else 100
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                        avg_time = metrics.get('avgResponseTime', 0)
                        st.metric("Avg Response", f"{avg_time if avg_time is not None else 0:.3f}s")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🤖 A2A Multi-Agent Orchestrator System | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

# Made with Bob
