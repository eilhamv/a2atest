import uvicorn
from typing_extensions import override
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)


class TravelAgent:
    """Simple travel advisor agent with mock recommendations"""
    
    DESTINATIONS = {
        "romantic": {
            "name": "Paris",
            "description": "The City of Light offers romantic ambiance, world-class cuisine, and iconic landmarks",
            "highlights": ["Eiffel Tower", "Seine River cruises", "Charming cafes", "Art museums"],
            "best_time": "April-June, September-October"
        },
        "adventure": {
            "name": "New Zealand",
            "description": "Perfect for thrill-seekers with stunning landscapes and outdoor activities",
            "highlights": ["Bungee jumping", "Hiking", "Skiing", "Lord of the Rings locations"],
            "best_time": "December-February (summer)"
        },
        "beach": {
            "name": "Maldives",
            "description": "Tropical paradise with crystal-clear waters and luxury resorts",
            "highlights": ["Snorkeling", "Diving", "Overwater bungalows", "Pristine beaches"],
            "best_time": "November-April"
        },
        "cultural": {
            "name": "Tokyo",
            "description": "Blend of ancient traditions and cutting-edge modernity",
            "highlights": ["Temples", "Cherry blossoms", "Technology", "Cuisine"],
            "best_time": "March-May, September-November"
        },
        "budget": {
            "name": "Thailand",
            "description": "Affordable destination with rich culture and beautiful beaches",
            "highlights": ["Bangkok temples", "Island hopping", "Street food", "Friendly locals"],
            "best_time": "November-February"
        }
    }
    
    TRAVEL_TIPS = {
        "paris": [
            "Learn basic French phrases (Bonjour, Merci, S'il vous plaît)",
            "Validate metro tickets before boarding",
            "Avoid tourist traps near Eiffel Tower - explore local neighborhoods",
            "Book museum tickets online to skip lines",
            "Try authentic bistros away from main tourist areas"
        ],
        "tokyo": [
            "Get a Suica/Pasmo card for easy train travel",
            "Learn basic Japanese etiquette (bowing, removing shoes)",
            "Cash is still widely used - carry yen",
            "Download Google Translate with offline Japanese",
            "Visit convenience stores (konbini) for quick meals"
        ],
        "new york": [
            "Use subway for transportation - faster than taxis",
            "Walk across Brooklyn Bridge for amazing views",
            "Visit museums on 'pay what you wish' days",
            "Try diverse food from different neighborhoods",
            "Book Broadway tickets in advance or try TKTS booth"
        ],
        "london": [
            "Get an Oyster card for public transport",
            "Many museums are free (British Museum, National Gallery)",
            "Mind the gap! Stand on right side of escalators",
            "Try traditional pub food and afternoon tea",
            "Book attractions online for better prices"
        ]
    }
    
    BUDGET_ESTIMATES = {
        "paris": {
            "flights": 800,
            "hotel_per_night": 150,
            "daily_expenses": 100,
            "activities": 200
        },
        "tokyo": {
            "flights": 1200,
            "hotel_per_night": 120,
            "daily_expenses": 80,
            "activities": 150
        },
        "maldives": {
            "flights": 1500,
            "hotel_per_night": 400,
            "daily_expenses": 150,
            "activities": 300
        },
        "thailand": {
            "flights": 900,
            "hotel_per_night": 50,
            "daily_expenses": 40,
            "activities": 100
        }
    }
    
    async def recommend_destination(self, query: str) -> str:
        """Recommend destinations based on preferences"""
        query_lower = query.lower()
        
        # Match preferences
        if any(word in query_lower for word in ["romantic", "romance", "honeymoon", "couple"]):
            dest = self.DESTINATIONS["romantic"]
        elif any(word in query_lower for word in ["adventure", "thrill", "hiking", "outdoor"]):
            dest = self.DESTINATIONS["adventure"]
        elif any(word in query_lower for word in ["beach", "tropical", "island", "ocean"]):
            dest = self.DESTINATIONS["beach"]
        elif any(word in query_lower for word in ["cultural", "culture", "history", "traditional"]):
            dest = self.DESTINATIONS["cultural"]
        elif any(word in query_lower for word in ["budget", "cheap", "affordable", "inexpensive"]):
            dest = self.DESTINATIONS["budget"]
        else:
            # Default recommendation
            dest = self.DESTINATIONS["romantic"]
        
        response = f"Recommended: {dest['name']}\n\n"
        response += f"{dest['description']}\n\n"
        response += f"Highlights: {', '.join(dest['highlights'])}\n"
        response += f"Best time to visit: {dest['best_time']}"
        
        return response
    
    async def get_travel_tips(self, query: str) -> str:
        """Provide travel tips for specific destinations"""
        query_lower = query.lower()
        
        # Find matching destination
        for city, tips in self.TRAVEL_TIPS.items():
            if city in query_lower:
                response = f"Travel Tips for {city.title()}:\n\n"
                for i, tip in enumerate(tips, 1):
                    response += f"{i}. {tip}\n"
                return response
        
        return "Please specify a destination (Paris, Tokyo, New York, or London) for travel tips"
    
    async def estimate_budget(self, query: str) -> str:
        """Estimate travel budget for destinations"""
        query_lower = query.lower()
        
        # Extract number of days
        days = 7  # default
        import re
        match = re.search(r'(\d+)\s*days?', query_lower)
        if match:
            days = int(match.group(1))
        
        # Find matching destination
        for city, costs in self.BUDGET_ESTIMATES.items():
            if city in query_lower:
                flights = costs["flights"]
                hotel = costs["hotel_per_night"] * days
                daily = costs["daily_expenses"] * days
                activities = costs["activities"]
                total = flights + hotel + daily + activities
                
                response = f"Budget Estimate for {days} days in {city.title()}:\n\n"
                response += f"Flights: ${flights}\n"
                response += f"Hotel ({days} nights): ${hotel}\n"
                response += f"Food & Transport: ${daily}\n"
                response += f"Activities: ${activities}\n"
                response += f"─────────────────\n"
                response += f"Total: ${total:,}"
                
                return response
        
        return "Please specify a destination (Paris, Tokyo, Maldives, or Thailand) for budget estimate"
    
    async def process_query(self, query: str) -> str:
        """Route query to appropriate travel method"""
        query_lower = query.lower()
        
        # Check for budget estimate
        if any(word in query_lower for word in ["budget", "cost", "price", "expensive", "estimate"]):
            return await self.estimate_budget(query)
        
        # Check for travel tips
        if any(word in query_lower for word in ["tips", "advice", "safety", "cultural"]):
            return await self.get_travel_tips(query)
        
        # Default to destination recommendation
        return await self.recommend_destination(query)


