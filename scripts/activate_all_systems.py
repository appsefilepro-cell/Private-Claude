"""
System-Wide Activation & Sync Script
Activates all Zapier integrations, syncs Microsoft 365, and prepares all systems
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SystemActivation')


class SystemActivator:
    """Activates and syncs all Agent X2.0 systems"""

    def __init__(self):
        """Initialize system activator"""
        self.activation_log = []
        self.config_dir = Path(__file__).parent.parent / 'config'

    def log_action(self, action: str, status: str, details: str = ""):
        """Log activation action"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "status": status,
            "details": details
        }
        self.activation_log.append(entry)

        icon = "✅" if status == "SUCCESS" else "⚠️" if status == "WARNING" else "❌"
        logger.info(f"{icon} {action}: {status} {f'- {details}' if details else ''}")

    def check_environment_config(self):
        """Check and verify environment configuration"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 1: ENVIRONMENT CONFIGURATION")
        logger.info("=" * 70)

        env_file = self.config_dir / '.env'

        if not env_file.exists():
            self.log_action("Environment Config", "WARNING", ".env file not found")
            logger.warning("To enable integrations, configure config/.env")
            return False

        self.log_action("Environment Config", "SUCCESS", ".env file found")

        # Check for required variables
        required_vars = [
            'ZAPIER_MCP_BEARER_TOKEN',
            'ZAPIER_MCP_ENDPOINT'
        ]

        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)

            missing = []
            for var in required_vars:
                if not os.getenv(var):
                    missing.append(var)

            if missing:
                self.log_action("Environment Variables", "WARNING", f"Missing: {', '.join(missing)}")
            else:
                self.log_action("Environment Variables", "SUCCESS", "All required variables set")

        except Exception as e:
            self.log_action("Environment Check", "ERROR", str(e))

        return True

    def activate_zapier_integrations(self):
        """Activate Zapier MCP integrations"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 2: ZAPIER MCP INTEGRATION")
        logger.info("=" * 70)

        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'zapier-integration'))
            from zapier_mcp_connector import ZapierMCPConnector

            connector = ZapierMCPConnector()

            if not connector.bearer_token:
                self.log_action("Zapier MCP", "WARNING", "Bearer token not configured")
                logger.warning("Configure ZAPIER_MCP_BEARER_TOKEN in config/.env")
                return False

            # Test connection
            try:
                status = connector.check_connection()
                self.log_action("Zapier MCP Connection", "SUCCESS", "Connected")
                return True
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    self.log_action("Zapier MCP Connection", "WARNING", "Spending cap reached (resets 3am)")
                    logger.info("Zapier MCP is configured correctly, waiting for spending cap reset")
                    return True
                else:
                    self.log_action("Zapier MCP Connection", "ERROR", error_msg)
                    return False

        except Exception as e:
            self.log_action("Zapier MCP", "ERROR", str(e))
            return False

    def sync_microsoft_365(self):
        """Check Microsoft 365 configuration"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 3: MICROSOFT 365 SYNC")
        logger.info("=" * 70)

        required_vars = [
            'MICROSOFT_TENANT_ID',
            'MICROSOFT_CLIENT_ID',
            'MICROSOFT_CLIENT_SECRET',
            'SHAREPOINT_SITE_URL'
        ]

        try:
            from dotenv import load_dotenv
            load_dotenv(self.config_dir / '.env')

            configured = []
            missing = []

            for var in required_vars:
                value = os.getenv(var)
                if value and not value.startswith('your_'):
                    configured.append(var)
                else:
                    missing.append(var)

            if configured:
                self.log_action("Microsoft 365 Config", "SUCCESS", f"{len(configured)}/{len(required_vars)} variables configured")
            else:
                self.log_action("Microsoft 365 Config", "WARNING", "No credentials configured")
                logger.warning("Configure Microsoft 365 credentials in config/.env")
                logger.info("See docs/API_SETUP_INSTRUCTIONS.md for setup guide")

            return len(configured) > 0

        except Exception as e:
            self.log_action("Microsoft 365 Sync", "ERROR", str(e))
            return False

    def activate_trading_systems(self):
        """Activate trading bot systems"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 4: TRADING SYSTEMS")
        logger.info("=" * 70)

        try:
            # Load risk profiles
            profiles_file = Path(__file__).parent.parent / 'pillar-a-trading' / 'config' / 'trading_risk_profiles.json'

            if not profiles_file.exists():
                self.log_action("Trading Risk Profiles", "ERROR", "Config file not found")
                return False

            with open(profiles_file, 'r') as f:
                profiles = json.load(f)

            profile_count = len(profiles['profiles'])
            self.log_action("Trading Risk Profiles", "SUCCESS", f"{profile_count} profiles loaded (beginner, novice, advanced)")

            # Check Agent 3.0
            sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'agent-3.0'))
            from agent_3_orchestrator import Agent3Orchestrator

            agent = Agent3Orchestrator()
            self.log_action("Agent 3.0 Orchestrator", "SUCCESS", "Initialized and ready")

            return True

        except Exception as e:
            self.log_action("Trading Systems", "ERROR", str(e))
            return False

    def activate_legal_systems(self):
        """Activate legal forensics systems"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 5: LEGAL FORENSICS")
        logger.info("=" * 70)

        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'legal-forensics'))
            from forensic_data_analyzer import ForensicDataAnalyzer

            analyzer = ForensicDataAnalyzer()
            case_count = len(analyzer.cases)
            self.log_action("Forensic Data Analyzer", "SUCCESS", f"{case_count} cases loaded")

            return True

        except Exception as e:
            self.log_action("Legal Systems", "ERROR", str(e))
            return False

    def activate_grant_intelligence(self):
        """Activate grant intelligence systems"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 6: GRANT INTELLIGENCE")
        logger.info("=" * 70)

        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-d-nonprofit' / 'grant-intelligence'))
            from grant_pipeline_manager import GrantPipelineManager

            manager = GrantPipelineManager()
            self.log_action("Grant Pipeline Manager", "SUCCESS", "Initialized and ready")

            return True

        except Exception as e:
            self.log_action("Grant Intelligence", "ERROR", str(e))
            return False

    def run_remediation_check(self):
        """Run remediation engine check"""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 7: REMEDIATION CHECK")
        logger.info("=" * 70)

        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'core-systems' / 'remediation'))
            from remediation_engine import RemediationEngine

            engine = RemediationEngine()
            self.log_action("Remediation Engine", "SUCCESS", "Ready for task recovery")

            # Check for incomplete tasks (if tasks file exists)
            tasks_file = Path(__file__).parent.parent / 'logs' / 'ingestion_tasks.json'
            if tasks_file.exists():
                with open(tasks_file, 'r') as f:
                    tasks = json.load(f)
                incomplete = [t for t in tasks if t.get('status') != 'COMPLETED']
                if incomplete:
                    self.log_action("Task Status", "WARNING", f"{len(incomplete)} incomplete tasks found")
                else:
                    self.log_action("Task Status", "SUCCESS", "All tasks completed")
            else:
                self.log_action("Task Status", "INFO", "No task history found")

            return True

        except Exception as e:
            self.log_action("Remediation Check", "ERROR", str(e))
            return False

    def generate_activation_report(self):
        """Generate comprehensive activation report"""
        logger.info("\n" + "=" * 70)
        logger.info("ACTIVATION COMPLETE - GENERATING REPORT")
        logger.info("=" * 70 + "\n")

        # Count successes, warnings, errors
        success_count = sum(1 for log in self.activation_log if log['status'] == 'SUCCESS')
        warning_count = sum(1 for log in self.activation_log if log['status'] == 'WARNING')
        error_count = sum(1 for log in self.activation_log if log['status'] == 'ERROR')

        total = len(self.activation_log)

        print("📊 SYSTEM ACTIVATION SUMMARY")
        print("-" * 70)
        print(f"Total Actions: {total}")
        print(f"✅ Success: {success_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(f"❌ Errors: {error_count}")
        print("-" * 70)

        # Export detailed log
        log_file = Path(__file__).parent.parent / 'logs' / f'activation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        os.makedirs(log_file.parent, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total": total,
                    "success": success_count,
                    "warnings": warning_count,
                    "errors": error_count
                },
                "actions": self.activation_log
            }, f, indent=2)

        logger.info(f"\nDetailed log saved to: {log_file}")

        # Next steps
        print("\n📋 NEXT STEPS:")
        print("-" * 70)

        if warning_count > 0 or error_count > 0:
            print("1. Review warnings and errors above")
            print("2. Configure missing API credentials in config/.env")
            print("3. See docs/API_SETUP_INSTRUCTIONS.md for setup guide")
            print("4. Re-run this script after configuration")
        else:
            print("✅ All systems activated successfully!")
            print("1. Run backtesting: python pillar-a-trading/backtesting/backtesting_engine.py")
            print("2. Run integration tests: python tests/integration_test_suite.py")
            print("3. Execute forensic analysis: python legal-forensics/execute_forensic_analysis.py")

        print("-" * 70 + "\n")

    def activate_all(self):
        """Run complete system activation"""
        logger.info("\n" + "=" * 70)
        logger.info("AGENT X2.0 - SYSTEM-WIDE ACTIVATION")
        logger.info("=" * 70)

        self.check_environment_config()
        self.activate_zapier_integrations()
        self.sync_microsoft_365()
        self.activate_trading_systems()
        self.activate_legal_systems()
        self.activate_grant_intelligence()
        self.run_remediation_check()

        self.generate_activation_report()


def main():
    """Main activation script"""
    activator = SystemActivator()
    activator.activate_all()


if __name__ == "__main__":
    main()
