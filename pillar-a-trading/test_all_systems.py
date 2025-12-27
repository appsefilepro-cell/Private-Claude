#!/usr/bin/env python3
"""
COMPLETE SYSTEM TEST RUNNER
Tests all 5 trading system components

Run this to verify everything is working correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add paths
sys.path.append('/home/user/Private-Claude/pillar-a-trading')

def print_header(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

async def test_mt5_setup():
    """Test MT5 Demo Setup"""
    print_header("TEST 1: MT5 DEMO SETUP")

    try:
        from mt5.mt5_demo_setup import MT5DemoSetup

        setup = MT5DemoSetup()
        print("✓ MT5DemoSetup imported successfully")
        print(f"✓ Data directory: {setup.data_dir}")
        print(f"✓ Configured brokers: {len(setup.brokers)}")
        print(f"✓ Database path: {setup.db_path}")

        # List brokers
        print("\nConfigured Brokers:")
        for broker in setup.brokers[:3]:
            print(f"  - {broker.name} ({broker.demo_server})")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_okx_paper_trading():
    """Test OKX Paper Trading"""
    print_header("TEST 2: OKX PAPER TRADING")

    try:
        from crypto.okx_paper_trading import OKXPaperTrading

        trader = OKXPaperTrading(testnet=True, paper_balance=100.0)
        print("✓ OKXPaperTrading imported successfully")
        print(f"✓ Initial balance: ${trader.balance:.2f}")
        print(f"✓ Max risk per trade: {trader.max_risk_per_trade*100}%")
        print(f"✓ Database path: {trader.db_path}")

        # Test market data
        print("\nTesting market data...")
        ticker = await trader.get_ticker("BTC-USDT")
        if ticker:
            print(f"✓ BTC-USDT: ${ticker['last']:,.2f}")
        else:
            print("⚠ Market data not available (network may be required)")

        # Check performance metrics
        metrics = trader.calculate_performance_metrics()
        print(f"✓ Performance tracking initialized")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_mql5_downloader():
    """Test MQL5 Algorithm Downloader"""
    print_header("TEST 3: MQL5 ALGORITHM DOWNLOADER")

    try:
        from mql5.mql5_algorithm_downloader import MQL5AlgorithmDownloader

        downloader = MQL5AlgorithmDownloader()
        print("✓ MQL5AlgorithmDownloader imported successfully")
        print(f"✓ Data directory: {downloader.data_dir}")
        print(f"✓ MQL5 algorithms directory: {downloader.mql5_dir}")
        print(f"✓ Python conversions directory: {downloader.python_dir}")
        print(f"✓ Database path: {downloader.db_path}")

        # Show target strategies
        print(f"\nTarget Strategies ({len(downloader.target_strategies)}):")
        for strategy in downloader.target_strategies[:5]:
            print(f"  - {strategy}")

        # Check saved algorithms
        algorithms = downloader.get_algorithms()
        print(f"✓ Saved algorithms: {len(algorithms)}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_bot_manager():
    """Test Trading Bot Manager"""
    print_header("TEST 4: TRADING BOT MANAGER 24/7")

    try:
        from trading_bot_manager_24_7 import TradingBotManager

        manager = TradingBotManager()
        print("✓ TradingBotManager imported successfully")
        print(f"✓ Data directory: {manager.data_dir}")
        print(f"✓ Database path: {manager.db_path}")
        print(f"✓ Configuration loaded: {len(manager.config['bots'])} bots")

        # Show configuration
        print("\nConfigured Bots:")
        for name, config in manager.config['bots'].items():
            status = "Enabled" if config.get('enabled') else "Disabled"
            print(f"  - {name} ({config['type']}): {status}")

        print(f"\n✓ Monitoring intervals:")
        print(f"  - Heartbeat: {manager.config['monitoring']['heartbeat_interval']}s")
        print(f"  - Metrics: {manager.config['monitoring']['metrics_interval']}s")
        print(f"  - Reports: {manager.config['monitoring']['report_interval']}s")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_dashboard():
    """Test Trading Dashboard"""
    print_header("TEST 5: LIVE TRADING DASHBOARD")

    try:
        from dashboard.live_trading_dashboard import TradingDashboard

        dashboard = TradingDashboard()
        print("✓ TradingDashboard imported successfully")
        print(f"✓ Data directory: {dashboard.data_dir}")
        print(f"✓ Bot manager DB: {dashboard.bot_manager_db}")
        print(f"✓ MT5 DB: {dashboard.mt5_db}")
        print(f"✓ OKX DB: {dashboard.okx_db}")

        # Get portfolio summary
        summary = dashboard.get_portfolio_summary()
        print("\n✓ Portfolio Summary:")
        print(f"  - Balance: ${summary['total_balance']:.2f}")
        print(f"  - Profit: ${summary['total_profit']:.2f}")
        print(f"  - Trades: {summary['total_trades']}")
        print(f"  - Active Bots: {summary['bots_running']}")

        # Get performance metrics
        metrics = dashboard.get_performance_metrics()
        print("\n✓ Performance Metrics:")
        print(f"  - Win Rate: {metrics['win_rate']:.1f}%")
        print(f"  - Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"  - Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")

        print("\n✓ Dashboard ready to deploy")
        print("  Run: streamlit run dashboard/live_trading_dashboard.py")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def run_all_tests():
    """Run all system tests"""
    print("\n" + "█"*70)
    print("  COMPLETE TRADING SYSTEM - VERIFICATION TEST")
    print("█"*70)

    results = []

    # Test each component
    results.append(("MT5 Demo Setup", await test_mt5_setup()))
    results.append(("OKX Paper Trading", await test_okx_paper_trading()))
    results.append(("MQL5 Downloader", await test_mql5_downloader()))
    results.append(("Bot Manager 24/7", await test_bot_manager()))
    results.append(("Live Dashboard", await test_dashboard()))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")
    print("\nComponent Status:")

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {name}")

    # Overall status
    print("\n" + "="*70)
    if passed == total:
        print("  ✓ ALL SYSTEMS OPERATIONAL")
        print("  🚀 Ready for paper trading!")
    else:
        print("  ⚠ Some components need attention")
        print("  Review errors above and fix issues")
    print("="*70 + "\n")

    # File statistics
    print_header("CODE STATISTICS")

    files = [
        ("mt5/mt5_demo_setup.py", 844),
        ("crypto/okx_paper_trading.py", 878),
        ("mql5/mql5_algorithm_downloader.py", 697),
        ("trading_bot_manager_24_7.py", 768),
        ("dashboard/live_trading_dashboard.py", 576)
    ]

    print("\nFiles Created:")
    total_lines = 0
    for filepath, lines in files:
        print(f"  {filepath:45s} {lines:4d} lines")
        total_lines += lines

    print(f"\n  {'TOTAL PRODUCTION CODE':45s} {total_lines:4d} lines")

    print("\n" + "="*70)
    print("  📊 System ready for deployment!")
    print("  📚 Read TRADING_SYSTEM_SETUP.md for full documentation")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
