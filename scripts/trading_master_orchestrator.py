#!/usr/bin/env python3
"""
Trading Master Orchestrator
Coordinates all 4 trading accounts (3 MT5 + 1 OKX) and ML analyzer
Runs the complete 24-hour trading marathon
"""

import sys
import os
import time
import json
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List
import signal

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_marathon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingMasterOrchestrator:
    """Master orchestrator for all trading operations"""

    def __init__(self):
        self.processes = {}
        self.threads = {}
        self.active = False
        self.start_time = None
        self.marathon_duration_hours = 24
        self.stats = {
            'mt5_trades': 0,
            'okx_trades': 0,
            'total_profit': 0,
            'mt5_profit': 0,
            'okx_profit': 0,
            'start_time': None,
            'errors': []
        }

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("\nReceived shutdown signal. Stopping all trading...")
        self.stop_all()
        sys.exit(0)

    def print_banner(self):
        """Print startup banner"""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        24-HOUR TRADING MARATHON - MASTER ORCHESTRATOR         ║
║                                                                ║
║  Trading Accounts:                                            ║
║    • MT5 Demo Account 1 (5044023923)                         ║
║    • MT5 Demo Account 2 (100459584)                          ║
║    • MT5 Demo Account 3 (5044025969)                         ║
║    • OKX Bitcoin Futures (DEMO MODE)                          ║
║                                                                ║
║  Target: 350+ trades in 24 hours                             ║
║  Strategy: ML Pattern Detection + Adaptive Learning          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
        print(banner)
        logger.info("Trading Marathon Orchestrator Starting...")

    def verify_dependencies(self) -> bool:
        """Verify all required scripts and dependencies exist"""
        logger.info("Verifying dependencies...")

        required_files = [
            '/home/user/Private-Claude/scripts/mt5_multi_account_trader.py',
            '/home/user/Private-Claude/scripts/okx_bitcoin_futures_trader.py',
            '/home/user/Private-Claude/scripts/ml_trade_analyzer.py',
            '/home/user/Private-Claude/scripts/zapier_trading_notifier.py',
            '/home/user/Private-Claude/MT5_AND_OKX_TRADING_CONFIG.json'
        ]

        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                logger.error(f"Missing required file: {file_path}")

        if missing_files:
            logger.error(f"Cannot start - {len(missing_files)} required files missing")
            return False

        # Verify Python packages
        required_packages = [
            'MetaTrader5',
            'ccxt',
            'pandas',
            'numpy',
            'sklearn',
            'requests'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"Missing Python package: {package}")

        if missing_packages:
            logger.warning(f"Missing packages: {', '.join(missing_packages)}")
            logger.warning("Install with: pip install -r requirements.txt")
            # Don't fail - let individual scripts handle missing packages

        logger.info("✓ Dependency verification complete")
        return True

    def start_mt5_trading(self):
        """Start MT5 multi-account trading"""
        logger.info("Starting MT5 multi-account trading...")

        try:
            process = subprocess.Popen(
                [sys.executable, '/home/user/Private-Claude/scripts/mt5_multi_account_trader.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['mt5'] = process
            logger.info("✓ MT5 trading process started")

            # Monitor output in background
            def monitor_mt5():
                for line in process.stdout:
                    logger.info(f"[MT5] {line.strip()}")

            thread = threading.Thread(target=monitor_mt5, daemon=True)
            thread.start()
            self.threads['mt5_monitor'] = thread

            return True

        except Exception as e:
            logger.error(f"Failed to start MT5 trading: {e}")
            self.stats['errors'].append(f"MT5 startup error: {e}")
            return False

    def start_okx_trading(self, demo_mode: bool = True):
        """Start OKX Bitcoin futures trading"""
        logger.info("Starting OKX Bitcoin futures trading...")

        try:
            mode = 'demo' if demo_mode else 'live'

            process = subprocess.Popen(
                [
                    sys.executable,
                    '/home/user/Private-Claude/scripts/okx_bitcoin_futures_trader.py',
                    '--mode', mode
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['okx'] = process
            logger.info(f"✓ OKX trading process started (mode: {mode})")

            # Monitor output in background
            def monitor_okx():
                for line in process.stdout:
                    logger.info(f"[OKX] {line.strip()}")

            thread = threading.Thread(target=monitor_okx, daemon=True)
            thread.start()
            self.threads['okx_monitor'] = thread

            return True

        except Exception as e:
            logger.error(f"Failed to start OKX trading: {e}")
            self.stats['errors'].append(f"OKX startup error: {e}")
            return False

    def start_ml_analyzer(self):
        """Start ML trade analyzer in continuous learning mode"""
        logger.info("Starting ML trade analyzer...")

        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    '/home/user/Private-Claude/scripts/ml_trade_analyzer.py',
                    '--continuous',
                    '--interval', '60'
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes['ml'] = process
            logger.info("✓ ML analyzer started (continuous learning mode)")

            # Monitor output in background
            def monitor_ml():
                for line in process.stdout:
                    logger.info(f"[ML] {line.strip()}")

            thread = threading.Thread(target=monitor_ml, daemon=True)
            thread.start()
            self.threads['ml_monitor'] = thread

            return True

        except Exception as e:
            logger.error(f"Failed to start ML analyzer: {e}")
            self.stats['errors'].append(f"ML analyzer startup error: {e}")
            return False

    def monitor_marathon(self):
        """Monitor the 24-hour trading marathon"""
        logger.info("Starting marathon monitoring thread...")

        report_interval = 3600  # Report every hour
        last_report = time.time()

        while self.active:
            try:
                current_time = time.time()
                elapsed_hours = (current_time - time.mktime(self.start_time.timetuple())) / 3600

                # Check if marathon is complete
                if elapsed_hours >= self.marathon_duration_hours:
                    logger.info(f"24-hour marathon complete! Stopping all trading...")
                    self.stop_all()
                    break

                # Hourly report
                if current_time - last_report >= report_interval:
                    self.generate_hourly_report(elapsed_hours)
                    last_report = current_time

                # Check process health
                self.check_process_health()

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in marathon monitoring: {e}")
                time.sleep(60)

    def check_process_health(self):
        """Check if all trading processes are still running"""
        for name, process in self.processes.items():
            if process.poll() is not None:
                logger.error(f"{name.upper()} process terminated unexpectedly!")
                self.stats['errors'].append(f"{name} process terminated")

                # Try to restart
                logger.info(f"Attempting to restart {name}...")
                if name == 'mt5':
                    self.start_mt5_trading()
                elif name == 'okx':
                    self.start_okx_trading(demo_mode=True)
                elif name == 'ml':
                    self.start_ml_analyzer()

    def generate_hourly_report(self, elapsed_hours: float):
        """Generate and send hourly progress report"""
        logger.info("=" * 70)
        logger.info(f"HOURLY TRADING MARATHON REPORT - Hour {int(elapsed_hours)} of 24")
        logger.info("=" * 70)
        logger.info(f"Marathon Duration: {elapsed_hours:.1f} hours")
        logger.info(f"Time Remaining: {24 - elapsed_hours:.1f} hours")
        logger.info("")

        # Load latest trade data
        trade_stats = self.load_trade_statistics()

        logger.info("Trading Activity:")
        logger.info(f"  MT5 Trades: {trade_stats.get('mt5_trades', 0)}")
        logger.info(f"  OKX Trades: {trade_stats.get('okx_trades', 0)}")
        logger.info(f"  Total Trades: {trade_stats.get('total_trades', 0)}")
        logger.info("")

        logger.info("Performance:")
        logger.info(f"  MT5 Profit: ${trade_stats.get('mt5_profit', 0):.2f}")
        logger.info(f"  OKX Profit: ${trade_stats.get('okx_profit', 0):.2f}")
        logger.info(f"  Total Profit: ${trade_stats.get('total_profit', 0):.2f}")
        logger.info("")

        logger.info("Process Status:")
        for name, process in self.processes.items():
            status = "✓ Running" if process.poll() is None else "✗ Stopped"
            logger.info(f"  {name.upper()}: {status}")

        logger.info("")
        logger.info(f"Target Progress: {trade_stats.get('total_trades', 0)}/350 trades")
        logger.info("=" * 70)

        # Send to Zapier
        try:
            from zapier_trading_notifier import ZapierTradingNotifier
            notifier = ZapierTradingNotifier()
            notifier.notify_hourly_summary(trade_stats)
        except Exception as e:
            logger.error(f"Failed to send hourly report to Zapier: {e}")

    def load_trade_statistics(self) -> Dict:
        """Load current trading statistics from log files"""
        stats = {
            'mt5_trades': 0,
            'okx_trades': 0,
            'total_trades': 0,
            'mt5_profit': 0,
            'okx_profit': 0,
            'total_profit': 0
        }

        # Load from ML learning files
        try:
            if os.path.exists('/home/user/Private-Claude/mt5_ml_learning.json'):
                with open('/home/user/Private-Claude/mt5_ml_learning.json', 'r') as f:
                    mt5_data = json.load(f)
                    performance = mt5_data.get('performance_metrics', {})
                    stats['mt5_trades'] = performance.get('total_trades', 0)
                    stats['mt5_profit'] = performance.get('total_profit', 0)
        except:
            pass

        try:
            if os.path.exists('/home/user/Private-Claude/okx_ml_learning.json'):
                with open('/home/user/Private-Claude/okx_ml_learning.json', 'r') as f:
                    okx_data = json.load(f)
                    performance = okx_data.get('performance_metrics', {})
                    stats['okx_trades'] = performance.get('total_trades', 0)
                    stats['okx_profit'] = performance.get('total_profit', 0)
        except:
            pass

        stats['total_trades'] = stats['mt5_trades'] + stats['okx_trades']
        stats['total_profit'] = stats['mt5_profit'] + stats['okx_profit']

        return stats

    def generate_final_report(self):
        """Generate final marathon report"""
        logger.info("\n" + "=" * 70)
        logger.info("24-HOUR TRADING MARATHON - FINAL REPORT")
        logger.info("=" * 70)

        trade_stats = self.load_trade_statistics()

        logger.info(f"\nMarathon Period:")
        logger.info(f"  Start: {self.start_time}")
        logger.info(f"  End: {datetime.now()}")
        logger.info(f"  Duration: 24 hours")

        logger.info(f"\nTrading Activity:")
        logger.info(f"  MT5 Total Trades: {trade_stats['mt5_trades']}")
        logger.info(f"  OKX Total Trades: {trade_stats['okx_trades']}")
        logger.info(f"  TOTAL TRADES: {trade_stats['total_trades']} (Target: 350)")

        logger.info(f"\nFinancial Performance:")
        logger.info(f"  MT5 Total Profit: ${trade_stats['mt5_profit']:.2f}")
        logger.info(f"  OKX Total Profit: ${trade_stats['okx_profit']:.2f}")
        logger.info(f"  TOTAL PROFIT: ${trade_stats['total_profit']:.2f}")

        logger.info(f"\nErrors During Marathon: {len(self.stats['errors'])}")
        if self.stats['errors']:
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                logger.info(f"  - {error}")

        logger.info("\n" + "=" * 70)
        logger.info("MARATHON COMPLETE!")
        logger.info("=" * 70)

        # Send final report to Zapier
        try:
            from zapier_trading_notifier import ZapierTradingNotifier
            notifier = ZapierTradingNotifier()
            notifier.notify_daily_report(trade_stats)
        except Exception as e:
            logger.error(f"Failed to send final report to Zapier: {e}")

        # Save final report to file
        report_file = f'/home/user/Private-Claude/marathon_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump({
                'stats': trade_stats,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'errors': self.stats['errors']
            }, f, indent=2)

        logger.info(f"\nFinal report saved to: {report_file}")

    def start_marathon(self, demo_mode: bool = True):
        """Start the 24-hour trading marathon"""
        self.print_banner()

        # Verify dependencies
        if not self.verify_dependencies():
            logger.error("Cannot start marathon - dependency check failed")
            return False

        self.start_time = datetime.now()
        self.active = True

        logger.info(f"\nMarathon Start Time: {self.start_time}")
        logger.info(f"Expected End Time: {self.start_time + timedelta(hours=24)}")
        logger.info("\n" + "=" * 70)

        # Start all trading systems
        logger.info("\nStarting all trading systems...")

        mt5_started = self.start_mt5_trading()
        time.sleep(3)

        okx_started = self.start_okx_trading(demo_mode=demo_mode)
        time.sleep(3)

        ml_started = self.start_ml_analyzer()
        time.sleep(3)

        if not (mt5_started or okx_started):
            logger.error("Failed to start any trading systems - aborting marathon")
            self.stop_all()
            return False

        logger.info("\n" + "=" * 70)
        logger.info("ALL SYSTEMS STARTED - MARATHON IN PROGRESS")
        logger.info("=" * 70)
        logger.info("\nPress Ctrl+C to stop the marathon gracefully\n")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_marathon, daemon=True)
        monitor_thread.start()
        self.threads['monitor'] = monitor_thread

        # Wait for marathon to complete or interruption
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            logger.info("\nMarathon interrupted by user")

        # Generate final report
        self.generate_final_report()

        return True

    def stop_all(self):
        """Stop all trading processes"""
        logger.info("\nStopping all trading processes...")

        self.active = False

        for name, process in self.processes.items():
            try:
                if process.poll() is None:  # Still running
                    logger.info(f"Stopping {name.upper()}...")
                    process.terminate()
                    process.wait(timeout=10)
                    logger.info(f"✓ {name.upper()} stopped")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
                try:
                    process.kill()
                except:
                    pass

        logger.info("All trading processes stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Master Orchestrator - 24-Hour Marathon')
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo',
                        help='Trading mode for OKX (MT5 always uses demo accounts)')
    parser.add_argument('--duration', type=int, default=24,
                        help='Marathon duration in hours (default: 24)')
    args = parser.parse_args()

    orchestrator = TradingMasterOrchestrator()
    orchestrator.marathon_duration_hours = args.duration

    demo_mode = args.mode == 'demo'

    if not demo_mode:
        logger.warning("\n" + "!" * 70)
        logger.warning("WARNING: You are about to start LIVE trading with REAL MONEY on OKX!")
        logger.warning("!" * 70)
        response = input("\nType 'YES I UNDERSTAND' to proceed with live trading: ")
        if response != 'YES I UNDERSTAND':
            logger.info("Live trading cancelled")
            return

    try:
        orchestrator.start_marathon(demo_mode=demo_mode)
    except Exception as e:
        logger.error(f"Fatal error in marathon: {e}")
        orchestrator.stop_all()


if __name__ == "__main__":
    main()
