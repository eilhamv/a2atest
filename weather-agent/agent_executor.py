from typing_extensions import override
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

class WeatherAgent:
    """Simple weather agent with mock data"""
    
    WEATHER_DATA = {
        "dallas": {"condition": "Sunny", "temp_f": 75, "temp_c": 24},
        "chicago": {"condition": "Cloudy", "temp_f": 55, "temp_c": 13},
        "new york": {"condition": "Rainy", "temp_f": 60, "temp_c": 16},
        "tokyo": {"condition": "Clear", "temp_f": 70, "temp_c": 21},
        "paris": {"condition": "Rainy", "temp_f": 54, "temp_c": 12},
    }
    
    async def get_weather(self, query: str) -> str:
        query_lower = query.lower()
        
        # Find city
        city = None
        for city_name in self.WEATHER_DATA.keys():
            if city_name in query_lower:
                city = city_name
                break
        
        if not city:
            return "Please specify a city: Dallas, Chicago, New York, or Tokyo"
        
        weather = self.WEATHER_DATA[city]
        
        if "forecast" in query_lower:
            return f"5-day forecast for {city.title()}: {weather['condition']}, temps around {weather['temp_f']}°F ({weather['temp_c']}°C)"
        
        return f"{city.title()}: {weather['condition']}, {weather['temp_f']}°F ({weather['temp_c']}°C)"


class WeatherAgentExecutor(AgentExecutor):
    """A2A AgentExecutor implementation for weather agent"""
    
    def __init__(self):
        self.agent = WeatherAgent()
    
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Get the user's message
        message_text = ""
        if context.message and context.message.parts:
            for part in context.message.parts:
                # Part is a discriminated union, access via root
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    message_text = part.root.text
                    break
        
        # Process the weather query
        result = await self.agent.get_weather(message_text)
        
        # Send response through event queue
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    @override
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
