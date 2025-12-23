"""
Generate Initial Performance Report
Creates comprehensive performance report from trading bot data
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from bot_performance_tracker import PerformanceTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PerformanceReportGenerator')


def get_latest_performance_data(mode: str = "paper", profile: str = "beginner") -> Optional[Dict[str, Any]]:
    """Get latest performance data from JSON files"""
    try:
        performance_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'performance'

        if not performance_dir.exists():
            logger.warning("Performance directory not found")
            return None

        # Find latest performance JSON
        json_files = list(performance_dir.glob(f"performance_{mode}_{profile}_*.json"))

        if not json_files:
            logger.warning("No performance data found")
            return None

        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

        with open(latest_file, 'r') as f:
            data = json.load(f)

        return data

    except Exception as e:
        logger.error(f"Error loading performance data: {e}")
        return None


def generate_initial_report(mode: str = "paper", profile: str = "beginner") -> str:
    """Generate initial performance report"""

    logger.info("="*80)
    logger.info("GENERATING INITIAL PERFORMANCE REPORT")
    logger.info("="*80)

    # Get performance data
    data = get_latest_performance_data(mode, profile)

    # Create report directory
    report_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / 'trading_bot_performance_initial.json'

    if data:
        metrics = data.get('metrics', {})
        trades = data.get('trades', [])

        # Create comprehensive report
        report = {
            "report_type": "Initial Performance Report",
            "generated_at": datetime.now().isoformat(),
            "mode": mode,
            "profile": profile,
            "session_info": {
                "start_time": data.get('metadata', {}).get('session_start'),
                "duration": "Initial test period",
                "status": "Running"
            },
            "summary": {
                "total_trades": metrics.get('total_trades', 0),
                "open_trades": metrics.get('open_trades', 0),
                "closed_trades": metrics.get('closed_trades', 0),
                "win_rate": f"{metrics.get('win_rate', 0):.2f}%",
                "initial_capital": f"${metrics.get('initial_capital', 0):,.2f}",
                "current_capital": f"${metrics.get('current_capital', 0):,.2f}",
                "net_profit": f"${metrics.get('net_profit', 0):,.2f}",
                "roi": f"{metrics.get('roi_percentage', 0):.2f}%"
            },
            "performance_metrics": {
                "winning_trades": metrics.get('winning_trades', 0),
                "losing_trades": metrics.get('losing_trades', 0),
                "total_profit": f"${metrics.get('total_profit', 0):,.2f}",
                "total_loss": f"${metrics.get('total_loss', 0):,.2f}",
                "profit_factor": str(metrics.get('profit_factor', 'N/A')),
                "avg_win": f"${metrics.get('avg_win', 0):,.2f}",
                "avg_loss": f"${metrics.get('avg_loss', 0):,.2f}",
                "largest_win": f"${metrics.get('largest_win', 0):,.2f}",
                "largest_loss": f"${metrics.get('largest_loss', 0):,.2f}"
            },
            "risk_metrics": {
                "peak_capital": f"${metrics.get('peak_capital', 0):,.2f}",
                "max_drawdown": f"${metrics.get('max_drawdown', 0):,.2f}",
                "max_drawdown_pct": f"{metrics.get('max_drawdown_pct', 0):.2f}%",
                "sharpe_ratio": f"{metrics.get('sharpe_ratio', 0):.4f}"
            },
            "trades": trades,
            "analysis": generate_analysis(metrics, trades)
        }

    else:
        # No data yet, create placeholder report
        report = {
            "report_type": "Initial Performance Report",
            "generated_at": datetime.now().isoformat(),
            "mode": mode,
            "profile": profile,
            "status": "Bot is starting up - No trades executed yet",
            "summary": {
                "total_trades": 0,
                "initial_capital": "$10,000.00",
                "current_capital": "$10,000.00",
                "net_profit": "$0.00",
                "roi": "0.00%"
            },
            "analysis": {
                "status": "Waiting for first trades",
                "recommendation": "Bot is in paper trading mode. Monitor for trade execution."
            }
        }

    # Save report
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Initial performance report saved: {report_path}")

    # Also create text version
    create_text_report(report, report_dir / 'trading_bot_performance_initial.txt')

    # Print summary
    print_report_summary(report)

    return str(report_path)


def generate_analysis(metrics: Dict[str, Any], trades: list) -> Dict[str, Any]:
    """Generate performance analysis"""

    analysis = {
        "overall_status": "Unknown",
        "profitability": "Unknown",
        "risk_level": "Unknown",
        "recommendations": []
    }

    try:
        # Overall status
        roi = metrics.get('roi_percentage', 0)
        if roi > 5:
            analysis["overall_status"] = "Excellent"
        elif roi > 2:
            analysis["overall_status"] = "Good"
        elif roi > 0:
            analysis["overall_status"] = "Positive"
        elif roi == 0:
            analysis["overall_status"] = "Neutral"
        else:
            analysis["overall_status"] = "Negative"

        # Profitability
        win_rate = metrics.get('win_rate', 0)
        if win_rate >= 60:
            analysis["profitability"] = "High"
        elif win_rate >= 50:
            analysis["profitability"] = "Moderate"
        elif win_rate >= 40:
            analysis["profitability"] = "Low"
        else:
            analysis["profitability"] = "Poor"

        # Risk level
        max_drawdown = metrics.get('max_drawdown_pct', 0)
        if max_drawdown < 2:
            analysis["risk_level"] = "Very Low"
        elif max_drawdown < 5:
            analysis["risk_level"] = "Low"
        elif max_drawdown < 10:
            analysis["risk_level"] = "Moderate"
        else:
            analysis["risk_level"] = "High"

        # Recommendations
        if win_rate < 50:
            analysis["recommendations"].append("Consider adjusting entry criteria or confidence threshold")

        if max_drawdown > 5:
            analysis["recommendations"].append("Monitor risk management - Drawdown is elevated")

        if metrics.get('total_trades', 0) < 10:
            analysis["recommendations"].append("Continue monitoring - More data needed for conclusive analysis")

        if roi > 0 and win_rate > 55:
            analysis["recommendations"].append("Strategy performing well - Continue current approach")

    except Exception as e:
        logger.error(f"Error generating analysis: {e}")

    return analysis


def create_text_report(report: Dict[str, Any], filepath: Path):
    """Create human-readable text report"""

    with open(filepath, 'w') as f:
        f.write("="*80 + "\n")
        f.write("24/7 TRADING BOT - INITIAL PERFORMANCE REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"Report Generated: {report.get('generated_at', 'N/A')}\n")
        f.write(f"Trading Mode: {report.get('mode', 'N/A').upper()}\n")
        f.write(f"Risk Profile: {report.get('profile', 'N/A').capitalize()}\n")
        f.write("\n")

        # Summary
        f.write("SUMMARY\n")
        f.write("-"*80 + "\n")
        summary = report.get('summary', {})
        for key, value in summary.items():
            f.write(f"{key.replace('_', ' ').title():<25} {value}\n")
        f.write("\n")

        # Performance metrics
        if 'performance_metrics' in report:
            f.write("PERFORMANCE METRICS\n")
            f.write("-"*80 + "\n")
            metrics = report.get('performance_metrics', {})
            for key, value in metrics.items():
                f.write(f"{key.replace('_', ' ').title():<25} {value}\n")
            f.write("\n")

        # Risk metrics
        if 'risk_metrics' in report:
            f.write("RISK METRICS\n")
            f.write("-"*80 + "\n")
            risk = report.get('risk_metrics', {})
            for key, value in risk.items():
                f.write(f"{key.replace('_', ' ').title():<25} {value}\n")
            f.write("\n")

        # Analysis
        if 'analysis' in report:
            f.write("ANALYSIS\n")
            f.write("-"*80 + "\n")
            analysis = report.get('analysis', {})

            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    if key == 'recommendations' and isinstance(value, list):
                        f.write("\nRecommendations:\n")
                        for rec in value:
                            f.write(f"  • {rec}\n")
                    else:
                        f.write(f"{key.replace('_', ' ').title():<25} {value}\n")
            else:
                f.write(str(analysis) + "\n")

            f.write("\n")

        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")

    logger.info(f"Text report saved: {filepath}")


def print_report_summary(report: Dict[str, Any]):
    """Print report summary to console"""

    print("\n" + "="*80)
    print("INITIAL PERFORMANCE REPORT - SUMMARY")
    print("="*80)

    summary = report.get('summary', {})
    print(f"\nTotal Trades: {summary.get('total_trades', 0)}")
    print(f"Initial Capital: {summary.get('initial_capital', '$0')}")
    print(f"Current Capital: {summary.get('current_capital', '$0')}")
    print(f"Net Profit: {summary.get('net_profit', '$0')}")
    print(f"ROI: {summary.get('roi', '0%')}")
    print(f"Win Rate: {summary.get('win_rate', '0%')}")

    if 'analysis' in report:
        analysis = report.get('analysis', {})
        print(f"\nOverall Status: {analysis.get('overall_status', 'Unknown')}")
        print(f"Profitability: {analysis.get('profitability', 'Unknown')}")
        print(f"Risk Level: {analysis.get('risk_level', 'Unknown')}")

        recs = analysis.get('recommendations', [])
        if recs:
            print("\nRecommendations:")
            for rec in recs:
                print(f"  • {rec}")

    print("\n" + "="*80 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate Initial Performance Report')
    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'demo', 'live'],
                       help='Trading mode (default: paper)')
    parser.add_argument('--profile', type=str, default='beginner',
                       choices=['beginner', 'novice', 'advanced'],
                       help='Risk profile (default: beginner)')

    args = parser.parse_args()

    # Generate report
    report_path = generate_initial_report(mode=args.mode, profile=args.profile)

    print(f"\n✓ Initial performance report generated: {report_path}")


if __name__ == "__main__":
    main()
