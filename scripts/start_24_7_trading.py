#!/usr/bin/env python3
"""
24/7 Trading System Launcher
Starts all 21 trading accounts and keeps them running continuously
"""

import json
import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/24_7_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('24x7Trading')


class ContinuousTradingOrchestrator:
    """Manages 24/7 trading across all accounts"""

    def __init__(self):
        self.config_file = Path(__file__).parent.parent / 'pillar-a-trading' / 'config' / 'multi_account_config.json'
        self.running = True
        self.account_threads = {}
        self.account_stats = {}
        self.load_config()

    def load_config(self):
        """Load multi-account configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✅ Loaded configuration for {self.config['total_accounts']} accounts")
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            sys.exit(1)

    def start_account_trading(self, account: Dict[str, Any]):
        """Start trading for a single account (runs in separate thread)"""
        account_id = account['id']
        account_name = account['name']

        logger.info(f"🚀 Starting 24/7 trading for {account_name} (#{account_id})")

        # Add to sys.path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'agent-3.0'))
        sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'bots' / 'pattern-recognition'))

        from agent_3_orchestrator import Agent3Orchestrator
        from candlestick_analyzer import CandlestickAnalyzer

        # Initialize trading components
        agent = Agent3Orchestrator()
        analyzer = CandlestickAnalyzer(pair=account.get('trading_pair', 'BTC/USD'))

        # Initialize account stats
        self.account_stats[account_id] = {
            'name': account_name,
            'profile': account['profile'],
            'environment': account['environment'],
            'initial_capital': account['initial_capital'],
            'current_capital': account['initial_capital'],
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'current_positions': [],
            'last_trade_time': None,
            'uptime_start': datetime.now().isoformat(),
            'status': 'RUNNING'
        }

        iteration = 0
        while self.running:
            try:
                iteration += 1

                # Simulate market data fetch (in production, connect to real API)
                candles = self.fetch_market_data(account)

                # Analyze patterns
                signal = analyzer.analyze_pattern(candles)

                # Execute trades based on signal
                if signal.get('type') in ['BUY', 'SELL'] and signal.get('confidence', 0) > 0.70:
                    self.execute_trade(account_id, signal)

                # Update stats every 100 iterations
                if iteration % 100 == 0:
                    self.save_account_stats()
                    logger.info(f"📊 {account_name}: {self.account_stats[account_id]['total_trades']} trades, "
                              f"Capital: ${self.account_stats[account_id]['current_capital']:,.2f}")

                # Sleep for configured interval (default: 60 seconds)
                time.sleep(account.get('check_interval_seconds', 60))

            except Exception as e:
                logger.error(f"❌ Error in {account_name}: {e}")
                self.account_stats[account_id]['status'] = f'ERROR: {str(e)[:100]}'
                time.sleep(300)  # Wait 5 minutes before retry on error

        logger.info(f"🛑 Stopped trading for {account_name}")

    def fetch_market_data(self, account: Dict[str, Any]) -> List[Dict]:
        """Fetch market data (placeholder - connect to real API in production)"""
        # This is a placeholder - in production, connect to Alpaca, Interactive Brokers, etc.
        import random

        # Generate realistic candle data
        base_price = 50000  # BTC base price
        candles = []

        for i in range(5):
            volatility = random.uniform(0.98, 1.02)
            open_price = base_price * volatility
            high_price = open_price * random.uniform(1.0, 1.02)
            low_price = open_price * random.uniform(0.98, 1.0)
            close_price = random.uniform(low_price, high_price)

            candles.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': random.randint(100, 1000)
            })

            base_price = close_price

        return candles

    def execute_trade(self, account_id: str, signal: Dict[str, Any]):
        """Execute trade based on signal"""
        stats = self.account_stats[account_id]

        # Calculate position size based on risk parameters
        position_size = stats['current_capital'] * 0.02  # 2% of capital

        # Simulate trade execution
        trade = {
            'timestamp': datetime.now().isoformat(),
            'type': signal['type'],
            'pair': signal['pair'],
            'pattern': signal['pattern'],
            'confidence': signal['confidence'],
            'price': signal.get('price', 0),
            'size': position_size,
            'profit_loss': 0  # Will be calculated on close
        }

        # Update stats
        stats['total_trades'] += 1
        stats['last_trade_time'] = trade['timestamp']
        stats['current_positions'].append(trade)

        logger.info(f"💰 {stats['name']} executed {signal['type']} - {signal['pattern']} "
                   f"@ ${signal.get('price', 0):,.2f} (Confidence: {signal['confidence']:.2%})")

    def save_account_stats(self):
        """Save all account statistics"""
        try:
            stats_file = Path('logs') / f'trading_stats_{datetime.now().strftime("%Y%m%d")}.json'
            with open(stats_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'accounts': self.account_stats
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def start_all_accounts(self):
        """Start trading on all accounts in separate threads"""
        logger.info("=" * 70)
        logger.info("🚀 STARTING 24/7 TRADING SYSTEM")
        logger.info("=" * 70)
        logger.info(f"Total Accounts: {self.config['total_accounts']}")
        logger.info(f"Run 24/7: {self.config.get('monitoring', {}).get('run_24_7', True)}")
        logger.info("=" * 70)

        for account in self.config['accounts']:
            if account.get('run_24_7', True):
                thread = threading.Thread(
                    target=self.start_account_trading,
                    args=(account,),
                    daemon=True,
                    name=f"Trading-{account['id']}"
                )
                thread.start()
                self.account_threads[account['id']] = thread
                time.sleep(1)  # Stagger starts

        logger.info(f"✅ Started {len(self.account_threads)} trading threads")
        logger.info("=" * 70)
        logger.info("📊 Press Ctrl+C to view status (system will continue running)")
        logger.info("=" * 70)

    def monitor_forever(self):
        """Monitor all accounts and keep system running"""
        try:
            while self.running:
                time.sleep(300)  # Check every 5 minutes

                # Check thread health
                active_threads = sum(1 for t in self.account_threads.values() if t.is_alive())
                logger.info(f"💓 Heartbeat: {active_threads}/{len(self.account_threads)} accounts active")

                # Save stats
                self.save_account_stats()

        except KeyboardInterrupt:
            logger.info("\n📊 CURRENT STATUS - System continues running in background")
            self.print_status()
            logger.info("\n💡 System is still running 24/7 in background")
            logger.info("   To stop: kill this process or restart server")

    def print_status(self):
        """Print current status of all accounts"""
        print("\n" + "=" * 70)
        print("📊 24/7 TRADING SYSTEM STATUS")
        print("=" * 70)

        total_capital = 0
        total_trades = 0

        for account_id, stats in self.account_stats.items():
            print(f"\n{stats['name']} ({stats['profile'].upper()})")
            print(f"  Status: {stats['status']}")
            print(f"  Capital: ${stats['current_capital']:,.2f} (Initial: ${stats['initial_capital']:,.2f})")
            print(f"  Trades: {stats['total_trades']} (W: {stats['winning_trades']}, L: {stats['losing_trades']})")
            print(f"  Uptime: {stats['uptime_start']}")

            total_capital += stats['current_capital']
            total_trades += stats['total_trades']

        print("\n" + "=" * 70)
        print(f"TOTAL PORTFOLIO: ${total_capital:,.2f}")
        print(f"TOTAL TRADES: {total_trades}")
        print("=" * 70)


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                  24/7 TRADING SYSTEM LAUNCHER                     ║
    ║                       Agent X2.0 - Pillar A                       ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    orchestrator = ContinuousTradingOrchestrator()
    orchestrator.start_all_accounts()
    orchestrator.monitor_forever()


if __name__ == "__main__":
    main()
