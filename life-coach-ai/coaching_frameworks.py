"""
Coaching Frameworks
Implementation of proven coaching models and tools
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class LifeArea(Enum):
    """Life areas for Wheel of Life"""
    CAREER = "career"
    FINANCES = "finances"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    PERSONAL_GROWTH = "personal_growth"
    FUN_RECREATION = "fun_recreation"
    PHYSICAL_ENVIRONMENT = "physical_environment"
    CONTRIBUTION = "contribution"


@dataclass
class GROWModel:
    """
    GROW Model - Goal, Reality, Options, Will
    One of the most widely used coaching frameworks
    """
    session_id: str
    client_id: str

    # G - Goal
    goal: str = ""
    goal_details: str = ""
    desired_outcome: str = ""
    success_criteria: str = ""

    # R - Reality
    current_situation: str = ""
    whats_happening_now: str = ""
    whats_been_tried: List[str] = field(default_factory=list)
    obstacles: List[str] = field(default_factory=list)
    resources_available: List[str] = field(default_factory=list)

    # O - Options
    possible_actions: List[str] = field(default_factory=list)
    brainstormed_ideas: List[str] = field(default_factory=list)
    creative_solutions: List[str] = field(default_factory=list)
    best_options: List[str] = field(default_factory=list)

    # W - Will (Way Forward)
    chosen_action: str = ""
    specific_steps: List[str] = field(default_factory=list)
    timeline: str = ""
    commitment_level: int = 0  # 1-10 scale
    support_needed: List[str] = field(default_factory=list)
    accountability_plan: str = ""

    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def get_goal_questions() -> List[str]:
        """Questions for the Goal phase"""
        return [
            "What would you like to focus on in this session?",
            "What would you like to achieve?",
            "What does success look like?",
            "How will you know when you've achieved it?",
            "What would make this session valuable for you?",
            "Is this goal within your control?",
            "On a scale of 1-10, how important is this goal to you?"
        ]

    @staticmethod
    def get_reality_questions() -> List[str]:
        """Questions for the Reality phase"""
        return [
            "What's happening now?",
            "What have you tried so far?",
            "What's working? What's not working?",
            "What obstacles are you facing?",
            "Who else is involved?",
            "What resources do you have available?",
            "On a scale of 1-10, where are you now?",
            "What's really going on here?",
            "What's beneath that?"
        ]

    @staticmethod
    def get_options_questions() -> List[str]:
        """Questions for the Options phase"""
        return [
            "What could you do?",
            "What else?",
            "If anything were possible, what would you do?",
            "What would you do if you had unlimited resources?",
            "What would you advise a friend to do?",
            "What if fear wasn't a factor?",
            "What are all the possible ways forward?",
            "Which options appeal to you most?",
            "What are the pros and cons of each option?"
        ]

    @staticmethod
    def get_will_questions() -> List[str]:
        """Questions for the Way Forward phase"""
        return [
            "What will you do?",
            "When will you do it?",
            "What's your first step?",
            "What support do you need?",
            "How committed are you to this action? (1-10)",
            "What might get in the way?",
            "How will you overcome obstacles?",
            "How will you know you've succeeded?",
            "What accountability would be helpful?",
            "On a scale of 1-10, how likely are you to complete this?"
        ]


@dataclass
class WheelOfLife:
    """
    Wheel of Life Assessment
    Visual tool for evaluating life balance and satisfaction
    """
    assessment_id: str
    client_id: str
    assessment_date: datetime = field(default_factory=datetime.now)

    # Scores for each life area (1-10 scale)
    scores: Dict[LifeArea, int] = field(default_factory=dict)

    # Additional context for each area
    area_notes: Dict[LifeArea, str] = field(default_factory=dict)
    satisfaction_reasons: Dict[LifeArea, str] = field(default_factory=dict)
    improvement_ideas: Dict[LifeArea, List[str]] = field(default_factory=dict)

    # Overall insights
    strongest_areas: List[LifeArea] = field(default_factory=list)
    areas_for_growth: List[LifeArea] = field(default_factory=list)
    overall_balance_score: float = 0.0
    key_insights: List[str] = field(default_factory=list)

    def set_score(self, area: LifeArea, score: int, note: str = ""):
        """Set score for a life area"""
        self.scores[area] = max(1, min(10, score))
        if note:
            self.area_notes[area] = note
        self._calculate_insights()

    def _calculate_insights(self):
        """Calculate overall insights from scores"""
        if not self.scores:
            return

        # Calculate average score
        self.overall_balance_score = sum(self.scores.values()) / len(self.scores)

        # Identify strongest areas (8-10)
        self.strongest_areas = [
            area for area, score in self.scores.items()
            if score >= 8
        ]

        # Identify areas for growth (1-5)
        self.areas_for_growth = [
            area for area, score in self.scores.items()
            if score <= 5
        ]

    def get_report(self) -> str:
        """Generate a Wheel of Life report"""
        report = "WHEEL OF LIFE ASSESSMENT\n"
        report += "=" * 50 + "\n\n"
        report += f"Date: {self.assessment_date.strftime('%B %d, %Y')}\n"
        report += f"Overall Balance Score: {self.overall_balance_score:.1f}/10\n\n"

        report += "LIFE AREA SCORES:\n"
        report += "-" * 50 + "\n"

        for area in LifeArea:
            if area in self.scores:
                score = self.scores[area]
                report += f"{area.value.replace('_', ' ').title():.<30} {score}/10\n"

                if area in self.area_notes:
                    report += f"  Note: {self.area_notes[area]}\n"

        if self.strongest_areas:
            report += "\nSTRONGEST AREAS:\n"
            for area in self.strongest_areas:
                report += f"  - {area.value.replace('_', ' ').title()}\n"

        if self.areas_for_growth:
            report += "\nAREAS FOR GROWTH:\n"
            for area in self.areas_for_growth:
                report += f"  - {area.value.replace('_', ' ').title()}\n"

        if self.key_insights:
            report += "\nKEY INSIGHTS:\n"
            for insight in self.key_insights:
                report += f"  - {insight}\n"

        return report

    @staticmethod
    def get_assessment_questions(area: LifeArea) -> List[str]:
        """Get coaching questions for each life area"""
        return [
            f"On a scale of 1-10, how satisfied are you with your {area.value.replace('_', ' ')}?",
            f"What's working well in this area?",
            f"What would make this a 10?",
            f"What's one thing you could do to improve this area?",
            f"What's the cost of leaving this area as it is?"
        ]


@dataclass
class ValuesElicitation:
    """
    Values Elicitation Exercise
    Help clients identify and clarify their core values
    """
    client_id: str

    # Identified values
    core_values: List[str] = field(default_factory=list)  # Top 3-5 values
    important_values: List[str] = field(default_factory=list)  # Other important values

    # Value definitions (what each value means to the client)
    value_definitions: Dict[str, str] = field(default_factory=dict)

    # How values show up
    values_in_action: Dict[str, List[str]] = field(default_factory=dict)
    values_being_honored: List[str] = field(default_factory=list)
    values_being_compromised: List[str] = field(default_factory=list)

    # Insights
    value_conflicts: List[str] = field(default_factory=list)
    alignment_insights: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def common_values() -> List[str]:
        """List of common values to explore"""
        return [
            "Achievement", "Adventure", "Authenticity", "Balance", "Compassion",
            "Courage", "Creativity", "Family", "Freedom", "Growth",
            "Health", "Honesty", "Integrity", "Joy", "Kindness",
            "Learning", "Love", "Peace", "Security", "Service",
            "Spirituality", "Success", "Wisdom", "Connection", "Independence"
        ]

    @staticmethod
    def get_values_questions() -> List[str]:
        """Questions to elicit values"""
        return [
            "What matters most to you in life?",
            "What do you stand for?",
            "When have you felt most fulfilled? What values were you honoring?",
            "What makes you angry or frustrated? (Often indicates a value being violated)",
            "What do you admire in others?",
            "What do you want to be remembered for?",
            "If you could only keep 5 values, which would they be?",
            "How do these values show up in your daily life?",
            "Where are your values being honored? Where are they being compromised?"
        ]


@dataclass
class MiraclQuestion:
    """
    Miracle Question Technique
    Solution-focused coaching tool
    """
    client_id: str
    session_id: str

    # The miracle question response
    miracle_scenario: str = ""

    # What would be different
    first_signs: List[str] = field(default_factory=list)
    what_changes: List[str] = field(default_factory=list)
    who_notices: List[str] = field(default_factory=list)
    feelings_different: List[str] = field(default_factory=list)

    # Current reality
    whats_already_happening: List[str] = field(default_factory=list)  # Parts of the miracle already present
    small_steps_toward_miracle: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def get_miracle_question() -> str:
        """The classic miracle question"""
        return """
