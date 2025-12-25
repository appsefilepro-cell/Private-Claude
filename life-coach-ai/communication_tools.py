"""
Communication Tools
Email templates, messaging, and client communication management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class CommunicationType(Enum):
    """Types of communications"""
    WELCOME = "welcome"
    SESSION_CONFIRMATION = "session_confirmation"
    SESSION_REMINDER = "session_reminder"
    FOLLOW_UP = "follow_up"
    CHECK_IN = "check_in"
    ACCOUNTABILITY = "accountability"
    CELEBRATION = "celebration"
    RESOURCE_SHARING = "resource_sharing"
    CANCELLATION = "cancellation"
    RESCHEDULING = "rescheduling"
    PACKAGE_COMPLETION = "package_completion"
    MONTHLY_UPDATE = "monthly_update"


@dataclass
class CommunicationTemplate:
    """Template for client communications"""
    template_id: str
    name: str
    type: CommunicationType
    subject: str
    body: str
    variables: List[str] = field(default_factory=list)  # e.g., {client_name}, {date}, etc.

    def render(self, variables: Dict[str, str]) -> Dict[str, str]:
        """Render template with variables"""
        subject = self.subject
        body = self.body

        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            subject = subject.replace(placeholder, str(var_value))
            body = body.replace(placeholder, str(var_value))

        return {
            'subject': subject,
            'body': body
        }


class CommunicationLibrary:
    """
    Library of communication templates for various coaching scenarios
    """

    @staticmethod
    def get_welcome_email() -> CommunicationTemplate:
        """Welcome email for new clients"""
        return CommunicationTemplate(
            template_id="welcome_001",
            name="New Client Welcome",
            type=CommunicationType.WELCOME,
            subject="Welcome to Your Coaching Journey, {client_name}!",
            body="""
Dear {client_name},

Welcome! I'm so excited to begin this coaching journey with you.

I'm honored that you've chosen to invest in yourself and your growth. Coaching is a powerful partnership, and I'm committed to supporting you in achieving the goals that matter most to you.

Here's what you can expect from our work together:

• A safe, confidential space for exploration and growth
• Powerful questions that promote insight and clarity
• Accountability and support for the changes you want to make
• Celebration of your wins, both big and small
• Honest, compassionate partnership

Our first session is scheduled for {session_date} at {session_time}. In this discovery session, we'll:
- Get to know each other
- Explore what you want to focus on
- Clarify your goals and desired outcomes
- Create a plan for our work together

To make the most of our first session, please take some time to reflect on:
1. What brought you to coaching at this time?
2. What would make our work together successful?
3. What areas of your life do you want to focus on?

I look forward to connecting with you soon!

Warm regards,
{coach_name}

P.S. If you have any questions before our session, please don't hesitate to reach out.
"""
        )

    @staticmethod
    def get_session_reminder() -> CommunicationTemplate:
        """Session reminder email"""
        return CommunicationTemplate(
            template_id="reminder_001",
            name="Session Reminder",
            type=CommunicationType.SESSION_REMINDER,
            subject="Reminder: Coaching Session Tomorrow - {session_date}",
            body="""
Hi {client_name},

This is a friendly reminder about our coaching session:

Date: {session_date}
Time: {session_time}
Duration: {duration} minutes
Meeting Link: {meeting_link}

To prepare for our session, you might want to:
• Review any commitments from our last session
• Reflect on what you'd like to focus on
• Gather any questions or topics you want to explore

I'm looking forward to our time together!

See you soon,
{coach_name}
"""
        )

    @staticmethod
    def get_follow_up_email() -> CommunicationTemplate:
        """Post-session follow-up"""
        return CommunicationTemplate(
            template_id="followup_001",
            name="Session Follow-Up",
            type=CommunicationType.FOLLOW_UP,
            subject="Session Recap & Action Items - {session_date}",
            body="""
Hi {client_name},

Thank you for a wonderful session today! I loved witnessing your insights and commitment to growth.

Here's a brief recap of what we explored:

KEY INSIGHTS:
{key_insights}

YOUR COMMITMENTS:
{commitments}

RESOURCES SHARED:
{resources}

Remember: {encouraging_message}

Our next session is scheduled for {next_session_date} at {next_session_time}.

In the meantime, I'm here if you need anything.

Cheering you on,
{coach_name}
"""
        )

    @staticmethod
    def get_accountability_check_in() -> CommunicationTemplate:
        """Accountability check-in"""
        return CommunicationTemplate(
            template_id="accountability_001",
            name="Accountability Check-In",
            type=CommunicationType.ACCOUNTABILITY,
            subject="How's It Going? Quick Check-In",
            body="""
Hi {client_name},

I wanted to check in on how things are going with {goal_area}.

Last we spoke, you committed to: {commitment}

