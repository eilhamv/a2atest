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
import re


class CalculatorAgent:
    """Simple calculator agent with mock implementations"""
    
    EXCHANGE_RATES = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 149.50,
    }
    
    async def calculate(self, expression: str) -> str:
        """Perform basic math operations"""
        try:
            # Extract math expression from query
            # Look for patterns like "15 * 4 + 10" or "calculate 100 + 50"
            match = re.search(r'([\d\s\+\-\*\/\(\)\.]+)', expression)
            if match:
                expr = match.group(1).strip()
                result = eval(expr)
                return f"{expr} = {result}"
            return "Please provide a valid math expression (e.g., 15 * 4 + 10)"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    async def convert_currency(self, query: str) -> str:
        """Convert between currencies"""
        try:
            # Extract amount and currencies
            # Pattern: "100 USD to EUR" or "convert 50 GBP to JPY"
            query_upper = query.upper()
            match = re.search(r'(\d+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:to|TO|in|IN)\s+([A-Z]{3})', query_upper)
            if not match:
                # Try without space before "to"
                match = re.search(r'(\d+(?:\.\d+)?)\s*([A-Z]{3})\s*(?:to|TO)\s*([A-Z]{3})', query_upper)
            
            if match:
                amount = float(match.group(1))
                from_curr = match.group(2)
                to_curr = match.group(3)
                
                if from_curr not in self.EXCHANGE_RATES or to_curr not in self.EXCHANGE_RATES:
                    return f"Supported currencies: {', '.join(self.EXCHANGE_RATES.keys())}"
                
                # Convert via USD
                usd_amount = amount / self.EXCHANGE_RATES[from_curr]
                result = usd_amount * self.EXCHANGE_RATES[to_curr]
                
                return f"{amount} {from_curr} = {result:.2f} {to_curr}"
            
            return "Please specify amount and currencies (e.g., 100 USD to EUR)"
        except Exception as e:
            return f"Currency conversion error: {str(e)}"
    
    async def convert_temperature(self, query: str) -> str:
        """Convert between Celsius and Fahrenheit"""
        try:
            # Pattern: "12°C to F" or "68 fahrenheit to celsius"
            query_upper = query.upper()
            
            # Celsius to Fahrenheit
            match = re.search(r'(\d+(?:\.\d+)?)\s*°?C', query_upper)
            if match and ('F' in query_upper or 'FAHRENHEIT' in query_upper):
                celsius = float(match.group(1))
                fahrenheit = (celsius * 9/5) + 32
                return f"{celsius}°C = {fahrenheit:.1f}°F"
            
            # Fahrenheit to Celsius
            match = re.search(r'(\d+(?:\.\d+)?)\s*°?F', query_upper)
            if match and ('C' in query_upper or 'CELSIUS' in query_upper):
                fahrenheit = float(match.group(1))
                celsius = (fahrenheit - 32) * 5/9
                return f"{fahrenheit}°F = {celsius:.1f}°C"
            
            return "Please specify temperature with unit (e.g., 12°C to F or 68°F to C)"
        except Exception as e:
            return f"Temperature conversion error: {str(e)}"
    
    async def process_query(self, query: str) -> str:
        """Route query to appropriate calculation method"""
        query_lower = query.lower()
        
        # Check for currency conversion
        if any(curr in query.upper() for curr in self.EXCHANGE_RATES.keys()):
            if 'to' in query_lower or 'convert' in query_lower:
                return await self.convert_currency(query)
        
        # Check for temperature conversion
        if ('°c' in query_lower or 'celsius' in query_lower or 
            '°f' in query_lower or 'fahrenheit' in query_lower):
            return await self.convert_temperature(query)
        
        # Default to calculation
        return await self.calculate(query)


class CalculatorAgentExecutor(AgentExecutor):
    """A2A AgentExecutor implementation for calculator agent"""
    
    def __init__(self):
        self.agent = CalculatorAgent()
    
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
    calculate_skill = AgentSkill(
        id='calculate',
        name='Calculate',
        description='Perform basic math operations: add, subtract, multiply, divide',
        tags=['math', 'calculation', 'arithmetic'],
        examples=['15 * 4 + 10', 'Calculate 100 / 5', '(50 + 30) * 2'],
    )
    
    currency_skill = AgentSkill(
        id='convert_currency',
        name='Convert Currency',
        description='Convert between USD, EUR, GBP, and JPY currencies',
        tags=['currency', 'money', 'exchange'],
        examples=['100 USD to EUR', 'Convert 50 GBP to JPY', '1000 JPY in USD'],
    )
    
    temperature_skill = AgentSkill(
        id='convert_temperature',
        name='Convert Temperature',
        description='Convert between Celsius and Fahrenheit temperature scales',
        tags=['temperature', 'celsius', 'fahrenheit'],
        examples=['12°C to F', '68°F to C', 'Convert 25 celsius to fahrenheit'],
    )
    
    # Create Agent Card
    agent_card = AgentCard(
        name='calculator_agent',
        version='1.0.0',
        description='Performs calculations, currency conversions, and temperature conversions',
        url='http://localhost:5002',
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
        skills=[calculate_skill, currency_skill, temperature_skill],
    )
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=CalculatorAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print("🧮 Calculator Agent starting on http://localhost:5002")
    print("📋 AgentCard: http://localhost:5002/.well-known/agent.json")
    
    # Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=5002)

# Made with Bob
