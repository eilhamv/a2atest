#!/usr/bin/env python3
"""
Email Agent - Remote SaaS agent for A2A multi-agent system
Demonstrates remote agent integration with Context Forge
"""
import asyncio
import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)
from agent_executor import EmailAgentExecutor

if __name__ == '__main__':
    # Define agent skills
    send_email_skill = AgentSkill(
        id='send_email',
        name='Send Email',
        description='Send an email to a recipient with subject and message',
        tags=['email', 'send', 'communication'],
        examples=[
            'Send email to john@example.com with subject Hello and message Hi there',
            'Email sarah@company.com about Meeting tomorrow',
            'Send mail to team@startup.com with subject Update and message Project completed'
        ],
    )
    
    validate_email_skill = AgentSkill(
        id='validate_email',
        name='Validate Email',
        description='Validate email address format and check domain',
        tags=['email', 'validation', 'verify'],
        examples=[
            'Validate email john@example.com',
            'Check if sarah@company.com is valid',
            'Is test@gmail.com a valid email?'
        ],
    )
    
    check_status_skill = AgentSkill(
        id='check_email_status',
        name='Check Email Status',
        description='Check delivery status of sent emails',
        tags=['email', 'status', 'tracking', 'delivery'],
        examples=[
            'Check status email_abc12345',
            'What is the delivery status?',
            'Track email delivery'
        ],
    )
    
    # Get port and URL from environment
    port = int(os.getenv('PORT', '5004'))
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
    base_url = f'https://{railway_url}' if railway_url else f'http://localhost:{port}'
    
    # Create Agent Card
    agent_card = AgentCard(
        name='email_agent',
        version='1.0.0',
        description='Remote SaaS email service agent for sending, validating, and tracking emails',
        url=base_url,
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
        skills=[send_email_skill, validate_email_skill, check_status_skill],
    )
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=EmailAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A server application
    app = server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    # Build the Starlette app
    starlette_app = server.build()
    
    # Add health check endpoint for Railway
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    
    async def health_check(request):
        return JSONResponse({"status": "healthy", "service": "email-agent"})
    
    # Add health route to the app
    starlette_app.routes.append(Route('/health', health_check))
    
    print(f"📧 Email Agent (Remote SaaS) starting on {base_url}")
    print(f"📋 AgentCard: {base_url}/.well-known/agent.json")
    print(f"🏥 Health check: {base_url}/health")
    print("✨ This agent simulates a remote SaaS email service")
    if railway_url:
        print(f"🚀 Deployed on Railway: https://{railway_url}")
    else:
        print("🚀 Running locally - ready to be deployed to Railway.app!")
    
    # Start server
    uvicorn.run(starlette_app, host='0.0.0.0', port=port)

# Made with Bob
