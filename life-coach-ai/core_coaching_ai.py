"""
Core Coaching AI - Empathy, Active Listening, and Powerful Questioning
This module implements the heart of the Life Coach AI with emotional intelligence
and advanced conversational capabilities.
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class EmotionalState(Enum):
    """Detected emotional states from client communication"""
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    HOPEFUL = "hopeful"
    OVERWHELMED = "overwhelmed"
    MOTIVATED = "motivated"
    DISCOURAGED = "discouraged"
    PEACEFUL = "peaceful"


class QuestionType(Enum):
    """Types of coaching questions"""
    OPEN_ENDED = "open_ended"
    CLARIFYING = "clarifying"
    PROBING = "probing"
    REFLECTIVE = "reflective"
    SCALING = "scaling"
    MIRACLE = "miracle"
    CHALLENGING = "challenging"
    FUTURE_FOCUSED = "future_focused"
    VALUE_BASED = "value_based"


@dataclass
class ConversationContext:
    """Maintains context throughout a coaching conversation"""
    client_id: str
    session_id: str
    conversation_history: List[Dict] = field(default_factory=list)
    detected_emotions: List[EmotionalState] = field(default_factory=list)
    key_themes: List[str] = field(default_factory=list)
    client_values: List[str] = field(default_factory=list)
    energy_level: int = 5  # 1-10 scale
    openness_level: int = 5  # 1-10 scale

    def add_message(self, role: str, content: str, timestamp: datetime = None):
        """Add a message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': timestamp or datetime.now()
        })


class EmpathyEngine:
    """
    Generates empathetic responses that acknowledge emotions and build connection
    """

    EMPATHY_PATTERNS = {
        EmotionalState.FRUSTRATED: [
            "I can hear the frustration in what you're sharing. That sounds really challenging.",
            "It's completely understandable to feel frustrated in this situation.",
            "I sense this has been weighing on you. Thank you for sharing that with me."
        ],
        EmotionalState.EXCITED: [
            "Your excitement is wonderful to witness! This clearly means a lot to you.",
            "I can feel your energy and enthusiasm about this. That's fantastic!",
            "It's beautiful to see you light up when talking about this."
        ],
        EmotionalState.ANXIOUS: [
            "I hear the worry in your voice. These feelings are valid.",
            "Anxiety around this makes complete sense given what you're facing.",
            "It's okay to feel uncertain. Let's explore this together."
        ],
        EmotionalState.OVERWHELMED: [
            "It sounds like you're carrying a lot right now. I'm here with you.",
            "Feeling overwhelmed is a signal. Let's take this one step at a time.",
            "That's a lot on your plate. How can we break this down together?"
        ],
        EmotionalState.DISCOURAGED: [
            "I hear that you're feeling discouraged. That takes courage to acknowledge.",
            "Sometimes the path forward isn't clear, and that's hard. I'm here with you.",
            "It's okay to feel this way. Let's explore what's beneath this feeling."
        ],
        EmotionalState.HOPEFUL: [
            "I can sense the hope in what you're sharing. That's a powerful place to be.",
            "Hope is a beautiful thing. Let's build on that energy.",
            "I love hearing the possibility in your words."
        ]
    }

    @staticmethod
    def detect_emotion(text: str) -> List[EmotionalState]:
        """
        Analyze text to detect emotional states using keyword patterns
        """
        emotions = []
        text_lower = text.lower()

        emotion_keywords = {
            EmotionalState.FRUSTRATED: ['frustrated', 'annoying', 'stuck', 'can\'t', 'difficult', 'hard'],
            EmotionalState.EXCITED: ['excited', 'amazing', 'love', 'great', 'fantastic', 'wonderful'],
            EmotionalState.ANXIOUS: ['worried', 'anxious', 'nervous', 'scared', 'afraid', 'uncertain'],
            EmotionalState.OVERWHELMED: ['overwhelmed', 'too much', 'can\'t handle', 'drowning', 'buried'],
            EmotionalState.DISCOURAGED: ['discouraged', 'giving up', 'pointless', 'hopeless', 'defeated'],
            EmotionalState.HOPEFUL: ['hope', 'hopeful', 'maybe', 'possibility', 'could be', 'looking forward'],
            EmotionalState.CONFIDENT: ['confident', 'ready', 'capable', 'can do', 'strong', 'sure'],
            EmotionalState.MOTIVATED: ['motivated', 'driven', 'determined', 'committed', 'focused']
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)

        return emotions if emotions else [EmotionalState.UNCERTAIN]

    @staticmethod
    def generate_empathetic_response(emotion: EmotionalState) -> str:
        """Generate an empathetic response based on detected emotion"""
        import random
        patterns = EmpathyEngine.EMPATHY_PATTERNS.get(
            emotion,
            ["I hear you. Tell me more about what you're experiencing."]
        )
        return random.choice(patterns)

    @staticmethod
    def validate_feelings(text: str) -> str:
        """Create a validating response to client's feelings"""
        validations = [
            "Your feelings are completely valid.",
            "It makes perfect sense that you'd feel this way.",
            "Anyone in your situation would feel similarly.",
            "Thank you for trusting me with these feelings.",
            "There's no right or wrong way to feel about this."
        ]
        import random
        return random.choice(validations)