Imagine that tonight, while you're sleeping, a miracle happens.
The problem that brought you here is completely resolved.
But because you were sleeping, you don't know that the miracle has happened.

When you wake up tomorrow morning, what will be the first small sign that tells you
that this miracle has occurred? What will be different?
"""

    @staticmethod
    def get_follow_up_questions() -> List[str]:
        """Follow-up questions for miracle question"""
        return [
            "What's the first thing you would notice?",
            "What would others notice about you?",
            "How would you feel differently?",
            "What would you be doing differently?",
            "On a scale of 1-10, where are you now in relation to this miracle?",
            "What's already happening that's part of this miracle?",
            "What would be the smallest step toward this miracle?",
            "What would need to happen to move from a 3 to a 4?"
        ]


@dataclass
class ScalingQuestion:
    """
    Scaling Questions Framework
    Powerful tool for measuring progress and generating insight
    """
    question: str
    current_score: int  # 1-10
    target_score: int = 10

    # Understanding the current score
    whats_working: List[str] = field(default_factory=list)
    why_not_lower: str = ""
    what_represents_current: str = ""

    # Moving forward
    next_level_up: str = ""  # What would a 5 look like if current is 4?
    what_would_help: List[str] = field(default_factory=list)
    small_steps: List[str] = field(default_factory=list)

    # Target score
    what_represents_target: str = ""
    what_would_be_different: str = ""

    @staticmethod
    def create_scaling_questions() -> List[str]:
        """Common scaling questions"""
        return [
            "On a scale of 1-10, how confident are you about achieving this goal?",
            "On a scale of 1-10, how satisfied are you with [area of life]?",
            "On a scale of 1-10, how motivated are you right now?",
            "On a scale of 1-10, how much progress have you made?",
            "On a scale of 1-10, how aligned is this with your values?",
            "On a scale of 1-10, how committed are you to taking action?",
            "On a scale of 1-10, where would you like to be in 3 months?"
        ]

    @staticmethod
    def get_exploration_questions(current_score: int) -> List[str]:
        """Questions to explore the scale"""
        next_score = current_score + 1
        return [
            f"What makes you a {current_score} and not a {current_score - 1}?",
            f"What's working that keeps you at a {current_score}?",
            f"What would a {next_score} look like?",
            f"What would need to happen to move from a {current_score} to a {next_score}?",
            f"What's the smallest step you could take to move up the scale?",
            "What would a 10 look like for you?",
            "When have you been at a higher number? What was different then?"
        ]


class CoachingFrameworkLibrary:
    """
    Library of coaching frameworks and tools
    """

    @staticmethod
    def get_framework_description(framework_name: str) -> str:
        """Get description of a coaching framework"""
        descriptions = {
            "GROW": "Goal, Reality, Options, Will - A structured model for problem-solving and goal achievement",
            "Wheel of Life": "Visual assessment tool for evaluating life balance across key areas",
            "Values Elicitation": "Process for identifying and clarifying core values",
            "Miracle Question": "Solution-focused technique for envisioning desired outcomes",
            "Scaling Questions": "Tool for measuring progress and generating actionable insights",
            "SMART Goals": "Specific, Measurable, Achievable, Relevant, Time-bound goal setting",
            "SOAR": "Strengths, Opportunities, Aspirations, Results - Appreciative inquiry approach",
            "Johari Window": "Self-awareness tool for exploring known/unknown aspects of self",
            "Eisenhower Matrix": "Prioritization tool based on urgency and importance",
            "SWOT": "Strengths, Weaknesses, Opportunities, Threats analysis"
        }
        return descriptions.get(framework_name, "Framework description not available")

    @staticmethod
    def recommend_framework(client_need: str) -> List[str]:
        """Recommend frameworks based on client need"""
        recommendations = {
            "goal_setting": ["GROW", "SMART Goals", "Scaling Questions"],
            "life_balance": ["Wheel of Life", "Values Elicitation"],
            "problem_solving": ["GROW", "SWOT", "Scaling Questions"],
            "vision_clarity": ["Miracle Question", "Values Elicitation", "SOAR"],
            "decision_making": ["Values Elicitation", "SWOT", "Eisenhower Matrix"],
            "progress_tracking": ["Scaling Questions", "SMART Goals"],
            "self_awareness": ["Values Elicitation", "Johari Window", "Wheel of Life"]
        }

        need_lower = client_need.lower()
        for key, frameworks in recommendations.items():
            if key in need_lower:
                return frameworks

        return ["GROW", "Scaling Questions"]  # Default recommendations
