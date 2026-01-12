"""
7-Day Comprehensive Backtesting Suite
Extended backtesting across all risk profiles with detailed performance analysis
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from backtesting_engine import BacktestingEngine, run_all_profiles_backtest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('7DayBacktest')


class ExtendedBacktestRunner:
    """Extended backtesting with performance monitoring and risk adjustment"""

    def __init__(self):
        """Initialize extended backtest runner"""
        self.results = {}
        self.recommendations = []

    def run_7day_backtest(self):
        """Run 7-day backtest for all profiles"""
        logger.info("\n" + "=" * 70)
        logger.info("7-DAY COMPREHENSIVE BACKTEST")
        logger.info("=" * 70)
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("Testing: Beginner, Novice, Advanced profiles")
        logger.info("Duration: 7 days (168 hours)")
        logger.info("=" * 70 + "\n")

        # Run backtest for all profiles
        self.results = run_all_profiles_backtest(days=7)

        # Analyze results
        self.analyze_performance()
        self.generate_recommendations()
        self.export_comprehensive_report()

        return self.results

    def analyze_performance(self):
        """Analyze performance across all profiles"""
        logger.info("\n" + "=" * 70)
        logger.info("PERFORMANCE ANALYSIS")
        logger.info("=" * 70 + "\n")

        for profile, metrics in self.results.items():
            if 'total_trades' not in metrics or metrics['total_trades'] == 0:
                logger.warning(f"{profile.upper()}: No trades executed - market conditions too stable")
                continue

            logger.info(f"📊 {profile.upper()} PROFILE:")
            logger.info(f"  Total Trades: {metrics['total_trades']}")
            logger.info(f"  Win Rate: {metrics['win_rate']}%")
            logger.info(f"  ROI: {metrics['roi_percentage']}%")
            logger.info(f"  Net Profit: ${metrics['net_profit']:.2f}")
            logger.info(f"  Profit Factor: {metrics['profit_factor']:.2f}")
            logger.info(f"  Final Capital: ${metrics['final_capital']:,.2f}")

            # Performance evaluation
            if metrics['roi_percentage'] > 5:
                logger.info(f"  ✅ Excellent performance!")
            elif metrics['roi_percentage'] > 0:
                logger.info(f"  ✓ Profitable")
            else:
                logger.info(f"  ⚠️ Unprofitable - needs adjustment")

            logger.info("")

    def generate_recommendations(self):
        """Generate recommendations based on backtest results"""
        logger.info("\n" + "=" * 70)
        logger.info("RISK PARAMETER RECOMMENDATIONS")
        logger.info("=" * 70 + "\n")

        for profile, metrics in self.results.items():
            if 'total_trades' not in metrics or metrics['total_trades'] == 0:
                continue

            recommendations = {
                "profile": profile,
                "current_performance": {
                    "roi": metrics['roi_percentage'],
                    "win_rate": metrics['win_rate'],
                    "profit_factor": metrics['profit_factor']
                },
                "recommendations": []
            }

            # Win rate analysis
            if metrics['win_rate'] < 50:
                recommendations["recommendations"].append({
                    "parameter": "confidence_threshold",
                    "action": "INCREASE",
                    "reason": f"Win rate below 50% ({metrics['win_rate']}%)",
                    "suggested_value": "+5% (higher quality signals)"
                })

            # Profit factor analysis
            if metrics['profit_factor'] < 1.5:
                recommendations["recommendations"].append({
                    "parameter": "stop_loss / take_profit ratio",
                    "action": "ADJUST",
                    "reason": f"Low profit factor ({metrics['profit_factor']:.2f})",
                    "suggested_value": "Wider take profit or tighter stop loss"
                })

            # ROI analysis
            if metrics['roi_percentage'] < 0:
                recommendations["recommendations"].append({
                    "parameter": "pattern_selection",
                    "action": "REVIEW",
                    "reason": "Negative ROI - some patterns underperforming",
                    "suggested_value": "Disable low-confidence patterns"
                })
            elif metrics['roi_percentage'] > 10:
                recommendations["recommendations"].append({
                    "parameter": "position_size",
                    "action": "CONSIDER INCREASE",
                    "reason": f"Strong performance ({metrics['roi_percentage']}% ROI)",
                    "suggested_value": "Increase position size by 0.5% if comfortable"
                })

            # Trading frequency analysis
            daily_trades = metrics['total_trades'] / 7
            if daily_trades < 1:
                recommendations["recommendations"].append({
                    "parameter": "confidence_threshold",
                    "action": "DECREASE",
                    "reason": f"Low trading frequency ({daily_trades:.1f} trades/day)",
                    "suggested_value": "-5% (more trading opportunities)"
                })

            self.recommendations.append(recommendations)

            # Print recommendations
            if recommendations["recommendations"]:
                logger.info(f"🎯 {profile.upper()} RECOMMENDATIONS:")
                for rec in recommendations["recommendations"]:
                    logger.info(f"  • {rec['parameter']}: {rec['action']}")
                    logger.info(f"    Reason: {rec['reason']}")
                    logger.info(f"    Suggestion: {rec['suggested_value']}")
                logger.info("")
            else:
                logger.info(f"✅ {profile.upper()}: Parameters optimal - no changes recommended\n")

    def export_comprehensive_report(self):
        """Export comprehensive 7-day backtest report"""
        output_dir = Path(__file__).parent.parent.parent / 'backtest-results'
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export recommendations
        recommendations_file = output_dir / f'7day_recommendations_{timestamp}.json'
        with open(recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)

        # Export full results
        results_file = output_dir / f'7day_full_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration_days": 7,
                "profiles_tested": list(self.results.keys()),
                "results": self.results,
                "recommendations": self.recommendations
            }, f, indent=2)

        # Generate markdown report
        markdown_report = self.generate_markdown_report()
        report_file = output_dir / f'7day_backtest_report_{timestamp}.md'
        with open(report_file, 'w') as f:
            f.write(markdown_report)

        logger.info("\n" + "=" * 70)
        logger.info("REPORTS EXPORTED")
        logger.info("=" * 70)
        logger.info(f"Recommendations: {recommendations_file}")
        logger.info(f"Full Results: {results_file}")
        logger.info(f"Markdown Report: {report_file}")
        logger.info("=" * 70 + "\n")

    def generate_markdown_report(self):
        """Generate markdown backtest report"""
        report = f"""# 7-Day Backtesting Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** 7 days (168 hours)