class ActiveListeningEngine:
    """
    Implements active listening techniques including reflection, paraphrasing,
    and summarization
    """

    @staticmethod
    def reflect_content(client_message: str) -> str:
        """
        Reflect back what was heard to ensure understanding
        """
        reflection_starters = [
            f"So what I'm hearing is that {client_message.lower()}",
            f"It sounds like {client_message.lower()}",
            f"If I understand correctly, {client_message.lower()}",
            f"Let me make sure I understand - {client_message.lower()}",
        ]
        import random
        return random.choice(reflection_starters)

    @staticmethod
    def paraphrase(key_points: List[str]) -> str:
        """
        Paraphrase client's key points to show understanding
        """
        if not key_points:
            return "Tell me more about what's on your mind."

        if len(key_points) == 1:
            return f"So the main thing you're focusing on is {key_points[0]}."

        points_str = ", ".join(key_points[:-1]) + f", and {key_points[-1]}"
        return f"I'm hearing several important things: {points_str}."

    @staticmethod
    def summarize_session(conversation_history: List[Dict]) -> str:
        """
        Create a summary of the coaching session
        """
        if len(conversation_history) < 2:
            return "We're just getting started with our conversation."

        client_messages = [
            msg['content'] for msg in conversation_history
            if msg['role'] == 'client'
        ]

        summary = f"In our session today, we've explored {len(client_messages)} important areas. "
        summary += "The key themes that emerged include your growth, challenges you're facing, "
        summary += "and the possibilities ahead of you."

        return summary

    @staticmethod
    def extract_key_words(text: str) -> List[str]:
        """Extract key words and themes from client's message"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'was', 'am', 'are', 'been', 'being', 'i', 'you',
                     'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her'}

        words = re.findall(r'\b\w+\b', text.lower())
        key_words = [w for w in words if w not in stop_words and len(w) > 3]

        # Return unique words, prioritizing longer words
        return sorted(set(key_words), key=lambda x: -len(x))[:5]


class PowerfulQuestioningEngine:
    """
    Generates powerful coaching questions that promote insight and self-discovery
    """

    QUESTION_BANK = {
        QuestionType.OPEN_ENDED: [
            "What would you like to explore in our session today?",
            "Tell me more about what's really important to you here.",
            "What does success look like for you in this area?",
            "How would you describe where you are right now?",
            "What's alive for you in this moment?"
        ],
        QuestionType.CLARIFYING: [
            "What do you mean by that?",
            "Can you give me an example?",
            "Help me understand what that looks like for you.",
            "What specifically are you referring to?",
            "When you say {keyword}, what does that mean to you?"
        ],
        QuestionType.PROBING: [
            "What's beneath that?",
            "What else is there?",
            "What are you not saying?",
            "What would happen if you did nothing?",
            "What's the real challenge here for you?"
        ],
        QuestionType.REFLECTIVE: [
            "What are you learning about yourself?",
            "How does this connect to your values?",
            "What does this reveal about what matters to you?",
            "Looking back, what do you notice?",
            "What patterns do you see?"
        ],
        QuestionType.SCALING: [
            "On a scale of 1-10, where are you right now?",
            "What would it take to move from a {current} to a {target}?",
            "What does a 10 look like for you?",
            "What's working that keeps you at a {current} instead of lower?",
            "What would be different at one level higher?"
        ],
        QuestionType.MIRACLE: [
            "If a miracle happened tonight and this was resolved, what would you notice first?",
            "Imagine it's a year from now and you've achieved this goal - what's different?",
            "If you could wave a magic wand, what would change?",
            "What would your best self do in this situation?",
            "If fear wasn't a factor, what would you do?"
        ],
        QuestionType.CHALLENGING: [
            "What's the story you're telling yourself about this?",
            "What would be possible if that weren't true?",
            "What are you tolerating?",
            "What's it costing you to stay where you are?",
            "What are you afraid might happen if you succeed?"
        ],
        QuestionType.FUTURE_FOCUSED: [
            "What do you want to create?",
            "What's your next step?",
            "What will you do differently going forward?",
            "When will you start?",
            "What support do you need to make this happen?"
        ],
        QuestionType.VALUE_BASED: [
            "What matters most to you about this?",
            "What values are you honoring by pursuing this?",
            "What kind of person do you want to be in this situation?",
            "What legacy do you want to leave?",
            "What would make you proud?"
        ]
    }

    @staticmethod
    def generate_question(question_type: QuestionType, context: Dict = None) -> str:
        """Generate a powerful coaching question based on type and context"""
        import random
        questions = PowerfulQuestioningEngine.QUESTION_BANK[question_type]
        question = random.choice(questions)

        # Fill in context variables if provided
        if context:
            question = question.format(**context)

        return question

    @staticmethod
    def follow_up_question(client_response: str) -> str:
        """Generate an appropriate follow-up question based on client's response"""
        emotions = EmpathyEngine.detect_emotion(client_response)

        # Choose question type based on emotion
        if EmotionalState.UNCERTAIN in emotions:
            return PowerfulQuestioningEngine.generate_question(QuestionType.CLARIFYING)
        elif EmotionalState.EXCITED in emotions:
            return PowerfulQuestioningEngine.generate_question(QuestionType.FUTURE_FOCUSED)
        elif EmotionalState.FRUSTRATED in emotions or EmotionalState.OVERWHELMED in emotions:
            return PowerfulQuestioningEngine.generate_question(QuestionType.PROBING)
        else:
            return PowerfulQuestioningEngine.generate_question(QuestionType.OPEN_ENDED)

    @staticmethod
    def create_question_sequence(goal: str) -> List[str]:
        """Create a sequence of questions to explore a goal deeply"""
        return [
            f"Tell me about what achieving '{goal}' would mean to you.",
            PowerfulQuestioningEngine.generate_question(QuestionType.VALUE_BASED),
            PowerfulQuestioningEngine.generate_question(QuestionType.SCALING),
            PowerfulQuestioningEngine.generate_question(QuestionType.MIRACLE),
            PowerfulQuestioningEngine.generate_question(QuestionType.FUTURE_FOCUSED)
        ]


