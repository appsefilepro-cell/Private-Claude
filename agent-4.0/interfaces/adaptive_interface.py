"""
Adaptive Interface System for Agent 4.0 Advanced
Automatically detects user skill level and provides appropriate interface
"""

import os
import json
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """User skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    NON_CODER = "non_coder"
    PYTHON_DEVELOPER = "python_developer"
    AI_DEVELOPER = "ai_developer"
    CFO_DEEP_SYNC = "cfo_deep_sync"


class InterfaceType(Enum):
    """Available interface types"""
    SIMPLE_GUI = "simple_gui"
    GUI_WITH_CUSTOMIZATION = "gui_with_customization"
    ADVANCED_GUI_WITH_API = "advanced_gui_with_api"
    FULL_API_CODE_ACCESS = "full_api_code_access"
    ADAPTIVE_ALL_LEVELS = "adaptive_all_levels"
    ROLE_BASED_ADAPTIVE = "role_based_adaptive"


@dataclass
class UserProfile:
    """User profile information"""
    user_id: str
    skill_level: SkillLevel
    preferred_interface: InterfaceType
    device_type: str = "desktop"
    remote_access: bool = False
    voice_enabled: bool = False
    accessibility_needs: List[str] = None


class SkillDetector:
    """Detects user skill level based on interaction patterns"""
    
    def __init__(self):
        self.interaction_history = []
    
    def detect_skill_level(self, user_actions: List[Dict]) -> SkillLevel:
        """
        Detect skill level based on user actions
        
        Args:
            user_actions: List of user action dictionaries
            
        Returns:
            Detected skill level
        """
        if not user_actions:
            return SkillLevel.BEGINNER
        
        # Analyze actions to determine skill level
        code_actions = sum(1 for a in user_actions if a.get('type') == 'code')
        api_actions = sum(1 for a in user_actions if a.get('type') == 'api')
        gui_actions = sum(1 for a in user_actions if a.get('type') == 'gui')
        
        total_actions = len(user_actions)
        
        if code_actions / total_actions > 0.7:
            return SkillLevel.EXPERT
        elif api_actions / total_actions > 0.5:
            return SkillLevel.ADVANCED
        elif gui_actions / total_actions > 0.8:
            return SkillLevel.BEGINNER
        else:
            return SkillLevel.INTERMEDIATE
    
    def detect_role(self, user_preferences: Dict) -> Optional[SkillLevel]:
        """Detect specialized role based on user preferences"""
        if user_preferences.get('no_coding_required'):
            return SkillLevel.NON_CODER
        elif user_preferences.get('python_focused'):
            return SkillLevel.PYTHON_DEVELOPER
        elif user_preferences.get('ml_focused'):
            return SkillLevel.AI_DEVELOPER
        elif user_preferences.get('financial_focused'):
            return SkillLevel.CFO_DEEP_SYNC
        return None


class AdaptiveInterface:
    """Main adaptive interface system"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../config/agent_versions_config.json'
            )
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.skill_detector = SkillDetector()
        self.current_users = {}
    
    def create_user_profile(
        self,
        user_id: str,
        initial_actions: List[Dict] = None,
        preferences: Dict = None
    ) -> UserProfile:
        """Create a user profile with skill detection"""
        
        # Detect role first (specialized)
        role = None
        if preferences:
            role = self.skill_detector.detect_role(preferences)
        
        # Detect general skill level
        skill_level = role if role else self.skill_detector.detect_skill_level(
            initial_actions or []
        )
        
        # Determine appropriate interface
        interface_type = self._get_interface_for_skill(skill_level)
        
        # Create profile
        profile = UserProfile(
            user_id=user_id,
            skill_level=skill_level,
            preferred_interface=interface_type,
            device_type=preferences.get('device', 'desktop') if preferences else 'desktop',
            remote_access=preferences.get('remote_access', False) if preferences else False,
            voice_enabled=preferences.get('voice_enabled', False) if preferences else False,
            accessibility_needs=preferences.get('accessibility', []) if preferences else []
        )
        
        self.current_users[user_id] = profile
        logger.info(f"Created profile for user {user_id}: {skill_level.value} -> {interface_type.value}")
        
        return profile
    
    def _get_interface_for_skill(self, skill_level: SkillLevel) -> InterfaceType:
        """Get appropriate interface type for skill level"""
        mapping = {
            SkillLevel.BEGINNER: InterfaceType.SIMPLE_GUI,
            SkillLevel.INTERMEDIATE: InterfaceType.GUI_WITH_CUSTOMIZATION,
            SkillLevel.ADVANCED: InterfaceType.ADVANCED_GUI_WITH_API,
            SkillLevel.EXPERT: InterfaceType.FULL_API_CODE_ACCESS,
            SkillLevel.NON_CODER: InterfaceType.ROLE_BASED_ADAPTIVE,
            SkillLevel.PYTHON_DEVELOPER: InterfaceType.ROLE_BASED_ADAPTIVE,
            SkillLevel.AI_DEVELOPER: InterfaceType.ROLE_BASED_ADAPTIVE,
            SkillLevel.CFO_DEEP_SYNC: InterfaceType.ROLE_BASED_ADAPTIVE,
        }
        return mapping.get(skill_level, InterfaceType.SIMPLE_GUI)
    
    def get_available_features(self, user_id: str) -> Dict:
        """Get available features for a user based on their profile"""
        profile = self.current_users.get(user_id)
        if not profile:
            return {}
        
        # Get agent version based on skill level
        version = self._get_agent_version(profile.skill_level)
        version_config = self.config['agent_versions'].get(version, {})
        
        features = {
            'agent_version': version,
            'interface_type': profile.preferred_interface.value,
            'capabilities': version_config.get('capabilities', {}),
            'tools': self._get_available_tools(profile),
            'remote_access': self._get_remote_access_config(profile),
        }
        
        # Add specialized role features for Agent 4.0 Advanced
        if profile.skill_level in [
            SkillLevel.NON_CODER,
            SkillLevel.PYTHON_DEVELOPER,
            SkillLevel.AI_DEVELOPER,
            SkillLevel.CFO_DEEP_SYNC
        ]:
            features['specialized_role'] = self._get_specialized_role_config(
                profile.skill_level
            )
        
        return features
    
    def _get_agent_version(self, skill_level: SkillLevel) -> str:
        """Map skill level to agent version"""
        mapping = {
            SkillLevel.BEGINNER: "1.0",
            SkillLevel.INTERMEDIATE: "2.0",
            SkillLevel.ADVANCED: "2.0_advanced",
            SkillLevel.EXPERT: "3.0",
            SkillLevel.NON_CODER: "4.0_advanced",
            SkillLevel.PYTHON_DEVELOPER: "4.0_advanced",
            SkillLevel.AI_DEVELOPER: "4.0_advanced",
            SkillLevel.CFO_DEEP_SYNC: "4.0_advanced",
        }
        return mapping.get(skill_level, "1.0")
    
    def _get_available_tools(self, profile: UserProfile) -> Dict:
        """Get available tools based on profile"""
        tools = self.config.get('tool_suites', {})
        
        # Filter based on skill level and role
        if profile.skill_level == SkillLevel.BEGINNER:
            return {
                'pdf_toolkit': {'capabilities': ['read', 'view']},
                'csv_handler': {'capabilities': ['view', 'basic_filter']},
            }
        
        return tools
    
    def _get_remote_access_config(self, profile: UserProfile) -> Dict:
        """Get remote access configuration"""
        if not profile.remote_access:
            return {'enabled': False}
        
        config = self.config.get('remote_access_config', {})
        
        if profile.device_type == 'phone':
            return config.get('phone_interface', {})
        elif profile.device_type == 'tablet':
            return config.get('tablet_interface', {})
        else:
            return config.get('api_access', {})
    
    def _get_specialized_role_config(self, skill_level: SkillLevel) -> Dict:
        """Get specialized role configuration for Agent 4.0 Advanced"""
        version_config = self.config['agent_versions'].get('4.0_advanced', {})
        roles = version_config.get('specialized_roles', {})
        
        role_mapping = {
            SkillLevel.NON_CODER: 'non_coder',
            SkillLevel.PYTHON_DEVELOPER: 'python_developer',
            SkillLevel.AI_DEVELOPER: 'ai_developer',
            SkillLevel.CFO_DEEP_SYNC: 'cfo_deep_sync',
        }
        
        role_key = role_mapping.get(skill_level)
        return roles.get(role_key, {})
    
    def update_user_skill(self, user_id: str, new_actions: List[Dict]):
        """Update user skill level based on new actions"""
        profile = self.current_users.get(user_id)
        if not profile:
            return
        
        # Re-detect skill level
        new_skill = self.skill_detector.detect_skill_level(new_actions)
        
        if new_skill != profile.skill_level:
            logger.info(f"User {user_id} skill upgraded: {profile.skill_level.value} -> {new_skill.value}")
            profile.skill_level = new_skill
            profile.preferred_interface = self._get_interface_for_skill(new_skill)
    
    def get_interface_launcher(self, user_id: str) -> str:
        """Get the appropriate interface launcher script for a user"""
        profile = self.current_users.get(user_id)
        if not profile:
            return "python agent-4.0/interfaces/simple_gui.py"
        
        interface_scripts = {
            InterfaceType.SIMPLE_GUI: "python agent-4.0/interfaces/simple_gui.py",
            InterfaceType.GUI_WITH_CUSTOMIZATION: "python agent-4.0/interfaces/customizable_gui.py",
            InterfaceType.ADVANCED_GUI_WITH_API: "python agent-4.0/interfaces/advanced_dashboard.py",
            InterfaceType.FULL_API_CODE_ACCESS: "python agent-4.0/interfaces/api_server.py",
            InterfaceType.ROLE_BASED_ADAPTIVE: f"python agent-4.0/interfaces/role_interface.py --role {profile.skill_level.value}",
        }
        
        return interface_scripts.get(
            profile.preferred_interface,
            "python agent-4.0/interfaces/simple_gui.py"
        )


