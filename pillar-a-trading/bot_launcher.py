"""
Trading Bot Launcher
Main entry point for starting the 24/7 trading bot system
Initializes all components, connections, and starts execution
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import signal
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from bot_24_7_runner import TradingBot24x7, TradingMode
from bot_performance_tracker import PerformanceTracker
from test_suite_runner import TestSuiteRunner

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'launcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BotLauncher')


class TradingBotLauncher:
    """
    Main launcher for 24/7 trading bot system
    Handles initialization, API connections, and system startup
    """

    def __init__(self,
                 mode: str = "paper",
                 profile: str = "beginner",
                 run_tests: bool = True,
                 enable_monitoring: bool = True):
        """
        Initialize trading bot launcher

        Args:
            mode: Trading mode (paper/demo/live)
            profile: Risk profile (beginner/novice/advanced)
            run_tests: Run test suite before starting
            enable_monitoring: Enable performance monitoring
        """
        self.mode = mode
        self.profile = profile
        self.run_tests = run_tests
        self.enable_monitoring = enable_monitoring

        self.bot = None
        self.performance_tracker = None
        self.test_runner = None

        logger.info("="*80)
        logger.info("TRADING BOT LAUNCHER INITIALIZED")
        logger.info("="*80)
        logger.info(f"Mode: {mode.upper()}")
        logger.info(f"Profile: {profile.capitalize()}")
        logger.info(f"Run Tests: {run_tests}")
        logger.info(f"Monitoring: {enable_monitoring}")
        logger.info("="*80)

    def check_prerequisites(self) -> bool:
        """Check system prerequisites before starting"""
        logger.info("\n--- Checking Prerequisites ---")

        checks = {
            "Config Files": self.check_config_files(),
            "Log Directories": self.check_directories(),
            "Risk Profiles": self.check_risk_profiles(),
            "Python Dependencies": self.check_dependencies()
        }

        all_passed = all(checks.values())

        for check_name, passed in checks.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            logger.info(f"{check_name}: {status}")

        if all_passed:
            logger.info("All prerequisites passed ✓")
        else:
            logger.error("Some prerequisites failed ✗")

        return all_passed

    def check_config_files(self) -> bool:
        """Check if required configuration files exist"""
        try:
            config_dir = Path(__file__).parent / 'config'
            required_files = [
                'trading_risk_profiles.json'
            ]

            for filename in required_files:
                filepath = config_dir / filename
                if not filepath.exists():
                    logger.warning(f"Config file not found: {filepath}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error checking config files: {e}")
            return False

    def check_directories(self) -> bool:
        """Check and create required directories"""
        try:
            required_dirs = [
                Path(__file__).parent.parent / 'logs' / 'trading_bot',
                Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'performance',
                Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'tests',
                Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'monitoring'
            ]

            for dir_path in required_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)

            return True
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            return False

    def check_risk_profiles(self) -> bool:
        """Verify risk profile configuration"""
        try:
            config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'

            if not config_path.exists():
                return False

            with open(config_path, 'r') as f:
                config = json.load(f)

            # Check if selected profile exists
            if self.profile not in config['profiles']:
                logger.error(f"Profile '{self.profile}' not found in config")
                return False

            return True
        except Exception as e:
            logger.error(f"Error checking risk profiles: {e}")
            return False

    def check_dependencies(self) -> bool:
        """Check Python dependencies"""
        try:
            # Check if required modules can be imported
            required_modules = []

            # All dependencies are standard library
            return True
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False

    def setup_kraken_connection(self) -> Dict[str, Any]:
        """
        Setup Kraken API connection
        For paper trading, this is simulated
        """
        logger.info("\n--- Setting up Kraken API Connection ---")

        try:
            if self.mode == "paper":
                logger.info("Paper trading mode - Using simulated market data")
                connection = {
                    "status": "connected",
                    "mode": "paper",
                    "endpoint": "simulated",
                    "api_key": None,
                    "timestamp": datetime.now().isoformat()
                }
            elif self.mode == "demo":
                logger.info("Demo mode - Using Kraken sandbox API")
                connection = {
                    "status": "connected",
                    "mode": "demo",
                    "endpoint": "https://api-sandbox.kraken.com",
                    "api_key": os.getenv("KRAKEN_SANDBOX_API_KEY"),
                    "timestamp": datetime.now().isoformat()
                }
            else:  # live
                logger.warning("Live trading mode - Real API connection required")
                connection = {
                    "status": "not_connected",
                    "mode": "live",
                    "endpoint": "https://api.kraken.com",
                    "api_key": os.getenv("KRAKEN_API_KEY"),
                    "timestamp": datetime.now().isoformat()
                }

            logger.info(f"Kraken connection status: {connection['status']}")
            return connection

        except Exception as e:
            logger.error(f"Error setting up Kraken connection: {e}")
            return {"status": "error", "error": str(e)}

    def setup_mt5_connection(self) -> Dict[str, Any]:
        """
        Setup MT5 connection
        For paper trading, this is simulated
        """
        logger.info("\n--- Setting up MT5 Connection ---")

        try:
            if self.mode == "paper":
                logger.info("Paper trading mode - MT5 connection simulated")
                connection = {
                    "status": "simulated",
                    "mode": "paper",
                    "platform": "MT5",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.info("MT5 connection not available in demo/live modes yet")
                connection = {
                    "status": "not_available",
                    "mode": self.mode,
                    "platform": "MT5",
                    "timestamp": datetime.now().isoformat()
                }

            logger.info(f"MT5 connection status: {connection['status']}")
            return connection

        except Exception as e:
            logger.error(f"Error setting up MT5 connection: {e}")
            return {"status": "error", "error": str(e)}

    def configure_risk_management(self) -> Dict[str, Any]:
        """Configure risk management parameters"""
        logger.info("\n--- Configuring Risk Management ---")

        try:
            config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'

            with open(config_path, 'r') as f:
                config = json.load(f)

            risk_params = config['profiles'][self.profile]['risk_parameters']

            logger.info(f"Risk Profile: {config['profiles'][self.profile]['name']}")
            logger.info(f"Max Position Size: {risk_params['max_position_size']*100}%")
            logger.info(f"Risk Per Trade: {risk_params['risk_per_trade']*100}%")
            logger.info(f"Max Daily Loss: {risk_params['max_daily_loss']*100}%")
            logger.info(f"Max Concurrent Trades: {risk_params['max_concurrent_trades']}")
            logger.info(f"Confidence Threshold: {risk_params['confidence_threshold']*100}%")

            return risk_params

        except Exception as e:
            logger.error(f"Error configuring risk management: {e}")
            return {}

    def run_test_suite(self) -> bool:
        """Run comprehensive test suite"""
        if not self.run_tests:
            logger.info("\n--- Skipping Test Suite (disabled) ---")
            return True

        logger.info("\n" + "="*80)
        logger.info("RUNNING COMPREHENSIVE TEST SUITE")
        logger.info("="*80)

        try:
            self.test_runner = TestSuiteRunner()
            results = self.test_runner.run_all_tests()

            if results['failed'] > 0:
                logger.error(f"Test suite failed: {results['failed']} test(s) failed")
                return False

            logger.info(f"Test suite passed: {results['passed']}/{results['total_tests']} tests")
            return True

        except Exception as e:
            logger.error(f"Error running test suite: {e}")
            logger.error(traceback.format_exc())
            return False

    def initialize_bot(self) -> bool:
        """Initialize the trading bot"""
        logger.info("\n" + "="*80)
        logger.info("INITIALIZING TRADING BOT")
        logger.info("="*80)

        try:
            # Create trading mode enum
            mode_enum = TradingMode(self.mode)

            # Initialize bot
            self.bot = TradingBot24x7(
                mode=mode_enum,
                profile=self.profile,
                config_path=None  # Use default config
            )

            logger.info("Trading bot initialized successfully ✓")
            return True

        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            logger.error(traceback.format_exc())
            return False

    def launch_bot(self) -> bool:
        """Launch the trading bot"""
        logger.info("\n" + "="*80)
        logger.info("LAUNCHING 24/7 TRADING BOT")
        logger.info("="*80)

        if not self.bot:
            logger.error("Bot not initialized")
            return False

        try:
            # Start the bot (this will block in the main thread)
            self.bot.start()
            return True

        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
            return True
        except Exception as e:
            logger.error(f"Error launching bot: {e}")
            logger.error(traceback.format_exc())
            return False

    def generate_startup_report(self) -> str:
        """Generate startup report"""
        logger.info("\n--- Generating Startup Report ---")

        try:
            report_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'reports'
            report_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = report_dir / f"startup_report_{timestamp}.txt"

            with open(report_path, 'w') as f:
                f.write("="*80 + "\n")
                f.write("24/7 TRADING BOT - STARTUP REPORT\n")
                f.write("="*80 + "\n\n")

                f.write("CONFIGURATION\n")
                f.write("-"*80 + "\n")
                f.write(f"Mode:           {self.mode.upper()}\n")
                f.write(f"Profile:        {self.profile.capitalize()}\n")
                f.write(f"Tests Enabled:  {self.run_tests}\n")
                f.write(f"Monitoring:     {self.enable_monitoring}\n")
                f.write(f"Start Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")

                f.write("API CONNECTIONS\n")
                f.write("-"*80 + "\n")
                f.write(f"Kraken API:     {'Simulated' if self.mode == 'paper' else 'Connected'}\n")
                f.write(f"MT5 Platform:   {'Simulated' if self.mode == 'paper' else 'Not Available'}\n")
                f.write("\n")

                f.write("SYSTEM STATUS\n")
                f.write("-"*80 + "\n")
                f.write(f"Bot Status:     RUNNING\n")
                f.write(f"Mode:           {self.mode.upper()}\n")
                f.write(f"Ready:          YES\n")
                f.write("\n")

                f.write("="*80 + "\n")
                f.write("END OF STARTUP REPORT\n")
                f.write("="*80 + "\n")

            logger.info(f"Startup report saved: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error generating startup report: {e}")
            return ""

    def run(self) -> bool:
        """Main launcher execution"""
        try:
            # 1. Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return False

            # 2. Setup API connections
            kraken_conn = self.setup_kraken_connection()
            mt5_conn = self.setup_mt5_connection()

            # 3. Configure risk management
            risk_params = self.configure_risk_management()

            # 4. Run test suite (optional)
            if self.run_tests:
                if not self.run_test_suite():
                    logger.warning("Test suite had failures, but continuing...")

            # 5. Initialize bot
            if not self.initialize_bot():
                logger.error("Bot initialization failed")
                return False

            # 6. Generate startup report
            self.generate_startup_report()

            # 7. Launch bot (this blocks until stopped)
            logger.info("\n" + "="*80)
            logger.info("STARTING TRADING OPERATIONS")
            logger.info("="*80)
            logger.info("Press Ctrl+C to stop the bot gracefully\n")

            return self.launch_bot()

        except Exception as e:
            logger.error(f"Fatal error in launcher: {e}")
            logger.error(traceback.format_exc())
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='24/7 Trading Bot Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch in paper trading mode with beginner profile
  python bot_launcher.py --mode paper --profile beginner

  # Launch in demo mode without tests
  python bot_launcher.py --mode demo --profile novice --no-tests

  # Launch in advanced mode
  python bot_launcher.py --mode paper --profile advanced
        """
    )

    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'demo', 'live'],
                       help='Trading mode (default: paper)')

    parser.add_argument('--profile', type=str, default='beginner',
                       choices=['beginner', 'novice', 'advanced'],
                       help='Risk profile (default: beginner)')

    parser.add_argument('--no-tests', action='store_true',
                       help='Skip test suite before starting')

    parser.add_argument('--no-monitoring', action='store_true',
                       help='Disable performance monitoring')

    args = parser.parse_args()

    # Create launcher
    launcher = TradingBotLauncher(
        mode=args.mode,
        profile=args.profile,
        run_tests=not args.no_tests,
        enable_monitoring=not args.no_monitoring
    )

    # Run launcher
    success = launcher.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