class CoachingConversationAI:
    """
    Main coaching conversation AI that brings together empathy, active listening,
    and powerful questioning
    """

    def __init__(self, coach_name: str = "Your Coach"):
        self.coach_name = coach_name
        self.empathy_engine = EmpathyEngine()
        self.listening_engine = ActiveListeningEngine()
        self.questioning_engine = PowerfulQuestioningEngine()

    def respond_to_client(self,
                          client_message: str,
                          context: ConversationContext) -> Dict[str, any]:
        """
        Generate a complete coaching response with empathy, reflection, and questions
        """
        # Detect emotions
        emotions = self.empathy_engine.detect_emotion(client_message)
        context.detected_emotions.extend(emotions)

        # Extract key themes
        key_words = self.listening_engine.extract_key_words(client_message)
        context.key_themes.extend(key_words)

        # Add to conversation history
        context.add_message('client', client_message)

        # Build response components
        response_parts = []

        # 1. Empathetic acknowledgment
        if emotions and emotions[0] in self.empathy_engine.EMPATHY_PATTERNS:
            empathy_response = self.empathy_engine.generate_empathetic_response(emotions[0])
            response_parts.append(empathy_response)

        # 2. Active listening reflection
        if len(client_message.split()) > 10:  # Only reflect on substantial messages
            reflection = self.listening_engine.reflect_content(
                " ".join(client_message.split()[:15]) + "..."
            )
            response_parts.append(reflection)

        # 3. Powerful question
        question = self.questioning_engine.follow_up_question(client_message)
        response_parts.append(question)

        # Combine response parts
        full_response = " ".join(response_parts)

        # Add to conversation history
        context.add_message('coach', full_response)

        return {
            'response': full_response,
            'detected_emotions': emotions,
            'key_themes': key_words,
            'suggested_next_questions': self.questioning_engine.create_question_sequence(
                key_words[0] if key_words else "your goal"
            )
        }

    def open_session(self, client_name: str, session_focus: Optional[str] = None) -> str:
        """Generate a warm opening for a coaching session"""
        openings = [
            f"Hello {client_name}, it's wonderful to connect with you today. ",
            f"Welcome {client_name}, I'm glad we have this time together. ",
            f"Hi {client_name}, thank you for being here. "
        ]

        import random
        opening = random.choice(openings)

        if session_focus:
            opening += f"I understand you'd like to focus on {session_focus}. "

        opening += "What would make this session valuable for you?"

        return opening

    def close_session(self, context: ConversationContext) -> str:
        """Generate a meaningful session closing with summary and next steps"""
        closing = f"As we close our session today, let me reflect on what we've explored together. "

        # Summarize
        summary = self.listening_engine.summarize_session(context.conversation_history)
        closing += summary + " "

        # Acknowledge growth
        closing += "I've witnessed your courage and willingness to explore deeply. "

        # Future focus
        closing += "What's one thing you're taking away from our session today? "
        closing += "And what's one action you're committed to before we meet next?"

        return closing

    def celebrate_progress(self, achievement: str) -> str:
        """Celebrate client's progress with genuine enthusiasm"""
        celebrations = [
            f"This is wonderful! {achievement} - I'm so proud of the work you've done.",
            f"Look at what you've accomplished: {achievement}! This is significant progress.",
            f"I want to take a moment to celebrate this with you: {achievement}. You should be really proud.",
            f"This is worth acknowledging: {achievement}. You've come so far!",
            f"Amazing! {achievement}. Do you see how far you've come?"
        ]

        import random
        return random.choice(celebrations)

    def provide_accountability(self, commitment: str, client_name: str) -> str:
        """Create accountability around a commitment"""
        accountability = f"{client_name}, I heard you commit to: {commitment}. "
        accountability += "This is important. What will help you stay accountable? "
        accountability += "How will you know you've succeeded? "
        accountability += "And what support do you need from me?"

        return accountability

    def handle_resistance(self, resistance_pattern: str) -> str:
        """Gently address resistance or stuck patterns"""
        responses = [
            "I notice there might be some resistance here. That's completely normal. What do you think that's about?",
            "It seems like there's something holding you back. What's the hesitation?",
            "I'm curious - what would need to be different for you to feel ready to move forward?",
            "Sometimes resistance is wisdom. What is this resistance trying to protect you from?",
            "What's the payoff for staying where you are?"
        ]

        import random
        return random.choice(responses)

    def deepen_insight(self, topic: str) -> List[str]:
        """Generate a series of questions to deepen insight on a topic"""
        return [
            f"What's really important to you about {topic}?",
            f"What would change if you approached {topic} differently?",
            f"What's your intuition telling you about {topic}?",
            f"If {topic} were completely resolved, what would be possible for you?",
            f"What are you learning about yourself through {topic}?"
        ]
