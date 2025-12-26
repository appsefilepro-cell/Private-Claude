#!/usr/bin/env python3
"""
Gather All Trading Bot Data
Consolidates all trading bot performance, backtest, and test results
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class TradingDataCollector:
    """Collect and consolidate all trading bot data"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.output_dir = self.base_dir / 'logs' / 'trading_bot' / 'consolidated'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.all_data = {
            'collection_timestamp': datetime.utcnow().isoformat(),
            'performance_data': [],
            'backtest_data': [],
            'test_results': [],
            'summary': {}
        }

    def gather_performance_data(self):
        """Gather all performance data"""
        pattern = str(self.base_dir / 'logs' / 'trading_bot' / 'performance' / '*.json')
        files = glob.glob(pattern)

        print(f"Found {len(files)} performance files")

        for file_path in sorted(files):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self.all_data['performance_data'].append({
                        'file': os.path.basename(file_path),
                        'data': data
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    def gather_backtest_data(self):
        """Gather all backtest data"""
        # From logs/trading_bot/test-results/backtest/
        pattern1 = str(self.base_dir / 'logs' / 'trading_bot' / 'test-results' / 'backtest' / '*.json')
        # From pillar-a-trading/backtest-results/
        pattern2 = str(self.base_dir / 'pillar-a-trading' / 'backtest-results' / '*.json')

        files = glob.glob(pattern1) + glob.glob(pattern2)
        print(f"Found {len(files)} backtest files")

        for file_path in sorted(files):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self.all_data['backtest_data'].append({
                        'file': os.path.basename(file_path),
                        'source': 'logs' if 'logs/' in file_path else 'pillar-a',
                        'data': data
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    def gather_test_results(self):
        """Gather all test results"""
        pattern = str(self.base_dir / 'logs' / 'trading_bot' / 'test-results' / 'test_results_*.json')
        files = glob.glob(pattern)

        print(f"Found {len(files)} test result files")

        for file_path in sorted(files):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self.all_data['test_results'].append({
                        'file': os.path.basename(file_path),
                        'data': data
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    def calculate_summary(self):
        """Calculate overall summary statistics"""
        summary = {
            'total_performance_files': len(self.all_data['performance_data']),
            'total_backtest_files': len(self.all_data['backtest_data']),
            'total_test_result_files': len(self.all_data['test_results']),
            'total_trades_across_all_tests': 0,
            'total_profit_loss': 0,
            'profiles_tested': set(),
            'trading_pairs_tested': set()
        }

        # Aggregate performance data
        for perf in self.all_data['performance_data']:
            data = perf.get('data', {})
            metrics = data.get('metrics', {})

            if 'total_trades' in metrics:
                summary['total_trades_across_all_tests'] += metrics.get('total_trades', 0)
            if 'net_profit' in metrics:
                summary['total_profit_loss'] += metrics.get('net_profit', 0)
            if 'profile' in metrics:
                summary['profiles_tested'].add(metrics['profile'])

        # Aggregate backtest data
        for backtest in self.all_data['backtest_data']:
            filename = backtest['file']
            if 'beginner' in filename:
                summary['profiles_tested'].add('beginner')
            elif 'novice' in filename:
                summary['profiles_tested'].add('novice')
            elif 'advanced' in filename:
                summary['profiles_tested'].add('advanced')

        # Convert sets to lists for JSON serialization
        summary['profiles_tested'] = sorted(list(summary['profiles_tested']))
        summary['trading_pairs_tested'] = ['BTC/USD', 'ETH/USD', 'SOL/USD']  # From config

        self.all_data['summary'] = summary

    def generate_latest_snapshot(self):
        """Generate snapshot of latest data"""
        latest = {
            'timestamp': datetime.utcnow().isoformat(),
            'latest_performance': None,
            'latest_test_results': None,
            'latest_backtest_metrics': {
                'beginner': None,
                'novice': None,
                'advanced': None
            }
        }

        # Get latest performance
        if self.all_data['performance_data']:
            latest['latest_performance'] = self.all_data['performance_data'][-1]['data']

        # Get latest test results
        if self.all_data['test_results']:
            latest['latest_test_results'] = self.all_data['test_results'][-1]['data']

        # Get latest backtest metrics for each profile
        for backtest in reversed(self.all_data['backtest_data']):
            filename = backtest['file']
            if 'metrics' in filename:
                if 'beginner' in filename and not latest['latest_backtest_metrics']['beginner']:
                    latest['latest_backtest_metrics']['beginner'] = backtest['data']
                elif 'novice' in filename and not latest['latest_backtest_metrics']['novice']:
                    latest['latest_backtest_metrics']['novice'] = backtest['data']
                elif 'advanced' in filename and not latest['latest_backtest_metrics']['advanced']:
                    latest['latest_backtest_metrics']['advanced'] = backtest['data']

        return latest

    def save_consolidated_data(self):
        """Save all consolidated data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save complete data dump
        complete_file = self.output_dir / f'complete_bot_data_{timestamp}.json'
        with open(complete_file, 'w') as f:
            json.dump(self.all_data, f, indent=2)
        print(f"\n✅ Complete data saved: {complete_file}")

        # Save latest snapshot
        latest = self.generate_latest_snapshot()
        latest_file = self.output_dir / f'latest_snapshot_{timestamp}.json'
        with open(latest_file, 'w') as f:
            json.dump(latest, f, indent=2)
        print(f"✅ Latest snapshot saved: {latest_file}")

        # Save summary only
        summary_file = self.output_dir / f'summary_{timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': self.all_data['collection_timestamp'],
                'summary': self.all_data['summary']
            }, f, indent=2)
        print(f"✅ Summary saved: {summary_file}")

        return complete_file, latest_file, summary_file

    def print_summary(self):
        """Print summary to console"""
        summary = self.all_data['summary']

        print(f"\n{'='*60}")
        print(f"TRADING BOT DATA COLLECTION SUMMARY")
        print(f"{'='*60}")
        print(f"Collection Time: {self.all_data['collection_timestamp']}")
        print(f"\nFiles Found:")
        print(f"  - Performance files: {summary['total_performance_files']}")
        print(f"  - Backtest files: {summary['total_backtest_files']}")
        print(f"  - Test result files: {summary['total_test_result_files']}")
        print(f"\nAggregated Statistics:")
        print(f"  - Total trades: {summary['total_trades_across_all_tests']}")
        print(f"  - Total P/L: ${summary['total_profit_loss']:.2f}")
        print(f"  - Profiles tested: {', '.join(summary['profiles_tested'])}")
        print(f"  - Trading pairs: {', '.join(summary['trading_pairs_tested'])}")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    print("Gathering all trading bot data...")

    collector = TradingDataCollector()

    # Gather all data
    collector.gather_performance_data()
    collector.gather_backtest_data()
    collector.gather_test_results()

    # Calculate summary
    collector.calculate_summary()

    # Save everything
    complete_file, latest_file, summary_file = collector.save_consolidated_data()

    # Print summary
    collector.print_summary()

    return {
        'complete_data_file': str(complete_file),
        'latest_snapshot_file': str(latest_file),
        'summary_file': str(summary_file),
        'summary': collector.all_data['summary']
    }


if __name__ == '__main__':
    result = main()
    print(f"Data collection complete!")
    print(f"Files saved to: logs/trading_bot/consolidated/")
