"""
Sandbox Trading Configuration & Live Monitoring
Real-time monitoring for sandbox and live trading environments
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'agent-3.0'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'zapier-integration'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SandboxMonitor')


class SandboxTradingMonitor:
    """Monitor and manage sandbox/live trading operations"""

    def __init__(self, environment: str = "sandbox", profile: str = "beginner"):
        """Initialize sandbox trading monitor"""
        self.environment = environment
        self.profile = profile
        self.config = self.load_config()
        self.trades = []
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "current_capital": 10000,
            "peak_capital": 10000,
            "drawdown": 0,
            "alerts": []
        }
        logger.info(f"Sandbox Monitor initialized - {environment.upper()} | {profile.upper()}")

    def load_config(self) -> Dict[str, Any]:
        """Load trading configuration"""
        config_file = Path(__file__).parent.parent / 'pillar-a-trading' / 'config' / 'trading_risk_profiles.json'

        if not config_file.exists():
            logger.error("Risk profiles not found")
            return {}

        with open(config_file, 'r') as f:
            all_profiles = json.load(f)

        profile_config = all_profiles['profiles'].get(self.profile, {})
        env_config = all_profiles.get('environment_settings', {}).get(self.environment, {})

        return {
            "profile": profile_config,
            "environment": env_config,
            "integration": all_profiles.get('integration_settings', {})
        }

    def check_live_readiness(self) -> Dict[str, Any]:
        """Check if system is ready for live trading"""
        logger.info("\n" + "="*70)
        logger.info("LIVE TRADING READINESS CHECK")
        logger.info("="*70 + "\n")

        checks = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "checks": [],
            "ready": True
        }

        # 1. Sandbox testing completed
        sandbox_days = self.calculate_sandbox_days()
        sandbox_ok = sandbox_days >= 7
        checks["checks"].append({
            "name": "Sandbox Testing Duration",
            "required": "7+ days",
            "actual": f"{sandbox_days} days",
            "passed": sandbox_ok,
            "critical": True
        })
        if not sandbox_ok:
            checks["ready"] = False

        # 2. Minimum trades executed
        min_trades = 10
        trades_ok = self.metrics["total_trades"] >= min_trades
        checks["checks"].append({
            "name": "Minimum Trades Executed",
            "required": f"{min_trades}+",
            "actual": self.metrics["total_trades"],
            "passed": trades_ok,
            "critical": True
        })
        if not trades_ok:
            checks["ready"] = False

        # 3. Win rate acceptable
        win_rate = (self.metrics["wins"] / self.metrics["total_trades"] * 100) if self.metrics["total_trades"] > 0 else 0
        win_rate_ok = win_rate >= 45
        checks["checks"].append({
            "name": "Win Rate",
            "required": "45%+",
            "actual": f"{win_rate:.1f}%",
            "passed": win_rate_ok,
            "critical": True
        })
        if not win_rate_ok:
            checks["ready"] = False

        # 4. Positive ROI
        roi = ((self.metrics["current_capital"] - 10000) / 10000 * 100)
        roi_ok = roi > 0
        checks["checks"].append({
            "name": "ROI (Profitability)",
            "required": "Positive",
            "actual": f"{roi:.2f}%",
            "passed": roi_ok,
            "critical": True
        })
        if not roi_ok:
            checks["ready"] = False

        # 5. Max drawdown acceptable
        max_drawdown = 15  # 15% max
        drawdown_ok = self.metrics["drawdown"] <= max_drawdown
        checks["checks"].append({
            "name": "Maximum Drawdown",
            "required": f"<{max_drawdown}%",
            "actual": f"{self.metrics['drawdown']:.2f}%",
            "passed": drawdown_ok,
            "critical": True
        })
        if not drawdown_ok:
            checks["ready"] = False

        # 6. API credentials configured
        api_ok = self.check_api_credentials()
        checks["checks"].append({
            "name": "Live API Credentials",
            "required": "Configured",
            "actual": "Configured" if api_ok else "Missing",
            "passed": api_ok,
            "critical": True
        })
        if not api_ok:
            checks["ready"] = False

        # 7. Zapier integration tested
        zapier_ok = self.check_zapier_integration()
        checks["checks"].append({
            "name": "Zapier Integration",
            "required": "Tested & Working",
            "actual": "Working" if zapier_ok else "Not Tested",
            "passed": zapier_ok,
            "critical": False
        })

        # Print results
        logger.info("READINESS CHECK RESULTS:")
        logger.info("-"*70)
        for check in checks["checks"]:
            status = "✅" if check["passed"] else "❌"
            critical = " [CRITICAL]" if check["critical"] else ""
            logger.info(f"{status} {check['name']}{critical}")
            logger.info(f"   Required: {check['required']} | Actual: {check['actual']}")
        logger.info("-"*70)

        if checks["ready"]:
            logger.info("\n✅ SYSTEM READY FOR LIVE TRADING")
            logger.info("\nNext Steps:")
            logger.info("1. Start with MINIMUM position sizes")
            logger.info("2. Enable email alerts for all trades")
            logger.info("3. Monitor closely for first 24 hours")
            logger.info("4. Review and adjust after first week")
        else:
            failed_critical = [c for c in checks["checks"] if not c["passed"] and c["critical"]]
            logger.warning(f"\n⚠️  NOT READY - {len(failed_critical)} CRITICAL CHECKS FAILED")
            logger.info("\nRequired Actions:")
            for check in failed_critical:
                logger.info(f"  • {check['name']}: Achieve {check['required']}")

        return checks

    def calculate_sandbox_days(self) -> int:
        """Calculate days of sandbox testing"""
        start = datetime.fromisoformat(self.metrics["start_time"])
        now = datetime.now()
        return (now - start).days

    def check_api_credentials(self) -> bool:
        """Check if live API credentials are configured"""
        try:
            from dotenv import load_dotenv
            load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

            kraken_key = os.getenv('KRAKEN_API_KEY')
            kraken_secret = os.getenv('KRAKEN_API_SECRET')

            return bool(kraken_key and kraken_secret and
                       not kraken_key.startswith('your_'))
        except:
            return False

    def check_zapier_integration(self) -> bool:
        """Check if Zapier integration is working"""
        try:
            from zapier_mcp_connector import ZapierMCPConnector
            connector = ZapierMCPConnector()
            return bool(connector.bearer_token)
        except:
            return False

    def generate_performance_report(self) -> str:
        """Generate performance report"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           SANDBOX TRADING PERFORMANCE REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

