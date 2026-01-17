#!/usr/bin/env python3
"""
Agent 4.0 Advanced Setup and Launch Script
Handles initialization, configuration, and launching of Agent 4.0 Advanced system
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AgentSetup:
    """Setup and configuration manager"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / 'config'
        self.interfaces_dir = self.base_dir / 'interfaces'
        self.tools_dir = self.base_dir / 'tools'
    
    def check_dependencies(self) -> bool:
        """Check if all dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'flask', 'fastapi', 'streamlit', 'gradio', 'dash',
            'anthropic', 'openai', 'redis', 'prometheus_client'
        ]
        
        optional_packages = [
            'PyPDF2', 'pdfplumber', 'reportlab'
        ]
        
        missing_required = []
        missing_optional = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_required.append(package)
        
        for package in optional_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_optional.append(package)
        
        if missing_required:
            logger.error(f"Missing required packages: {', '.join(missing_required)}")
            logger.error("Install with: pip install " + ' '.join(missing_required))
            return False
        
        if missing_optional:
            logger.warning(f"Missing optional packages: {', '.join(missing_optional)}")
            logger.warning("Some features may be limited. Install with: pip install " + ' '.join(missing_optional))
        
        logger.info("✓ All required dependencies installed")
        return True
    
    def initialize_sandbox(self) -> bool:
        """Initialize sandbox environment"""
        logger.info("Initializing sandbox environment...")
        
        # Create necessary directories
        directories = [
            self.base_dir / 'logs',
            self.base_dir / 'data',
            self.base_dir / 'temp',
            self.base_dir / 'state'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("✓ Sandbox environment initialized")
        return True
    
    def load_config(self) -> dict:
        """Load agent configuration"""
        config_file = self.config_dir / 'agent_versions_config.json'
        
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            return {}
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        logger.info("✓ Configuration loaded")
        return config
    
    def setup_environment(self):
        """Set up environment variables"""
        logger.info("Setting up environment...")
        
        # Set Python path
        os.environ['PYTHONPATH'] = str(self.base_dir)
        
        # Set agent home
        os.environ['AGENT_HOME'] = str(self.base_dir)
        
        logger.info("✓ Environment configured")
    
    def launch_interface(self, role: str, device: str = 'desktop'):
        """Launch appropriate interface for role"""
        logger.info(f"Launching interface for role: {role}")
        
        interface_script = self.interfaces_dir / 'role_interface.py'
        
        if not interface_script.exists():
            logger.error(f"Interface script not found: {interface_script}")
            return False
        
        # Launch interface
        cmd = [sys.executable, str(interface_script), '--role', role]
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to launch interface: {e}")
            return False
    
    def start_coordination_system(self):
        """Start agent coordination system"""
        logger.info("Starting agent coordination system...")
        
        coordinator_script = self.base_dir / 'orchestrator' / 'agent_coordinator.py'
        
        if coordinator_script.exists():
            logger.info("✓ Coordination system ready")
            return True
        else:
            logger.error("Coordination system not found")
            return False


def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        AGENT 4.0 ADVANCED - MULTI-VERSION SYSTEM            ║
║                                                              ║
║  Versions: 1.0, 2.0, 2.0 Advanced, 3.0, 4.0, 4.0 Advanced   ║
║  Agents: 219 (Master CFO + 8 Divisions + Committee 100)     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Agent 4.0 Advanced Setup and Launch'
    )
    
    parser.add_argument(
        '--role',
        type=str,
        choices=['non_coder', 'python_developer', 'ai_developer', 'cfo_deep_sync', 'auto'],
        default='auto',
        help='User role (auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['desktop', 'phone', 'tablet'],
        default='desktop',
        help='Device type'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check dependencies and configuration'
    )
    
    parser.add_argument(
        '--setup-only',
        action='store_true',
        help='Only perform setup, do not launch'
    )
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = AgentSetup()
    
    # Check dependencies
    if not setup.check_dependencies():
        sys.exit(1)
    
    if args.check_only:
        logger.info("✓ Dependency check passed")
        sys.exit(0)
    
    # Initialize sandbox
    if not setup.initialize_sandbox():
        logger.error("Failed to initialize sandbox")
        sys.exit(1)
    
    # Load configuration
    config = setup.load_config()
    if not config:
        logger.error("Failed to load configuration")
        sys.exit(1)
    
    # Setup environment
    setup.setup_environment()
    
    # Start coordination system
    if not setup.start_coordination_system():
        logger.error("Failed to start coordination system")
        sys.exit(1)
    
    if args.setup_only:
        logger.info("✓ Setup complete")
        sys.exit(0)
    
    # Launch interface
    print("\n" + "=" * 60)
    print("LAUNCHING AGENT INTERFACE")
    print("=" * 60 + "\n")
    
    if args.role == 'auto':
        logger.info("Auto-detecting user role...")
        # For now, default to non_coder for maximum accessibility
        role = 'non_coder'
        logger.info(f"Selected role: {role}")
    else:
        role = args.role
    
    logger.info(f"Device: {args.device}")
    logger.info(f"Role: {role}")
    
    # Show available features
    print("\n✨ AVAILABLE FEATURES:")
    print("  • PDF Processing (read, parse, generate, merge)")
    print("  • CSV Analysis (parse, transform, analyze, export)")
    print("  • Pricing Tools (calculate, optimize, forecast)")
    print("  • Remote Access (phone, tablet, web)")
    print("  • Voice Commands (natural language control)")
    print("  • Automated Workflows (no coding required)")
    
    print("\n🔗 QUICK LINKS:")
    print("  • Web Interface: http://localhost:8080")
    print("  • API Documentation: http://localhost:8080/docs")
    print("  • Dashboard: http://localhost:8080/dashboard")
    
    print("\n" + "=" * 60 + "\n")
    
    # Launch interface
    success = setup.launch_interface(role, args.device)
    
    if success:
        logger.info("✓ Agent system launched successfully")
    else:
        logger.error("Failed to launch agent system")
        sys.exit(1)


if __name__ == '__main__':
    main()
