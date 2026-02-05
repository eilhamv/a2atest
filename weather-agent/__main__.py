import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)
from agent_executor import WeatherAgentExecutor

if __name__ == '__main__':
    # Define agent skills
    get_weather_skill = AgentSkill(
        id='get_current_weather',
        name='Get Current Weather',
        description='Get current weather conditions for a specified city',
        tags=['weather', 'current'],
        examples=['What is the weather in Dallas?', 'Current weather in Tokyo'],
    )
    
    forecast_skill = AgentSkill(
        id='get_forecast',
        name='Get Weather Forecast',
        description='Get 5-day weather forecast for a city',
        tags=['weather', 'forecast'],
        examples=['Weather forecast for New York'],
    )
    
    # Create Agent Card
    agent_card = AgentCard(
        name='weather_agent',
        version='1.0.0',
        description='Provides current weather and forecasts for cities worldwide',
        url='http://localhost:5001',
        protocolVersion='0.3.0',
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
        ),
        authentication={
            'schemes': [],
        },
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        skills=[get_weather_skill, forecast_skill],
    )
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print("🌤️  Weather Agent starting on http://localhost:5001")
    print("📋 AgentCard: http://localhost:5001/.well-known/agent.json")
    
    # Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=5001)