**Profiles Tested:** Beginner, Novice, Advanced

---

## Performance Summary

| Profile | Trades | Win Rate | ROI | Net Profit | Profit Factor | Final Capital |
|---------|--------|----------|-----|------------|---------------|---------------|
"""

        for profile, metrics in self.results.items():
            if 'total_trades' in metrics and metrics['total_trades'] > 0:
                report += f"| {profile.capitalize()} | {metrics['total_trades']} | {metrics['win_rate']}% | {metrics['roi_percentage']}% | ${metrics['net_profit']:.2f} | {metrics['profit_factor']:.2f} | ${metrics['final_capital']:,.2f} |\n"

        report += "\n---\n\n## Detailed Analysis\n\n"

        for profile, metrics in self.results.items():
            if 'total_trades' not in metrics or metrics['total_trades'] == 0:
                report += f"### {profile.upper()} Profile\n\n**Status:** No trades executed during 7-day period\n\n"
                continue

            report += f"""### {profile.upper()} Profile

**Trading Activity:**
- Total Trades: {metrics['total_trades']}
- Winning Trades: {metrics['winning_trades']}
- Losing Trades: {metrics['losing_trades']}
- Win Rate: {metrics['win_rate']}%

**Financial Performance:**
- Initial Capital: ${metrics['initial_capital']:,.2f}
- Final Capital: ${metrics['final_capital']:,.2f}
- Net Profit: ${metrics['net_profit']:.2f}
- ROI: {metrics['roi_percentage']}%

**Trade Quality:**
- Average Win: ${metrics['avg_win']:.2f}
- Average Loss: ${metrics['avg_loss']:.2f}
- Profit Factor: {metrics['profit_factor']:.2f}
- Largest Win: ${metrics.get('largest_win', 0):.2f}
- Largest Loss: ${metrics.get('largest_loss', 0):.2f}

"""

        # Add recommendations section
        report += "\n---\n\n## Risk Parameter Recommendations\n\n"

        for rec in self.recommendations:
            if rec['recommendations']:
                report += f"### {rec['profile'].upper()} Profile\n\n"
                for r in rec['recommendations']:
                    report += f"""**{r['parameter']}:** {r['action']}
- Reason: {r['reason']}
- Suggestion: {r['suggested_value']}

"""

        report += """---

## Next Steps

1. **Review Performance:** Analyze which profile best matches your risk tolerance
2. **Adjust Parameters:** Implement recommended changes if ROI is below target
3. **Sandbox Testing:** Test adjusted parameters in sandbox environment
4. **Live Trading:** Graduate to live trading after successful sandbox testing

---

*Generated by Agent X2.0 Backtesting Engine*
"""

        return report


def main():
    """Run 7-day comprehensive backtest"""
    print("\n" + "📊" * 35)
    print("    7-DAY COMPREHENSIVE BACKTEST")
    print("    All Risk Profiles - Extended Analysis")
    print("📊" * 35 + "\n")

    runner = ExtendedBacktestRunner()
    results = runner.run_7day_backtest()

    logger.info("\n✅ 7-DAY BACKTEST COMPLETE")
    logger.info("\nNext Steps:")
    logger.info("1. Review recommendations in backtest-results/")
    logger.info("2. Adjust risk parameters if needed")
    logger.info("3. Run sandbox testing with adjusted parameters")
    logger.info("4. Monitor performance in live sandbox environment")

    return 0


if __name__ == "__main__":
    sys.exit(main())