class TravelAgentExecutor(AgentExecutor):
    """A2A AgentExecutor implementation for travel agent"""
    
    def __init__(self):
        self.agent = TravelAgent()
    
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
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    message_text = part.root.text
                    break
        
        # Process the query
        result = await self.agent.process_query(message_text)
        
        # Send response through event queue
        await event_queue.enqueue_event(new_agent_text_message(result))
    
    @override
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')


if __name__ == '__main__':
    # Define agent skills
    recommend_skill = AgentSkill(
        id='recommend_destination',
        name='Recommend Destination',
        description='Suggest travel destinations based on preferences like romantic, adventure, beach, cultural, or budget',
        tags=['travel', 'destination', 'recommendation'],
        examples=['Recommend a romantic destination', 'Best place for adventure travel', 'Budget-friendly vacation'],
    )
    
    tips_skill = AgentSkill(
        id='get_travel_tips',
        name='Get Travel Tips',
        description='Provide safety tips, cultural information, and practical advice for specific destinations',
        tags=['travel', 'tips', 'advice', 'safety'],
        examples=['Tips for Paris', 'Travel advice for Tokyo', 'What to know about New York'],
    )
    
    budget_skill = AgentSkill(
        id='estimate_budget',
        name='Estimate Budget',
        description='Calculate estimated travel costs including flights, accommodation, food, and activities',
        tags=['travel', 'budget', 'cost', 'price'],
        examples=['Budget for 7 days in Paris', 'How much does Tokyo cost', 'Estimate trip to Maldives'],
    )
    
    # Create Agent Card
    agent_card = AgentCard(
        name='travel_agent',
        version='1.0.0',
        description='Travel advisor providing destination recommendations, tips, and budget estimates',
        url='http://localhost:5003',
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
        skills=[recommend_skill, tips_skill, budget_skill],
    )
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=TravelAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print("✈️  Travel Agent starting on http://localhost:5003")
    print("📋 AgentCard: http://localhost:5003/.well-known/agent.json")
    
    # Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=5003)

# Made with Bob