def main():
    """Example usage"""
    interface = AdaptiveInterface()
    
    # Example 1: Non-coder user on phone
    non_coder_profile = interface.create_user_profile(
        user_id="user_001",
        preferences={
            'no_coding_required': True,
            'device': 'phone',
            'remote_access': True,
            'voice_enabled': True
        }
    )
    
    print("\n=== Non-Coder User Profile ===")
    print(f"Skill Level: {non_coder_profile.skill_level.value}")
    print(f"Interface: {non_coder_profile.preferred_interface.value}")
    print(f"Features: {json.dumps(interface.get_available_features('user_001'), indent=2)}")
    
    # Example 2: Python developer
    python_dev_profile = interface.create_user_profile(
        user_id="user_002",
        preferences={
            'python_focused': True,
            'device': 'desktop',
            'remote_access': True
        }
    )
    
    print("\n=== Python Developer Profile ===")
    print(f"Skill Level: {python_dev_profile.skill_level.value}")
    print(f"Interface: {python_dev_profile.preferred_interface.value}")
    print(f"Launch Command: {interface.get_interface_launcher('user_002')}")
    
    # Example 3: CFO Deep Sync user
    cfo_profile = interface.create_user_profile(
        user_id="user_003",
        preferences={
            'financial_focused': True,
            'device': 'tablet',
            'remote_access': True
        }
    )
    
    print("\n=== CFO Deep Sync Profile ===")
    print(f"Skill Level: {cfo_profile.skill_level.value}")
    print(f"Interface: {cfo_profile.preferred_interface.value}")


if __name__ == '__main__':
    main()
