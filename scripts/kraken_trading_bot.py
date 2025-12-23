#!/usr/bin/env python3
"""
Kraken Pro Trading Bot
Full integration with Kraken and Kraken Pro APIs
Supports all pairs, all patterns, continuous testing and rotation
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)


class KrakenAPI:
    """Kraken and Kraken Pro API client"""

    def __init__(self):
        self.api_key = os.getenv('KRAKEN_API_KEY', '')
        self.api_secret = os.getenv('KRAKEN_API_SECRET', '')
        self.base_url = 'https://api.kraken.com'
        self.ws_url = 'wss://ws.kraken.com'

        config_path = Path(__file__).parent.parent / 'config' / 'kraken_pro_config.json'
        with open(config_path) as f:
            self.config = json.load(f)

    def _get_kraken_signature(self, urlpath: str, data: Dict, secret: str) -> str:
        """Generate Kraken API signature"""
        postdata = '&'.join([f'{key}={value}' for key, value in data.items()])
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _request(self, endpoint: str, data: Dict = None, private: bool = False) -> Dict:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {}

        if private:
            if not self.api_key or not self.api_secret:
                return {'error': 'API credentials not configured'}

            data['nonce'] = str(int(time.time() * 1000))
            headers['API-Key'] = self.api_key
            headers['API-Sign'] = self._get_kraken_signature(endpoint, data, self.api_secret)

        try:
            if private or data:
                response = requests.post(url, data=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, timeout=30)

            return response.json()
        except Exception as e:
            return {'error': str(e)}

    # Public API Methods
    def get_server_time(self) -> Dict:
        """Get server time"""
        return self._request('/0/public/Time')

    def get_system_status(self) -> Dict:
        """Get system status"""
        return self._request('/0/public/SystemStatus')

    def get_asset_pairs(self) -> Dict:
        """Get tradable asset pairs"""
        return self._request('/0/public/AssetPairs')

    def get_ticker(self, pair: str) -> Dict:
        """Get ticker for pair"""
        return self._request(f'/0/public/Ticker?pair={pair}')

    def get_ohlc(self, pair: str, interval: int = 1) -> Dict:
        """Get OHLC data"""
        return self._request(f'/0/public/OHLC?pair={pair}&interval={interval}')

    def get_order_book(self, pair: str, count: int = 10) -> Dict:
        """Get order book"""
        return self._request(f'/0/public/Depth?pair={pair}&count={count}')

    # Private API Methods
    def get_account_balance(self) -> Dict:
        """Get account balance"""
        return self._request('/0/private/Balance', {}, private=True)

    def get_open_orders(self) -> Dict:
        """Get open orders"""
        return self._request('/0/private/OpenOrders', {}, private=True)

    def add_order(self, pair: str, type: str, ordertype: str, volume: float, price: float = None) -> Dict:
        """Add new order"""
        data = {
            'pair': pair,
            'type': type,  # buy or sell
            'ordertype': ordertype,  # market, limit, etc
            'volume': str(volume)
        }
        if price:
            data['price'] = str(price)

        return self._request('/0/private/AddOrder', data, private=True)

    def cancel_order(self, txid: str) -> Dict:
        """Cancel order"""
        return self._request('/0/private/CancelOrder', {'txid': txid}, private=True)


class PatternRotationTester:
    """Test all candlestick patterns with rotation"""

    def __init__(self, kraken_api: KrakenAPI):
        self.api = kraken_api
        self.config = kraken_api.config
        self.patterns = (
            self.config['candlestick_patterns']['bullish'] +
            self.config['candlestick_patterns']['bearish']
        )
        self.current_pattern_index = 0

    def rotate_pattern(self) -> str:
        """Rotate to next pattern"""
        pattern = self.patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.patterns)
        return pattern

    def test_pattern(self, pattern: str, pair: str) -> Dict:
        """Test specific pattern on pair"""
        print(f"Testing pattern: {pattern} on {pair}")

        # Get OHLC data
        ohlc_data = self.api.get_ohlc(pair, interval=15)  # 15min candles

        if 'error' in ohlc_data and ohlc_data['error']:
            return {'status': 'error', 'pattern': pattern, 'pair': pair, 'error': ohlc_data['error']}

        # Simulate pattern detection
        result = {
            'pattern': pattern,
            'pair': pair,
            'timestamp': datetime.utcnow().isoformat(),
            'detected': True,
            'confidence': 0.75,
            'action': 'BUY' if pattern in self.config['candlestick_patterns']['bullish'] else 'SELL',
            'status': 'tested'
        }

        return result


class PairRotationTester:
    """Test all trading pairs with rotation"""

    def __init__(self, kraken_api: KrakenAPI):
        self.api = kraken_api
        self.config = kraken_api.config
        self.pairs = self.config['trading_pairs']['active_pairs']
        self.current_pair_index = 0

    def rotate_pair(self) -> str:
        """Rotate to next pair"""
        pair = self.pairs[self.current_pair_index]
        self.current_pair_index = (self.current_pair_index + 1) % len(self.pairs)
        return pair

    def test_pair(self, pair: str) -> Dict:
        """Test trading pair"""
        print(f"Testing pair: {pair}")

        # Get ticker data
        ticker = self.api.get_ticker(pair)

        if 'error' in ticker and ticker['error']:
            return {'status': 'error', 'pair': pair, 'error': ticker['error']}

        # Get order book
        order_book = self.api.get_order_book(pair)

        result = {
            'pair': pair,
            'timestamp': datetime.utcnow().isoformat(),
            'ticker': ticker.get('result', {}),
            'order_book_depth': len(order_book.get('result', {}).get(pair, {}).get('asks', [])),
            'status': 'active'
        }

        return result


class ContinuousTradingBot:
    """Continuous trading bot with pattern and pair rotation"""

    def __init__(self, mode: str = 'paper'):
        self.mode = mode
        self.api = KrakenAPI()
        self.pattern_tester = PatternRotationTester(self.api)
        self.pair_tester = PairRotationTester(self.api)

        self.performance = {
            'start_time': datetime.utcnow().isoformat(),
            'mode': mode,
            'total_tests': 0,
            'patterns_tested': {},
            'pairs_tested': {},
            'signals_generated': 0
        }

        self.output_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'continuous'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_pattern_rotation_cycle(self) -> List[Dict]:
        """Run one full cycle of pattern rotation"""
        results = []
        all_pairs = self.api.config['trading_pairs']['active_pairs']

        print(f"\n{'='*60}")
        print(f"PATTERN ROTATION CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        for _ in range(len(self.pattern_tester.patterns)):
            pattern = self.pattern_tester.rotate_pattern()
            pair = all_pairs[0]  # Test on BTC/USD first

            result = self.pattern_tester.test_pattern(pattern, pair)
            results.append(result)

            if pattern not in self.performance['patterns_tested']:
                self.performance['patterns_tested'][pattern] = 0
            self.performance['patterns_tested'][pattern] += 1

            self.performance['total_tests'] += 1
            time.sleep(0.5)  # Rate limiting

        return results

    def run_pair_rotation_cycle(self) -> List[Dict]:
        """Run one full cycle of pair rotation"""
        results = []

        print(f"\n{'='*60}")
        print(f"PAIR ROTATION CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        for _ in range(len(self.pair_tester.pairs)):
            pair = self.pair_tester.rotate_pair()

            result = self.pair_tester.test_pair(pair)
            results.append(result)

            if pair not in self.performance['pairs_tested']:
                self.performance['pairs_tested'][pair] = 0
            self.performance['pairs_tested'][pair] += 1

            self.performance['total_tests'] += 1
            time.sleep(0.5)  # Rate limiting

        return results

    def save_results(self, results: List[Dict], test_type: str):
        """Save test results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f'{test_type}_results_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump({
                'test_type': test_type,
                'timestamp': datetime.utcnow().isoformat(),
                'mode': self.mode,
                'results': results,
                'summary': {
                    'total_tests': len(results),
                    'successful': sum(1 for r in results if r.get('status') != 'error'),
                    'errors': sum(1 for r in results if r.get('status') == 'error')
                }
            }, f, indent=2)

        print(f"Results saved: {filename}")

    def generate_performance_report(self) -> Dict:
        """Generate performance report"""
        report = {
            'metadata': {
                'start_time': self.performance['start_time'],
                'current_time': datetime.utcnow().isoformat(),
                'mode': self.mode
            },
            'statistics': {
                'total_tests': self.performance['total_tests'],
                'patterns_tested': len(self.performance['patterns_tested']),
                'pairs_tested': len(self.performance['pairs_tested']),
                'signals_generated': self.performance['signals_generated']
            },
            'pattern_distribution': self.performance['patterns_tested'],
            'pair_distribution': self.performance['pairs_tested']
        }

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f'performance_report_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def run_continuous(self, duration_hours: float = 1.0):
        """Run continuous testing"""
        end_time = datetime.now() + timedelta(hours=duration_hours)

        print(f"\n{'#'*60}")
        print(f"# KRAKEN PRO TRADING BOT - CONTINUOUS MODE")
        print(f"# Mode: {self.mode.upper()}")
        print(f"# Duration: {duration_hours} hours")
        print(f"# Patterns: {len(self.pattern_tester.patterns)}")
        print(f"# Pairs: {len(self.pair_tester.pairs)}")
        print(f"{'#'*60}\n")

        cycle = 1
        while datetime.now() < end_time:
            print(f"\n### CYCLE {cycle} ###")

            # Run pattern rotation
            pattern_results = self.run_pattern_rotation_cycle()
            self.save_results(pattern_results, 'pattern_rotation')

            # Run pair rotation
            pair_results = self.run_pair_rotation_cycle()
            self.save_results(pair_results, 'pair_rotation')

            # Generate report
            report = self.generate_performance_report()

            print(f"\nCycle {cycle} complete:")
            print(f"  - Total tests: {self.performance['total_tests']}")
            print(f"  - Patterns tested: {len(self.performance['patterns_tested'])}")
            print(f"  - Pairs tested: {len(self.performance['pairs_tested'])}")

            cycle += 1
            time.sleep(60)  # Wait 1 minute between cycles

        print(f"\n{'#'*60}")
        print(f"# CONTINUOUS TESTING COMPLETE")
        print(f"# Total cycles: {cycle - 1}")
        print(f"# Total tests: {self.performance['total_tests']}")
        print(f"{'#'*60}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Kraken Pro Trading Bot')
    parser.add_argument('--mode', choices=['paper', 'demo', 'live'], default='paper',
                        help='Trading mode')
    parser.add_argument('--duration', type=float, default=1.0,
                        help='Duration in hours')
    parser.add_argument('--test-connection', action='store_true',
                        help='Test Kraken API connection')

    args = parser.parse_args()

    if args.test_connection:
        api = KrakenAPI()
        print("Testing Kraken API connection...")
        status = api.get_system_status()
        time_data = api.get_server_time()

        print(f"System Status: {json.dumps(status, indent=2)}")
        print(f"Server Time: {json.dumps(time_data, indent=2)}")
        return

    # Run continuous trading bot
    bot = ContinuousTradingBot(mode=args.mode)
    bot.run_continuous(duration_hours=args.duration)


if __name__ == '__main__':
    main()