Environment: {self.environment.upper()}
Profile: {self.profile.upper()}
Duration: {self.calculate_sandbox_days()} days

TRADING ACTIVITY:
  Total Trades: {self.metrics['total_trades']}
  Winning Trades: {self.metrics['wins']}
  Losing Trades: {self.metrics['losses']}
  Win Rate: {(self.metrics['wins']/self.metrics['total_trades']*100) if self.metrics['total_trades'] > 0 else 0:.1f}%

FINANCIAL PERFORMANCE:
  Starting Capital: $10,000.00
  Current Capital: ${self.metrics['current_capital']:,.2f}
  Peak Capital: ${self.metrics['peak_capital']:,.2f}
  Net Profit/Loss: ${self.metrics['current_capital'] - 10000:,.2f}
  ROI: {((self.metrics['current_capital'] - 10000) / 10000 * 100):.2f}%
  Max Drawdown: {self.metrics['drawdown']:.2f}%

ALERTS: {len(self.metrics['alerts'])}
"""
        return report


def create_agent_30_config():
    """Create Agent 3.0 complete configuration"""
    config = {
        "version": "3.0.0",
        "deployment_date": datetime.now().strftime("%Y-%m-%d"),
        "environments": {
            "paper": {
                "enabled": True,
                "description": "Paper trading for learning",
                "default_profile": "beginner"
            },
            "sandbox": {
                "enabled": True,
                "description": "Sandbox testing with Kraken sandbox API",
                "default_profile": "novice",
                "requires_approval": False
            },
            "live": {
                "enabled": False,
                "description": "Live trading with real money",
                "default_profile": "beginner",
                "requires_approval": True,
                "requires_2fa": True
            }
        },
        "risk_management": {
            "global_kill_switch": True,
            "max_daily_loss_percent": 5,
            "max_weekly_loss_percent": 10,
            "emergency_halt_threshold": 15,
            "require_manual_approval_above": 1000
        },
        "integrations": {
            "zapier_mcp": {
                "enabled": True,
                "log_all_trades": True,
                "alert_on_loss": True,
                "alert_on_win": False,
                "daily_summary": True
            },
            "microsoft_365": {
                "enabled": True,
                "sharepoint_logging": True,
                "teams_alerts": False
            }
        },
        "monitoring": {
            "log_level": "INFO",
            "performance_tracking": True,
            "send_daily_report": True,
            "send_weekly_summary": True
        }
    }

    output_file = Path(__file__).parent.parent / 'pillar-a-trading' / 'agent-3.0' / 'agent_3_config.json'
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)

    logger.info(f"✅ Agent 3.0 configuration created: {output_file}")
    return config


def main():
    """Run sandbox monitoring and readiness check"""
    print("\n" + "🎯"*35)
    print("    AGENT 3.0 - SANDBOX TRADING MONITOR")
    print("    Live Trading Readiness Assessment")
    print("🎯"*35 + "\n")

    # Create Agent 3.0 config
    create_agent_30_config()

    # Initialize monitor
    monitor = SandboxTradingMonitor(environment="sandbox", profile="novice")

    # Check readiness
    readiness = monitor.check_live_readiness()

    # Generate report
    report = monitor.generate_performance_report()
    print(report)

    # Export readiness check
    output_dir = Path(__file__).parent.parent / 'backtest-results'
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f'live_trading_readiness_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(readiness, f, indent=2)

    logger.info(f"\nReadiness report saved: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