How's that coming along?

• What progress have you made?
• What challenges have you encountered?
• What support do you need?

No judgment - just curious and here to support you!

Quick reply appreciated so we can celebrate your wins or troubleshoot any obstacles.

Believing in you,
{coach_name}
"""
        )

    @staticmethod
    def get_celebration_email() -> CommunicationTemplate:
        """Celebration of wins"""
        return CommunicationTemplate(
            template_id="celebration_001",
            name="Celebration",
            type=CommunicationType.CELEBRATION,
            subject="Celebrating Your Win! 🎉",
            body="""
{client_name},

I have to take a moment to celebrate what you've accomplished!

{achievement}

Do you see how far you've come? This is HUGE!

{specific_observation}

I'm so proud of the work you're doing and the person you're becoming.

What are you most proud of about this accomplishment?

Celebrating with you,
{coach_name}

P.S. Don't forget to celebrate yourself too!
"""
        )

    @staticmethod
    def get_monthly_update() -> CommunicationTemplate:
        """Monthly progress update"""
        return CommunicationTemplate(
            template_id="monthly_001",
            name="Monthly Update",
            type=CommunicationType.MONTHLY_UPDATE,
            subject="Your Monthly Coaching Update - {month}",
            body="""
Hi {client_name},

As we close out {month}, I wanted to share a reflection on your coaching journey this month.

SESSIONS COMPLETED: {sessions_count}

GOALS WORKED ON:
{goals_list}

WINS & BREAKTHROUGHS:
{wins_list}

INSIGHTS EMERGING:
{insights_list}

FOCUS FOR NEXT MONTH:
{next_month_focus}

You're making real progress. Keep going!

Looking forward to continuing our work together.

{coach_name}
"""
        )

    @staticmethod
    def get_all_templates() -> Dict[str, CommunicationTemplate]:
        """Get all available templates"""
        return {
            'welcome': CommunicationLibrary.get_welcome_email(),
            'reminder': CommunicationLibrary.get_session_reminder(),
            'follow_up': CommunicationLibrary.get_follow_up_email(),
            'accountability': CommunicationLibrary.get_accountability_check_in(),
            'celebration': CommunicationLibrary.get_celebration_email(),
            'monthly': CommunicationLibrary.get_monthly_update()
        }


@dataclass
class Message:
    """A message to/from a client"""
    message_id: str
    client_id: str
    direction: str  # 'to_client' or 'from_client'
    subject: Optional[str]
    content: str
    communication_type: Optional[CommunicationType]
    sent_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    tags: List[str] = field(default_factory=list)


class CommunicationManager:
    """
    Manages all client communications
    """

    def __init__(self):
        self.templates = CommunicationLibrary.get_all_templates()
        self.messages: Dict[str, Message] = {}

    def create_message_from_template(self,
                                    template_name: str,
                                    client_id: str,
                                    variables: Dict[str, str]) -> Optional[Message]:
        """Create a message from a template"""
        template = self.templates.get(template_name)
        if not template:
            return None

        rendered = template.render(variables)

        import uuid
        message = Message(
            message_id=str(uuid.uuid4()),
            client_id=client_id,
            direction='to_client',
            subject=rendered['subject'],
            content=rendered['body'],
            communication_type=template.type
        )

        self.messages[message.message_id] = message
        return message

    def create_custom_message(self,
                            client_id: str,
                            subject: str,
                            content: str,
                            communication_type: Optional[CommunicationType] = None) -> Message:
        """Create a custom message"""
        import uuid
        message = Message(
            message_id=str(uuid.uuid4()),
            client_id=client_id,
            direction='to_client',
            subject=subject,
            content=content,
            communication_type=communication_type
        )

        self.messages[message.message_id] = message
        return message

    def get_client_messages(self, client_id: str) -> List[Message]:
        """Get all messages for a client"""
        return [
            msg for msg in self.messages.values()
            if msg.client_id == client_id
        ]

    def generate_session_recap(self,
                             client_name: str,
                             session_summary: Dict) -> str:
        """Generate a session recap message"""
        recap = f"Hi {client_name},\n\n"
        recap += "Thank you for a wonderful session today!\n\n"

        if session_summary.get('key_insights'):
            recap += "KEY INSIGHTS:\n"
            for insight in session_summary['key_insights']:
                recap += f"• {insight}\n"
            recap += "\n"

        if session_summary.get('commitments'):
            recap += "YOUR COMMITMENTS:\n"
            for commitment in session_summary['commitments']:
                recap += f"• {commitment}\n"
            recap += "\n"

        if session_summary.get('next_session'):
            recap += f"Next session: {session_summary['next_session']}\n\n"

        recap += "Keep up the great work!\n\n"
        recap += "Warmly,\nYour Coach"

        return recap
