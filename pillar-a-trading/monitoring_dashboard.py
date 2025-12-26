"""
Real-time Monitoring Dashboard
Displays live trading bot performance, trades, and system health
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import threading

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from bot_performance_tracker import PerformanceTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MonitoringDashboard')


class MonitoringDashboard:
    """
    Real-time monitoring dashboard for trading bot
    Displays performance metrics, active trades, and system health
    """

    def __init__(self,
                 mode: str = "paper",
                 profile: str = "beginner",
                 refresh_interval: int = 5):
        """
        Initialize monitoring dashboard

        Args:
            mode: Trading mode
            profile: Risk profile
            refresh_interval: Dashboard refresh interval in seconds
        """
        self.mode = mode
        self.profile = profile
        self.refresh_interval = refresh_interval
        self.running = False

        # Paths
        self.log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot'
        self.performance_dir = self.log_dir / 'performance'
        self.monitoring_dir = self.log_dir / 'monitoring'
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Monitoring Dashboard initialized - Mode: {mode}, Profile: {profile}")

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def get_latest_performance_data(self) -> Optional[Dict[str, Any]]:
        """Get latest performance data from logs"""
        try:
            # Find the most recent performance JSON file
            json_files = list(self.performance_dir.glob(f"performance_{self.mode}_{self.profile}_*.json"))

            if not json_files:
                return None

            # Sort by modification time, get most recent
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

            with open(latest_file, 'r') as f:
                data = json.load(f)

            return data

        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return None

    def get_bot_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        try:
            # Check if bot log file exists and is recent
            log_files = list(self.log_dir.glob('bot_runner_*.log'))

            if not log_files:
                return {"status": "NOT_RUNNING", "last_update": None}

            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            last_modified = datetime.fromtimestamp(latest_log.stat().st_mtime)
            time_since_update = datetime.now() - last_modified

            # Consider bot running if log was updated in last 2 minutes
            if time_since_update.total_seconds() < 120:
                status = "RUNNING"
            else:
                status = "IDLE"

            return {
                "status": status,
                "last_update": last_modified,
                "log_file": str(latest_log)
            }

        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {"status": "UNKNOWN", "error": str(e)}

    def format_metric(self, value: Any, decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
        """Format metric value for display"""
        try:
            if isinstance(value, (int, float)):
                if decimals == 0:
                    return f"{prefix}{int(value)}{suffix}"
                else:
                    return f"{prefix}{value:.{decimals}f}{suffix}"
            else:
                return str(value)
        except:
            return str(value)

    def render_dashboard(self, data: Optional[Dict[str, Any]] = None):
        """Render the monitoring dashboard"""
        self.clear_screen()

        # Header
        print("="*100)
        print(" "*35 + "24/7 TRADING BOT DASHBOARD")
        print("="*100)
        print()

        # System Status
        print("SYSTEM STATUS")
        print("-"*100)

        bot_status = self.get_bot_status()
        print(f"Bot Status:        {bot_status['status']}")
        print(f"Trading Mode:      {self.mode.upper()}")
        print(f"Risk Profile:      {self.profile.capitalize()}")
        print(f"Last Update:       {bot_status.get('last_update', 'N/A')}")
        print(f"Dashboard Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if not data:
            print("Waiting for performance data...")
            print()
            print("="*100)
            return

        metrics = data.get('metrics', {})

        # Trading Overview
        print("TRADING OVERVIEW")
        print("-"*100)
        print(f"Total Trades:      {metrics.get('total_trades', 0)}")
        print(f"Open Positions:    {metrics.get('open_trades', 0)}")
        print(f"Closed Trades:     {metrics.get('closed_trades', 0)}")
        print(f"Winning Trades:    {metrics.get('winning_trades', 0)} ({self.format_metric(metrics.get('win_rate', 0), 2, '', '%')})")
        print(f"Losing Trades:     {metrics.get('losing_trades', 0)}")
        print()

        # Capital & Performance
        print("CAPITAL & PERFORMANCE")
        print("-"*100)
        initial = metrics.get('initial_capital', 10000)
        current = metrics.get('current_capital', 10000)
        net_profit = metrics.get('net_profit', 0)
        roi = metrics.get('roi_percentage', 0)

        # Color coding (green for profit, red for loss)
        profit_indicator = "+" if net_profit >= 0 else ""

        print(f"Initial Capital:   ${initial:,.2f}")
        print(f"Current Capital:   ${current:,.2f}")
        print(f"Net Profit:        {profit_indicator}${net_profit:,.2f}")
        print(f"ROI:               {profit_indicator}{roi:.2f}%")
        print(f"Daily ROI:         {self.format_metric(metrics.get('daily_roi', 0), 2, '', '%')}")
        print()

        # Profit Metrics
        print("PROFIT METRICS")
        print("-"*100)
        print(f"Total Profit:      ${metrics.get('total_profit', 0):,.2f}")
        print(f"Total Loss:        ${metrics.get('total_loss', 0):,.2f}")
        print(f"Profit Factor:     {metrics.get('profit_factor', 'N/A')}")
        print(f"Avg Win:           ${metrics.get('avg_win', 0):,.2f}")
        print(f"Avg Loss:          ${metrics.get('avg_loss', 0):,.2f}")
        print(f"Largest Win:       ${metrics.get('largest_win', 0):,.2f}")
        print(f"Largest Loss:      ${metrics.get('largest_loss', 0):,.2f}")
        print()

        # Risk Metrics
        print("RISK METRICS")
        print("-"*100)
        print(f"Peak Capital:      ${metrics.get('peak_capital', 10000):,.2f}")
        print(f"Max Drawdown:      ${metrics.get('max_drawdown', 0):,.2f} ({metrics.get('max_drawdown_pct', 0):.2f}%)")
        print(f"Current Drawdown:  ${metrics.get('current_drawdown', 0):,.2f} ({metrics.get('current_drawdown_pct', 0):.2f}%)")
        print(f"Sharpe Ratio:      {metrics.get('sharpe_ratio', 0):.4f}")
        print()

        # Recent Trades
        print("RECENT TRADES (Last 5)")
        print("-"*100)

        trades = data.get('trades', [])
        if trades:
            # Sort by entry time, get last 5
            recent_trades = sorted(trades, key=lambda t: t.get('entry_time', ''), reverse=True)[:5]

            print(f"{'ID':<5} {'Pair':<10} {'Type':<6} {'Entry':<12} {'Exit':<12} {'P/L':<15} {'Status':<10}")
            print("-"*100)

            for trade in recent_trades:
                trade_id = str(trade.get('id', 'N/A'))[:5]
                pair = str(trade.get('pair', 'N/A'))[:10]
                trade_type = str(trade.get('type', 'N/A'))[:6]
                entry = f"${trade.get('entry_price', 0):.2f}"
                exit_price = trade.get('exit_price')
                exit_str = f"${exit_price:.2f}" if exit_price else "N/A"
                pl = trade.get('profit_loss')
                pl_str = f"${pl:,.2f}" if pl is not None else "N/A"
                status = str(trade.get('status', 'N/A'))[:10]

                print(f"{trade_id:<5} {pair:<10} {trade_type:<6} {entry:<12} {exit_str:<12} {pl_str:<15} {status:<10}")
        else:
            print("No trades recorded yet")

        print()

        # Footer
        print("="*100)
        print(f"Auto-refresh every {self.refresh_interval} seconds | Press Ctrl+C to exit")
        print("="*100)

    def save_dashboard_snapshot(self, data: Dict[str, Any]):
        """Save dashboard snapshot to log"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = self.monitoring_dir / f"dashboard_snapshot_{timestamp}.json"

            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "profile": self.profile,
                "bot_status": self.get_bot_status(),
                "metrics": data.get('metrics', {}),
                "recent_trades": data.get('trades', [])[:5]
            }

            with open(snapshot_path, 'w') as f:
                json.dump(snapshot, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving dashboard snapshot: {e}")

    def run(self):
        """Run monitoring dashboard"""
        self.running = True

        logger.info("Starting monitoring dashboard...")
        logger.info(f"Refresh interval: {self.refresh_interval} seconds")

        try:
            while self.running:
                # Get latest performance data
                data = self.get_latest_performance_data()

                # Render dashboard
                self.render_dashboard(data)

                # Save snapshot periodically (every 5 minutes)
                if data and datetime.now().minute % 5 == 0:
                    self.save_dashboard_snapshot(data)

                # Wait for next refresh
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            logger.info("Dashboard stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error in dashboard: {e}")
            self.running = False

    def stop(self):
        """Stop monitoring dashboard"""
        self.running = False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Bot Monitoring Dashboard')
    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'demo', 'live'],
                       help='Trading mode (default: paper)')
    parser.add_argument('--profile', type=str, default='beginner',
                       choices=['beginner', 'novice', 'advanced'],
                       help='Risk profile (default: beginner)')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds (default: 5)')

    args = parser.parse_args()

    # Create and run dashboard
    dashboard = MonitoringDashboard(
        mode=args.mode,
        profile=args.profile,
        refresh_interval=args.refresh
    )

    try:
        dashboard.run()
    except KeyboardInterrupt:
        logger.info("Dashboard stopped")
        dashboard.stop()


if __name__ == "__main__":
    main()
