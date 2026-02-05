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
    
    # Create Agent Card
    agent_card = AgentCard(
        name='email_agent',
        version='1.0.0',
        description='Remote SaaS email service agent for sending, validating, and tracking emails',
        url='http://localhost:5004',  # Will be updated to Railway URL after deployment
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
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    print("📧 Email Agent (Remote SaaS) starting on http://localhost:5004")
    print("📋 AgentCard: http://localhost:5004/.well-known/agent.json")
    print("✨ This agent simulates a remote SaaS email service")
    print("🚀 Ready to be deployed to Railway.app!")
    
    # Start server
    uvicorn.run(server.build(), host='0.0.0.0', port=5004)

# Made with Bob
