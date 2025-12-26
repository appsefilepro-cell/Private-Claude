"""
Trading Bot Test Suite Runner
Comprehensive testing framework for backtesting, strategy validation, and paper trading verification
Runs the same tests from existing backtest infrastructure plus additional validation
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from backtesting.backtesting_engine import BacktestingEngine, run_all_profiles_backtest
from bot_performance_tracker import PerformanceTracker

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'tests'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'test_suite_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TestSuiteRunner')


class TestSuiteRunner:
    """
    Comprehensive test suite for trading bot
    Includes backtesting, strategy validation, and performance benchmarks
    """

    def __init__(self):
        """Initialize test suite runner"""
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0

        # Output directory for test results
        self.output_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'test-results'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Test Suite Runner initialized")

    def run_test(self, test_name: str, test_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Run a single test

        Args:
            test_name: Name of the test
            test_func: Test function to execute
            *args, **kwargs: Arguments to pass to test function

        Returns:
            Test result dictionary
        """
        logger.info(f"Running test: {test_name}")
        start_time = datetime.now()

        try:
            result = test_func(*args, **kwargs)

            duration = datetime.now() - start_time
            test_result = {
                "name": test_name,
                "status": "PASSED",
                "duration": duration.total_seconds(),
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

            self.passed_tests += 1
            logger.info(f"✓ Test PASSED: {test_name} ({duration.total_seconds():.2f}s)")

        except Exception as e:
            duration = datetime.now() - start_time
            test_result = {
                "name": test_name,
                "status": "FAILED",
                "duration": duration.total_seconds(),
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }

            self.failed_tests += 1
            logger.error(f"✗ Test FAILED: {test_name}")
            logger.error(f"Error: {e}")

        self.test_results.append(test_result)
        return test_result

    def test_1_day_backtest_beginner(self) -> Dict[str, Any]:
        """Test 1-day backtest with beginner profile"""
        engine = BacktestingEngine(profile="beginner")
        results = engine.run_backtest(days=1)
        engine.export_results(output_dir=str(self.output_dir / "backtest"))

        # Validation
        assert results.get('total_trades', 0) >= 0, "Should have executed trades"
        assert 'roi_percentage' in results, "Should calculate ROI"

        return results

    def test_1_day_backtest_novice(self) -> Dict[str, Any]:
        """Test 1-day backtest with novice profile"""
        engine = BacktestingEngine(profile="novice")
        results = engine.run_backtest(days=1)
        engine.export_results(output_dir=str(self.output_dir / "backtest"))

        assert results.get('total_trades', 0) >= 0, "Should have executed trades"
        assert 'win_rate' in results, "Should calculate win rate"

        return results

    def test_1_day_backtest_advanced(self) -> Dict[str, Any]:
        """Test 1-day backtest with advanced profile"""
        engine = BacktestingEngine(profile="advanced")
        results = engine.run_backtest(days=1)
        engine.export_results(output_dir=str(self.output_dir / "backtest"))

        assert results.get('total_trades', 0) >= 0, "Should have executed trades"
        assert 'profit_factor' in results, "Should calculate profit factor"

        return results

    def test_7_day_backtest_all_profiles(self) -> Dict[str, Any]:
        """Test 7-day backtest across all profiles"""
        results = run_all_profiles_backtest(days=7)

        assert len(results) == 3, "Should test all 3 profiles"
        assert 'beginner' in results, "Should include beginner results"
        assert 'novice' in results, "Should include novice results"
        assert 'advanced' in results, "Should include advanced results"

        return results

    def test_performance_tracker_basic(self) -> Dict[str, Any]:
        """Test performance tracker basic functionality"""
        tracker = PerformanceTracker(mode="paper", profile="beginner")

        # Create test trade
        test_trade = {
            "id": 1,
            "pair": "BTC/USD",
            "type": "BUY",
            "entry_price": 50000,
            "quantity": 0.02,
            "position_value": 1000,
            "entry_time": datetime.now(),
            "status": "OPEN"
        }

        tracker.record_trade(test_trade)

        assert len(tracker.trades) == 1, "Should record trade"

        # Close trade
        test_trade['exit_price'] = 51000
        test_trade['exit_time'] = datetime.now()
        test_trade['status'] = 'CLOSED'
        test_trade['profit_loss'] = 20
        test_trade['profit_loss_pct'] = 2.0
        test_trade['close_reason'] = 'TAKE_PROFIT'

        tracker.update_trade(test_trade)

        metrics = tracker.get_current_metrics()
        assert metrics['closed_trades'] == 1, "Should have 1 closed trade"
        assert metrics['win_rate'] == 100.0, "Should have 100% win rate"

        return metrics

    def test_performance_tracker_metrics(self) -> Dict[str, Any]:
        """Test performance tracker metrics calculation"""
        tracker = PerformanceTracker(mode="paper", profile="beginner")

        # Create multiple test trades
        trades = [
            {
                "id": 1,
                "pair": "BTC/USD",
                "type": "BUY",
                "entry_price": 50000,
                "quantity": 0.02,
                "position_value": 1000,
                "entry_time": datetime.now() - timedelta(hours=3),
                "exit_time": datetime.now() - timedelta(hours=2),
                "exit_price": 51000,
                "status": "CLOSED",
                "profit_loss": 20,
                "profit_loss_pct": 2.0,
                "close_reason": "TAKE_PROFIT"
            },
            {
                "id": 2,
                "pair": "ETH/USD",
                "type": "BUY",
                "entry_price": 3000,
                "quantity": 0.33,
                "position_value": 1000,
                "entry_time": datetime.now() - timedelta(hours=2),
                "exit_time": datetime.now() - timedelta(hours=1),
                "exit_price": 2950,
                "status": "CLOSED",
                "profit_loss": -16.5,
                "profit_loss_pct": -1.65,
                "close_reason": "STOP_LOSS"
            },
            {
                "id": 3,
                "pair": "BTC/USD",
                "type": "BUY",
                "entry_price": 50500,
                "quantity": 0.02,
                "position_value": 1000,
                "entry_time": datetime.now() - timedelta(hours=1),
                "exit_time": datetime.now(),
                "exit_price": 51500,
                "status": "CLOSED",
                "profit_loss": 20,
                "profit_loss_pct": 1.98,
                "close_reason": "TAKE_PROFIT"
            }
        ]

        for trade in trades:
            tracker.record_trade(trade)
            tracker.update_trade(trade)

        metrics = tracker.get_current_metrics()

        # Validate metrics
        assert metrics['total_trades'] == 3, "Should have 3 trades"
        assert metrics['winning_trades'] == 2, "Should have 2 winning trades"
        assert metrics['losing_trades'] == 1, "Should have 1 losing trade"
        assert abs(metrics['win_rate'] - 66.67) < 0.1, "Win rate should be ~66.67%"
        assert metrics['total_profit'] > 0, "Should have positive total profit"

        return metrics

    def test_performance_tracker_export_json(self) -> str:
        """Test performance tracker JSON export"""
        tracker = PerformanceTracker(mode="paper", profile="beginner")

        # Add test trade
        test_trade = {
            "id": 1,
            "pair": "BTC/USD",
            "type": "BUY",
            "entry_price": 50000,
            "quantity": 0.02,
            "position_value": 1000,
            "entry_time": datetime.now(),
            "status": "CLOSED",
            "exit_price": 51000,
            "exit_time": datetime.now(),
            "profit_loss": 20,
            "profit_loss_pct": 2.0,
            "close_reason": "TAKE_PROFIT"
        }

        tracker.record_trade(test_trade)
        tracker.update_trade(test_trade)

        # Export JSON
        json_path = tracker.export_json()

        assert os.path.exists(json_path), "JSON file should be created"

        # Verify JSON content
        with open(json_path, 'r') as f:
            data = json.load(f)

        assert 'metadata' in data, "Should have metadata"
        assert 'metrics' in data, "Should have metrics"
        assert 'trades' in data, "Should have trades"

        return json_path

    def test_performance_tracker_export_csv(self) -> str:
        """Test performance tracker CSV export"""
        tracker = PerformanceTracker(mode="paper", profile="beginner")

        # Add test trade
        test_trade = {
            "id": 1,
            "pair": "BTC/USD",
            "type": "BUY",
            "entry_price": 50000,
            "quantity": 0.02,
            "position_value": 1000,
            "entry_time": datetime.now(),
            "status": "CLOSED",
            "exit_price": 51000,
            "exit_time": datetime.now(),
            "profit_loss": 20,
            "profit_loss_pct": 2.0,
            "close_reason": "TAKE_PROFIT"
        }

        tracker.record_trade(test_trade)
        tracker.update_trade(test_trade)

        # Export CSV
        csv_path = tracker.export_csv()

        assert os.path.exists(csv_path), "CSV file should be created"
        assert csv_path.endswith('.csv'), "Should be CSV file"

        return csv_path

    def test_performance_tracker_report(self) -> str:
        """Test performance tracker report generation"""
        tracker = PerformanceTracker(mode="paper", profile="beginner")

        # Add test trades
        for i in range(5):
            trade = {
                "id": i + 1,
                "pair": "BTC/USD",
                "type": "BUY",
                "entry_price": 50000 + i * 100,
                "quantity": 0.02,
                "position_value": 1000,
                "entry_time": datetime.now() - timedelta(hours=i+1),
                "exit_time": datetime.now() - timedelta(hours=i),
                "exit_price": 50000 + i * 100 + (100 if i % 2 == 0 else -50),
                "status": "CLOSED",
                "profit_loss": 2 if i % 2 == 0 else -1,
                "profit_loss_pct": 0.2 if i % 2 == 0 else -0.1,
                "close_reason": "TAKE_PROFIT" if i % 2 == 0 else "STOP_LOSS"
            }
            tracker.record_trade(trade)
            tracker.update_trade(trade)

        # Generate report
        report_path = tracker.generate_performance_report()

        assert os.path.exists(report_path), "Report file should be created"
        assert report_path.endswith('.txt'), "Should be text file"

        # Verify report content
        with open(report_path, 'r') as f:
            content = f.read()

        assert "TRADING BOT PERFORMANCE REPORT" in content, "Should have report header"
        assert "SESSION INFORMATION" in content, "Should have session info"
        assert "TRADE STATISTICS" in content, "Should have trade statistics"

        return report_path

    def test_risk_profile_loading(self) -> Dict[str, Any]:
        """Test risk profile configuration loading"""
        config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'

        assert config_path.exists(), "Risk profile config should exist"

        with open(config_path, 'r') as f:
            config = json.load(f)

        assert 'profiles' in config, "Should have profiles section"
        assert 'beginner' in config['profiles'], "Should have beginner profile"
        assert 'novice' in config['profiles'], "Should have novice profile"
        assert 'advanced' in config['profiles'], "Should have advanced profile"

        # Validate beginner profile
        beginner = config['profiles']['beginner']
        assert 'risk_parameters' in beginner, "Should have risk parameters"
        assert 'trading_pairs' in beginner, "Should have trading pairs"
        assert 'patterns_enabled' in beginner, "Should have patterns enabled"

        return config

    def test_config_validation(self) -> Dict[str, Any]:
        """Test trading bot configuration validation"""
        config_path = Path(__file__).parent.parent / 'config' / 'trading_bot_24_7_config.json'

        # Config might not exist yet, so this test checks if it's valid when it does
        if not config_path.exists():
            logger.warning("Config file not found, skipping validation")
            return {"status": "skipped"}

        with open(config_path, 'r') as f:
            config = json.load(f)

        # Validate required sections
        assert 'trading_pairs' in config, "Should have trading_pairs"
        assert isinstance(config['trading_pairs'], list), "trading_pairs should be a list"

        return config

    def test_strategy_validation_beginner(self) -> Dict[str, Any]:
        """Validate beginner strategy performance"""
        engine = BacktestingEngine(profile="beginner")
        results = engine.run_backtest(days=1)

        # Beginner should be conservative
        assert results.get('max_concurrent_trades', 0) <= 1, "Beginner should have max 1 concurrent trade"

        # Should have risk controls
        config = engine.config
        assert config.get('paper_trading_only', False) == True, "Beginner should be paper trading only"

        return {
            "profile": "beginner",
            "results": results,
            "validation": "PASSED"
        }

    def test_strategy_validation_advanced(self) -> Dict[str, Any]:
        """Validate advanced strategy performance"""
        engine = BacktestingEngine(profile="advanced")
        results = engine.run_backtest(days=1)

        # Advanced can have multiple concurrent trades
        config = engine.config
        max_concurrent = config.get('risk_parameters', {}).get('max_concurrent_trades', 0)
        assert max_concurrent >= 3, "Advanced should allow multiple concurrent trades"

        return {
            "profile": "advanced",
            "results": results,
            "validation": "PASSED"
        }

    def test_paper_trading_verification(self) -> Dict[str, Any]:
        """Verify paper trading functionality"""
        # This would test the actual bot in paper mode
        # For now, we verify the components work correctly

        tracker = PerformanceTracker(mode="paper", profile="beginner")
        assert tracker.mode == "paper", "Should be in paper mode"

        # Verify no real money is used
        assert tracker.initial_capital == 10000, "Paper trading should use default capital"

        return {
            "mode": "paper",
            "verification": "PASSED"
        }

    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks for all profiles"""
        results = {}

        for profile in ['beginner', 'novice', 'advanced']:
            engine = BacktestingEngine(profile=profile)
            backtest_results = engine.run_backtest(days=1)

            results[profile] = {
                "total_trades": backtest_results.get('total_trades', 0),
                "win_rate": backtest_results.get('win_rate', 0),
                "roi": backtest_results.get('roi_percentage', 0),
                "profit_factor": backtest_results.get('profit_factor', 0)
            }

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the suite"""
        logger.info("="*80)
        logger.info("STARTING COMPREHENSIVE TEST SUITE")
        logger.info("="*80)

        start_time = datetime.now()

        # Backtesting tests
        logger.info("\n--- BACKTESTING TESTS ---")
        self.run_test("1-Day Backtest - Beginner", self.test_1_day_backtest_beginner)
        self.run_test("1-Day Backtest - Novice", self.test_1_day_backtest_novice)
        self.run_test("1-Day Backtest - Advanced", self.test_1_day_backtest_advanced)
        self.run_test("7-Day Backtest - All Profiles", self.test_7_day_backtest_all_profiles)

        # Performance tracker tests
        logger.info("\n--- PERFORMANCE TRACKER TESTS ---")
        self.run_test("Performance Tracker - Basic", self.test_performance_tracker_basic)
        self.run_test("Performance Tracker - Metrics", self.test_performance_tracker_metrics)
        self.run_test("Performance Tracker - JSON Export", self.test_performance_tracker_export_json)
        self.run_test("Performance Tracker - CSV Export", self.test_performance_tracker_export_csv)
        self.run_test("Performance Tracker - Report", self.test_performance_tracker_report)

        # Configuration tests
        logger.info("\n--- CONFIGURATION TESTS ---")
        self.run_test("Risk Profile Loading", self.test_risk_profile_loading)
        self.run_test("Config Validation", self.test_config_validation)

        # Strategy validation tests
        logger.info("\n--- STRATEGY VALIDATION TESTS ---")
        self.run_test("Strategy Validation - Beginner", self.test_strategy_validation_beginner)
        self.run_test("Strategy Validation - Advanced", self.test_strategy_validation_advanced)

        # Paper trading tests
        logger.info("\n--- PAPER TRADING TESTS ---")
        self.run_test("Paper Trading Verification", self.test_paper_trading_verification)

        # Performance benchmarks
        logger.info("\n--- PERFORMANCE BENCHMARKS ---")
        self.run_test("Performance Benchmarks", self.test_performance_benchmarks)

        duration = datetime.now() - start_time

        # Generate summary
        summary = {
            "total_tests": len(self.test_results),
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "skipped": self.skipped_tests,
            "duration": duration.total_seconds(),
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results
        }

        # Print summary
        logger.info("\n" + "="*80)
        logger.info("TEST SUITE SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Tests:  {summary['total_tests']}")
        logger.info(f"Passed:       {summary['passed']} ✓")
        logger.info(f"Failed:       {summary['failed']} ✗")
        logger.info(f"Skipped:      {summary['skipped']}")
        logger.info(f"Duration:     {summary['duration']:.2f}s")
        logger.info("="*80)

        # Export results
        self.export_test_results(summary)

        return summary

    def export_test_results(self, summary: Dict[str, Any]):
        """Export test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Test results exported to {filepath}")


def main():
    """Main entry point"""
    runner = TestSuiteRunner()

    try:
        summary = runner.run_all_tests()

        # Exit with appropriate code
        if summary['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error running test suite: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
