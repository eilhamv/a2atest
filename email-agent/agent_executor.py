from typing_extensions import override
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
import re
import uuid
from datetime import datetime


class EmailAgent:
    """Mock email agent simulating SaaS email service (like SendGrid/Mailgun)"""
    
    def __init__(self):
        # Mock email storage for demo purposes
        self.sent_emails = {}
    
    async def send_email(self, query: str) -> str:
        """Send an email (mock implementation)"""
        try:
            # Extract email details from query
            # Pattern: "send email to john@example.com with subject Hello and message Hi there"
            query_lower = query.lower()
            
            # Extract recipient
            to_match = re.search(r'(?:to|recipient)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query)
            if not to_match:
                return "❌ Please specify recipient email (e.g., 'send email to john@example.com')"
            
            recipient = to_match.group(1)
            
            # Extract subject
            subject_match = re.search(r'(?:subject|title)\s+([^,\.]+?)(?:\s+(?:and|with|message|body)|$)', query, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else "No Subject"
            
            # Extract message/body
            message_match = re.search(r'(?:message|body|text)\s+(.+?)(?:\s*$)', query, re.IGNORECASE)
            message = message_match.group(1).strip() if message_match else "No message body"
            
            # Generate email ID
            email_id = f"email_{uuid.uuid4().hex[:8]}"
            
            # Store email (mock)
            self.sent_emails[email_id] = {
                'to': recipient,
                'subject': subject,
                'message': message,
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
                'delivery_status': 'delivered'
            }
            
            return f"✅ Email sent successfully!\n\n📧 Email ID: {email_id}\n📨 To: {recipient}\n📝 Subject: {subject}\n💬 Message: {message}\n⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✨ This is a mock email service (SaaS simulation)"
            
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
    
    async def validate_email(self, query: str) -> str:
        """Validate email address format"""
        try:
            # Extract email from query
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', query)
            
            if not email_match:
                return "❌ No email address found in query. Please provide an email to validate."
            
            email = email_match.group(1)
            
            # Basic validation
            if '@' not in email or '.' not in email.split('@')[1]:
                return f"❌ Invalid email format: {email}"
            
            # Check common domains
            domain = email.split('@')[1]
            common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'example.com']
            is_common = domain in common_domains
            
            return f"✅ Email validation result:\n\n📧 Email: {email}\n✓ Format: Valid\n🌐 Domain: {domain}\n{'⭐ Common provider' if is_common else '📍 Custom domain'}\n\n✨ This is a mock validation service"
            
        except Exception as e:
            return f"❌ Error validating email: {str(e)}"
    
    async def check_status(self, query: str) -> str:
        """Check email delivery status"""
        try:
            # Extract email ID from query
            id_match = re.search(r'email_[a-f0-9]{8}', query)
            
            if not id_match:
                # Show recent emails if no ID provided
                if not self.sent_emails:
                    return "📭 No emails sent yet. Send an email first!"
                
                recent = list(self.sent_emails.items())[-3:]  # Last 3 emails
                result = "📊 Recent email status:\n\n"
                for email_id, details in recent:
                    result += f"📧 {email_id}\n"
                    result += f"   To: {details['to']}\n"
                    result += f"   Status: {details['status']} ✅\n"
                    result += f"   Delivery: {details['delivery_status']}\n\n"
                return result + "💡 Tip: Use 'check status email_xxxxx' to check specific email"
            
            email_id = id_match.group(0)
            
            if email_id not in self.sent_emails:
                return f"❌ Email ID '{email_id}' not found. It may have been sent from a different session."
            
            details = self.sent_emails[email_id]
            
            return f"📊 Email Status Report:\n\n📧 Email ID: {email_id}\n📨 To: {details['to']}\n📝 Subject: {details['subject']}\n✅ Status: {details['status']}\n📬 Delivery: {details['delivery_status']}\n⏰ Sent: {details['timestamp']}\n\n✨ This is a mock status check service"
            
        except Exception as e:
            return f"❌ Error checking status: {str(e)}"
    
    async def process_query(self, query: str) -> str:
        """Route query to appropriate email method"""
        query_lower = query.lower()
        
        # Check for send email
        if 'send' in query_lower and ('email' in query_lower or 'mail' in query_lower):
            return await self.send_email(query)
        
        # Check for validate email
        if 'validate' in query_lower or 'check' in query_lower and 'valid' in query_lower:
            return await self.validate_email(query)
        
        # Check for status check
        if 'status' in query_lower or 'delivery' in query_lower or 'track' in query_lower:
            return await self.check_status(query)
        
        # Default help message
        return """📧 Email Agent - Available Commands:

1️⃣ Send Email:
   "send email to john@example.com with subject Hello and message Hi there"

2️⃣ Validate Email:
   "validate email john@example.com"

3️⃣ Check Status:
   "check status email_xxxxx" or "check delivery status"

✨ This is a mock SaaS email service for demonstration purposes."""


class EmailAgentExecutor(AgentExecutor):
    """A2A AgentExecutor implementation for email agent"""
    
    def __init__(self):
        self.agent = EmailAgent()
    
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

# Made with Bob
