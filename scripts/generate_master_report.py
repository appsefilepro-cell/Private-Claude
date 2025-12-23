#!/usr/bin/env python3
"""
Generate Master Trading Bot Performance Report
Combines all data from paper trading, backtests, continuous testing, and Kraken simulations
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def main():
    base_dir = Path(__file__).parent.parent

    # Gather all data sources
    report = {
        "report_timestamp": datetime.utcnow().isoformat(),
        "report_type": "MASTER_TRADING_BOT_PERFORMANCE_REPORT",
        "executive_summary": {},
        "data_sources": {},
        "kraken_continuous_testing": {},
        "historical_backtests": {},
        "paper_trading_performance": {},
        "consolidated_metrics": {}
    }

    # 1. Get consolidated data from gather_all_bot_data
    consolidated_files = glob.glob(str(base_dir / 'logs' / 'trading_bot' / 'consolidated' / '*.json'))
    if consolidated_files:
        latest_consolidated = sorted(consolidated_files)[-1]
        with open(latest_consolidated) as f:
            consolidated_data = json.load(f)
            report["data_sources"]["consolidated_historical"] = {
                "file": os.path.basename(latest_consolidated),
                "summary": consolidated_data.get('summary', {})
            }

    # 2. Get Kraken continuous testing results
    kraken_perf_files = glob.glob(str(base_dir / 'logs' / 'trading_bot' / 'continuous' / 'performance_report_*.json'))
    if kraken_perf_files:
        latest_kraken = sorted(kraken_perf_files)[-1]
        with open(latest_kraken) as f:
            kraken_data = json.load(f)
            report["kraken_continuous_testing"] = {
                "file": os.path.basename(latest_kraken),
                "metadata": kraken_data.get('metadata', {}),
                "statistics": kraken_data.get('statistics', {}),
                "pattern_distribution": kraken_data.get('pattern_distribution', {}),
                "pair_distribution": kraken_data.get('pair_distribution', {})
            }

    # 3. Get latest backtest results
    backtest_files = glob.glob(str(base_dir / 'pillar-a-trading' / 'backtest-results' / '*_metrics_*.json'))
    backtest_summary = {"beginner": None, "novice": None, "advanced": None}

    for profile in ["beginner", "novice", "advanced"]:
        profile_files = [f for f in backtest_files if profile in f]
        if profile_files:
            latest_file = sorted(profile_files)[-1]
            with open(latest_file) as f:
                backtest_summary[profile] = json.load(f)

    report["historical_backtests"] = backtest_summary

    # 4. Get latest paper trading performance
    paper_files = glob.glob(str(base_dir / 'logs' / 'trading_bot' / 'performance' / 'performance_paper_*.json'))
    if paper_files:
        latest_paper = sorted(paper_files)[-1]
        with open(latest_paper) as f:
            paper_data = json.load(f)
            report["paper_trading_performance"] = {
                "file": os.path.basename(latest_paper),
                "metrics": paper_data.get('metrics', {}),
                "trades": paper_data.get('trades', [])
            }

    # 5. Calculate executive summary
    exec_summary = {
        "total_systems_deployed": 0,
        "total_tests_executed": 0,
        "total_patterns_tested": 0,
        "total_pairs_tested": 0,
        "total_signals_generated": 0,
        "total_trades_executed": 0,
        "total_capital_tested": 0,
        "net_profit_all_systems": 0,
        "systems": []
    }

    # Kraken continuous
    if report["kraken_continuous_testing"]:
        stats = report["kraken_continuous_testing"]["statistics"]
        exec_summary["total_systems_deployed"] += 1
        exec_summary["total_tests_executed"] += stats.get("total_tests", 0)
        exec_summary["total_patterns_tested"] += stats.get("patterns_tested", 0)
        exec_summary["total_pairs_tested"] += stats.get("pairs_tested", 0)
        exec_summary["total_signals_generated"] += stats.get("signals_generated", 0)
        exec_summary["systems"].append({
            "name": "Kraken Pro Continuous Testing",
            "status": "Active",
            "tests": stats.get("total_tests", 0),
            "signals": stats.get("signals_generated", 0)
        })

    # Paper trading
    if report["paper_trading_performance"]:
        metrics = report["paper_trading_performance"]["metrics"]
        exec_summary["total_systems_deployed"] += 1
        exec_summary["total_trades_executed"] += metrics.get("total_trades", 0)
        exec_summary["total_capital_tested"] += metrics.get("initial_capital", 0)
        exec_summary["net_profit_all_systems"] += metrics.get("net_profit", 0)
        exec_summary["systems"].append({
            "name": "Paper Trading Bot",
            "status": "Active",
            "capital": metrics.get("current_capital", 0),
            "roi": f"{metrics.get('roi_percentage', 0)}%",
            "win_rate": f"{metrics.get('win_rate', 0)}%"
        })

    # Backtests
    for profile, data in report["historical_backtests"].items():
        if data:
            exec_summary["total_systems_deployed"] += 1
            exec_summary["total_trades_executed"] += data.get("total_trades", 0)
            exec_summary["total_capital_tested"] += data.get("initial_capital", 0)
            exec_summary["net_profit_all_systems"] += data.get("net_profit", 0)
            exec_summary["systems"].append({
                "name": f"Backtest - {profile.title()} Profile",
                "status": "Completed",
                "trades": data.get("total_trades", 0),
                "roi": f"{data.get('roi_percentage', 0)}%",
                "win_rate": f"{data.get('win_rate', 0)}%"
            })

    report["executive_summary"] = exec_summary

    # 6. Consolidated metrics
    report["consolidated_metrics"] = {
        "pattern_rotation_system": {
            "total_patterns": 24,
            "patterns_tested": report["kraken_continuous_testing"].get("statistics", {}).get("patterns_tested", 0),
            "patterns": [
                "HAMMER", "INVERTED_HAMMER", "BULLISH_ENGULFING", "MORNING_STAR",
                "THREE_WHITE_SOLDIERS", "DRAGONFLY_DOJI", "PIERCING_PATTERN",
                "BULLISH_HARAMI", "RISING_THREE_METHODS", "THREE_INSIDE_UP",
                "BULLISH_MARUBOZU", "BULLISH_SPINNING_TOP", "SHOOTING_STAR",
                "HANGING_MAN", "BEARISH_ENGULFING", "EVENING_STAR",
                "THREE_BLACK_CROWS", "GRAVESTONE_DOJI", "DARK_CLOUD_COVER",
                "BEARISH_HARAMI", "FALLING_THREE_METHODS", "THREE_INSIDE_DOWN",
                "BEARISH_MARUBOZU", "BEARISH_SPINNING_TOP"
            ]
        },
        "pair_rotation_system": {
            "total_pairs": 10,
            "pairs_tested": report["kraken_continuous_testing"].get("statistics", {}).get("pairs_tested", 0),
            "pairs": [
                "XXBTZUSD (Bitcoin)", "XETHZUSD (Ethereum)", "SOLUSD (Solana)",
                "XRPUSD (Ripple)", "ADAUSD (Cardano)", "DOTUSD (Polkadot)",
                "MATICUSD (Polygon)", "LINKUSD (Chainlink)", "AVAXUSD (Avalanche)",
                "ATOMUSD (Cosmos)"
            ]
        },
        "trading_modes": {
            "paper": "Active - $10,000 initial capital",
            "demo": "Configured - Ready to activate",
            "live": "Configured - Requires Kraken API keys",
            "simulation": "Active - Continuous testing"
        }
    }

    # 7. Save master report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = base_dir / 'logs' / 'trading_bot' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / f'MASTER_REPORT_{timestamp}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    # 8. Print summary
    print(f"\n{'='*70}")
    print(f"MASTER TRADING BOT PERFORMANCE REPORT")
    print(f"{'='*70}")
    print(f"Generated: {report['report_timestamp']}")
    print(f"\n{'='*70}")
    print(f"EXECUTIVE SUMMARY")
    print(f"{'='*70}")
    print(f"Total Systems Deployed: {exec_summary['total_systems_deployed']}")
    print(f"Total Tests Executed: {exec_summary['total_tests_executed']}")
    print(f"Total Patterns Tested: {exec_summary['total_patterns_tested']}")
    print(f"Total Pairs Tested: {exec_summary['total_pairs_tested']}")
    print(f"Total Signals Generated: {exec_summary['total_signals_generated']}")
    print(f"Total Trades Executed: {exec_summary['total_trades_executed']}")
    print(f"Total Capital Tested: ${exec_summary['total_capital_tested']:,.2f}")
    print(f"Net Profit (All Systems): ${exec_summary['net_profit_all_systems']:,.2f}")

    print(f"\n{'='*70}")
    print(f"ACTIVE SYSTEMS")
    print(f"{'='*70}")
    for system in exec_summary['systems']:
        print(f"\n{system['name']}")
        print(f"  Status: {system['status']}")
        for key, value in system.items():
            if key not in ['name', 'status']:
                print(f"  {key.title()}: {value}")

    print(f"\n{'='*70}")
    print(f"KRAKEN CONTINUOUS TESTING")
    print(f"{'='*70}")
    if report["kraken_continuous_testing"]:
        stats = report["kraken_continuous_testing"]["statistics"]
        print(f"Total Tests: {stats.get('total_tests', 0)}")
        print(f"Patterns Tested: {stats.get('patterns_tested', 0)} unique patterns")
        print(f"Pairs Tested: {stats.get('pairs_tested', 0)} unique pairs")
        print(f"Signals Generated: {stats.get('signals_generated', 0)}")

        print(f"\nPattern Distribution (Top 5):")
        pattern_dist = report["kraken_continuous_testing"]["pattern_distribution"]
        for i, (pattern, count) in enumerate(sorted(pattern_dist.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            print(f"  {i}. {pattern}: {count} tests")

        print(f"\nPair Distribution (Top 5):")
        pair_dist = report["kraken_continuous_testing"]["pair_distribution"]
        for i, (pair, count) in enumerate(sorted(pair_dist.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            print(f"  {i}. {pair}: {count} tests")

    print(f"\n{'='*70}")
    print(f"Report saved: {report_file}")
    print(f"{'='*70}\n")

    return str(report_file)


if __name__ == '__main__':
    report_file = main()
    print(f"✅ Master report generation complete!")
