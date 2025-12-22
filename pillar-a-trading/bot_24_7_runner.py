"""
24/7 Trading Bot Runner
Continuous execution system with paper, demo, and live trading modes
Includes automatic restart, performance monitoring, and market hours detection
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import signal

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from backtesting.backtesting_engine import BacktestingEngine
from bot_performance_tracker import PerformanceTracker

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'bot_runner_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Bot24x7Runner')


class TradingMode(Enum):
    """Trading mode enumeration"""
    PAPER = "paper"          # Simulated trading with fake money
    DEMO = "demo"            # Demo account with virtual funds ($10k)
    LIVE = "live"            # Real trading with real money


class MarketStatus(Enum):
    """Market status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    POST_MARKET = "post_market"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"


class TradingBot24x7:
    """
    24/7 Trading Bot with multiple operation modes
    Supports paper trading, demo mode, and live trading
    """

    def __init__(self,
                 mode: TradingMode = TradingMode.PAPER,
                 profile: str = "beginner",
                 config_path: Optional[str] = None):
        """
        Initialize 24/7 trading bot

        Args:
            mode: Trading mode (paper/demo/live)
            profile: Risk profile (beginner/novice/advanced)
            config_path: Path to configuration file
        """
        self.mode = mode
        self.profile = profile
        self.running = False
        self.start_time = None
        self.restart_count = 0
        self.max_restarts = 10

        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'trading_bot_24_7_config.json'

        self.config = self.load_config(config_path)

        # Initialize components
        self.performance_tracker = PerformanceTracker(mode=mode.value, profile=profile)
        self.backtesting_engine = BacktestingEngine(profile=profile)

        # Trading state
        self.current_capital = self.get_initial_capital()
        self.open_positions = []
        self.daily_trade_count = 0
        self.last_daily_reset = datetime.now().date()

        # Performance monitoring
        self.last_15min_check = datetime.now()
        self.last_hourly_check = datetime.now()
        self.last_4hour_check = datetime.now()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info(f"Trading Bot initialized - Mode: {mode.value.upper()}, Profile: {profile}")
        logger.info(f"Initial capital: ${self.current_capital:,.2f}")

    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load bot configuration"""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self.get_default_config()

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "trading_pairs": ["BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD"],
            "check_interval_seconds": 60,
            "performance_check_intervals": {
                "15_minutes": 900,
                "1_hour": 3600,
                "4_hours": 14400
            },
            "paper_mode": {
                "initial_capital": 10000
            },
            "demo_mode": {
                "initial_capital": 10000
            },
            "live_mode": {
                "requires_confirmation": True
            }
        }

    def get_initial_capital(self) -> float:
        """Get initial capital based on mode"""
        if self.mode == TradingMode.PAPER:
            return self.config.get('paper_mode', {}).get('initial_capital', 10000)
        elif self.mode == TradingMode.DEMO:
            return self.config.get('demo_mode', {}).get('initial_capital', 10000)
        else:
            # For live mode, would fetch from exchange
            return 0.0

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()

    def check_market_status(self) -> MarketStatus:
        """
        Check current market status
        Crypto markets are 24/7, but this is useful for traditional markets integration
        """
        now = datetime.now()

        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return MarketStatus.WEEKEND

        # For crypto, always open
        # For traditional markets, would check hours
        return MarketStatus.OPEN

    def is_weekend(self) -> bool:
        """Check if current time is weekend"""
        return datetime.now().weekday() >= 5

    def reset_daily_counters(self):
        """Reset daily counters if new day"""
        current_date = datetime.now().date()
        if current_date != self.last_daily_reset:
            logger.info(f"New day detected, resetting daily counters")
            self.daily_trade_count = 0
            self.last_daily_reset = current_date

    def fetch_market_data(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current market data for trading pair
        In production, this would connect to Kraken/MT5 API
        """
        try:
            # Simulated market data for paper/demo modes
            if self.mode in [TradingMode.PAPER, TradingMode.DEMO]:
                # Generate simulated data
                base_prices = {
                    "BTC/USD": 50000,
                    "ETH/USD": 3000,
                    "SOL/USD": 100,
                    "XRP/USD": 0.50
                }

                base_price = base_prices.get(pair, 1000)
                price_variation = (hash(str(datetime.now().timestamp())) % 100 - 50) / 10

                return {
                    "pair": pair,
                    "timestamp": datetime.now(),
                    "price": base_price + price_variation,
                    "volume": 1000000,
                    "bid": base_price + price_variation - 0.5,
                    "ask": base_price + price_variation + 0.5
                }
            else:
                # For live mode, would use real API
                logger.warning("Live mode API not implemented yet")
                return None

        except Exception as e:
            logger.error(f"Error fetching market data for {pair}: {e}")
            return None

    def analyze_market(self, pair: str, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze market and generate trading signals
        Uses pattern recognition and technical analysis
        """
        try:
            # In production, would use full candlestick analyzer
            # For now, simple momentum-based signal

            signal = None

            # Simple moving average crossover simulation
            if hash(str(market_data['timestamp'])) % 100 < 30:  # 30% chance of signal
                signal_type = "BUY" if hash(str(market_data['price'])) % 2 == 0 else "SELL"

                signal = {
                    "pair": pair,
                    "type": signal_type,
                    "price": market_data['price'],
                    "confidence": 0.75 + (hash(str(market_data['timestamp'])) % 20) / 100,
                    "pattern": "MOMENTUM_CROSSOVER",
                    "timestamp": market_data['timestamp']
                }

            return signal

        except Exception as e:
            logger.error(f"Error analyzing market for {pair}: {e}")
            return None

    def execute_trade(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute trade based on signal
        """
        try:
            # Check if we can execute (risk limits, etc.)
            if not self.can_execute_trade(signal):
                return None

            # Calculate position size
            position_size = self.calculate_position_size(signal)

            trade = {
                "id": len(self.performance_tracker.trades) + 1,
                "pair": signal['pair'],
                "type": signal['type'],
                "entry_price": signal['price'],
                "quantity": position_size / signal['price'],
                "position_value": position_size,
                "entry_time": signal['timestamp'],
                "stop_loss": self.calculate_stop_loss(signal),
                "take_profit": self.calculate_take_profit(signal),
                "status": "OPEN",
                "mode": self.mode.value,
                "profile": self.profile
            }

            # Execute trade
            if self.mode == TradingMode.LIVE:
                # Would execute real trade via API
                logger.warning("Live trading not implemented yet")
                return None
            else:
                # Paper/Demo trading - just record it
                self.open_positions.append(trade)
                self.daily_trade_count += 1

                # Track trade
                self.performance_tracker.record_trade(trade)

                logger.info(f"Trade executed: {trade['type']} {trade['pair']} @ ${trade['entry_price']:.2f}")
                logger.info(f"Position size: ${trade['position_value']:.2f}, Quantity: {trade['quantity']:.6f}")

                return trade

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            logger.error(traceback.format_exc())
            return None

    def can_execute_trade(self, signal: Dict[str, Any]) -> bool:
        """Check if trade can be executed based on risk parameters"""
        # Load risk profile
        config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'
        try:
            with open(config_path, 'r') as f:
                profiles = json.load(f)

            risk_params = profiles['profiles'][self.profile]['risk_parameters']

            # Check confidence threshold
            if signal['confidence'] < risk_params['confidence_threshold']:
                logger.debug(f"Signal confidence too low: {signal['confidence']}")
                return False

            # Check daily trade limit
            max_daily_trades = profiles['profiles'][self.profile].get('max_trades_per_day', 10)
            if self.daily_trade_count >= max_daily_trades:
                logger.debug(f"Daily trade limit reached: {self.daily_trade_count}/{max_daily_trades}")
                return False

            # Check max concurrent trades
            if len(self.open_positions) >= risk_params['max_concurrent_trades']:
                logger.debug(f"Max concurrent trades reached: {len(self.open_positions)}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking trade execution criteria: {e}")
            return False

    def calculate_position_size(self, signal: Dict[str, Any]) -> float:
        """Calculate position size based on risk parameters"""
        config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'
        try:
            with open(config_path, 'r') as f:
                profiles = json.load(f)

            risk_params = profiles['profiles'][self.profile]['risk_parameters']
            max_position_size = risk_params['max_position_size']

            return self.current_capital * max_position_size

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return self.current_capital * 0.01  # Default 1%

    def calculate_stop_loss(self, signal: Dict[str, Any]) -> float:
        """Calculate stop loss price"""
        config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'
        try:
            with open(config_path, 'r') as f:
                profiles = json.load(f)

            stop_loss_pct = profiles['profiles'][self.profile].get('stop_loss_percentage', 0.02)

            if signal['type'] == 'BUY':
                return signal['price'] * (1 - stop_loss_pct)
            else:
                return signal['price'] * (1 + stop_loss_pct)

        except Exception as e:
            logger.error(f"Error calculating stop loss: {e}")
            return signal['price'] * 0.98  # Default 2%

    def calculate_take_profit(self, signal: Dict[str, Any]) -> float:
        """Calculate take profit price"""
        config_path = Path(__file__).parent / 'config' / 'trading_risk_profiles.json'
        try:
            with open(config_path, 'r') as f:
                profiles = json.load(f)

            take_profit_pct = profiles['profiles'][self.profile].get('take_profit_percentage', 0.04)

            if signal['type'] == 'BUY':
                return signal['price'] * (1 + take_profit_pct)
            else:
                return signal['price'] * (1 - take_profit_pct)

        except Exception as e:
            logger.error(f"Error calculating take profit: {e}")
            return signal['price'] * 1.04  # Default 4%

    def check_open_positions(self):
        """Check and manage open positions"""
        for position in self.open_positions[:]:  # Copy list to allow removal
            # Fetch current price
            market_data = self.fetch_market_data(position['pair'])
            if not market_data:
                continue

            current_price = market_data['price']

            # Check stop loss
            if position['type'] == 'BUY' and current_price <= position['stop_loss']:
                self.close_position(position, current_price, "STOP_LOSS")
            elif position['type'] == 'SELL' and current_price >= position['stop_loss']:
                self.close_position(position, current_price, "STOP_LOSS")

            # Check take profit
            elif position['type'] == 'BUY' and current_price >= position['take_profit']:
                self.close_position(position, current_price, "TAKE_PROFIT")
            elif position['type'] == 'SELL' and current_price <= position['take_profit']:
                self.close_position(position, current_price, "TAKE_PROFIT")

    def close_position(self, position: Dict[str, Any], exit_price: float, reason: str):
        """Close an open position"""
        try:
            position['exit_price'] = exit_price
            position['exit_time'] = datetime.now()
            position['close_reason'] = reason
            position['status'] = 'CLOSED'

            # Calculate P/L
            if position['type'] == 'BUY':
                profit_loss = (exit_price - position['entry_price']) * position['quantity']
            else:
                profit_loss = (position['entry_price'] - exit_price) * position['quantity']

            position['profit_loss'] = profit_loss
            position['profit_loss_pct'] = (profit_loss / position['position_value']) * 100

            # Update capital
            self.current_capital += profit_loss

            # Update tracker
            self.performance_tracker.update_trade(position)

            # Remove from open positions
            self.open_positions.remove(position)

            logger.info(f"Position closed: {position['type']} {position['pair']} - {reason}")
            logger.info(f"P/L: ${profit_loss:.2f} ({position['profit_loss_pct']:.2f}%)")
            logger.info(f"Current capital: ${self.current_capital:,.2f}")

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            logger.error(traceback.format_exc())

    def perform_15min_check(self):
        """Perform 15-minute performance check"""
        logger.info("=== 15-Minute Performance Check ===")
        metrics = self.performance_tracker.get_current_metrics()

        logger.info(f"Current Capital: ${self.current_capital:,.2f}")
        logger.info(f"Open Positions: {len(self.open_positions)}")
        logger.info(f"Trades Today: {self.daily_trade_count}")
        logger.info(f"Win Rate: {metrics.get('win_rate', 0):.2f}%")
        logger.info(f"Total P/L: ${metrics.get('total_profit_loss', 0):.2f}")

        self.last_15min_check = datetime.now()

    def perform_hourly_check(self):
        """Perform hourly performance check"""
        logger.info("=== Hourly Performance Check ===")
        metrics = self.performance_tracker.get_hourly_metrics()

        logger.info(f"Trades Last Hour: {metrics.get('trades_last_hour', 0)}")
        logger.info(f"Hourly P/L: ${metrics.get('hourly_profit_loss', 0):.2f}")
        logger.info(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}")

        # Export hourly report
        self.performance_tracker.export_json()

        self.last_hourly_check = datetime.now()

    def perform_4hour_check(self):
        """Perform 4-hour performance check"""
        logger.info("=== 4-Hour Performance Check ===")
        metrics = self.performance_tracker.get_performance_summary()

        logger.info(f"Total Trades: {metrics.get('total_trades', 0)}")
        logger.info(f"Total P/L: ${metrics.get('total_profit_loss', 0):.2f}")
        logger.info(f"ROI: {metrics.get('roi_percentage', 0):.2f}%")
        logger.info(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")

        # Export comprehensive report
        self.performance_tracker.export_csv()
        self.performance_tracker.generate_performance_report()

        self.last_4hour_check = datetime.now()

    def check_performance_intervals(self):
        """Check if it's time for performance monitoring"""
        now = datetime.now()

        # 15-minute check
        if (now - self.last_15min_check).total_seconds() >= 900:  # 15 minutes
            self.perform_15min_check()

        # Hourly check
        if (now - self.last_hourly_check).total_seconds() >= 3600:  # 1 hour
            self.perform_hourly_check()

        # 4-hour check
        if (now - self.last_4hour_check).total_seconds() >= 14400:  # 4 hours
            self.perform_4hour_check()

    def run_trading_cycle(self):
        """Run one trading cycle"""
        try:
            # Reset daily counters if needed
            self.reset_daily_counters()

            # Check market status
            market_status = self.check_market_status()

            # Handle weekends (for crypto, still trade; for stocks, pause)
            if self.is_weekend():
                logger.debug("Weekend detected - Crypto markets still active")

            # Check open positions
            self.check_open_positions()

            # Scan trading pairs for signals
            for pair in self.config.get('trading_pairs', []):
                # Fetch market data
                market_data = self.fetch_market_data(pair)
                if not market_data:
                    continue

                # Analyze market
                signal = self.analyze_market(pair, market_data)
                if not signal:
                    continue

                # Execute trade if signal is valid
                self.execute_trade(signal)

            # Check performance intervals
            self.check_performance_intervals()

        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            logger.error(traceback.format_exc())
            # Don't crash, just log and continue

    def start(self):
        """Start the 24/7 trading bot"""
        if self.running:
            logger.warning("Bot is already running")
            return

        self.running = True
        self.start_time = datetime.now()

        logger.info("="*70)
        logger.info(f"24/7 TRADING BOT STARTED")
        logger.info(f"Mode: {self.mode.value.upper()}")
        logger.info(f"Profile: {self.profile}")
        logger.info(f"Start Time: {self.start_time}")
        logger.info(f"Trading Pairs: {', '.join(self.config.get('trading_pairs', []))}")
        logger.info("="*70)

        if self.mode == TradingMode.LIVE:
            logger.warning("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK ⚠️")
            confirmation = input("Type 'CONFIRM' to proceed with live trading: ")
            if confirmation != "CONFIRM":
                logger.info("Live trading cancelled by user")
                self.running = False
                return

        # Main loop
        check_interval = self.config.get('check_interval_seconds', 60)

        while self.running:
            try:
                # Run trading cycle
                self.run_trading_cycle()

                # Sleep until next check
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping...")
                self.stop()
                break

            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.error(traceback.format_exc())

                # Auto-restart on failure
                self.restart_count += 1
                if self.restart_count < self.max_restarts:
                    logger.info(f"Auto-restarting... (attempt {self.restart_count}/{self.max_restarts})")
                    time.sleep(30)  # Wait 30 seconds before restart
                else:
                    logger.error(f"Max restart attempts reached ({self.max_restarts}), stopping bot")
                    self.stop()
                    break

    def stop(self):
        """Stop the trading bot gracefully"""
        if not self.running:
            return

        logger.info("Stopping trading bot...")
        self.running = False

        # Close all open positions
        if self.open_positions:
            logger.info(f"Closing {len(self.open_positions)} open positions...")
            for position in self.open_positions[:]:
                market_data = self.fetch_market_data(position['pair'])
                if market_data:
                    self.close_position(position, market_data['price'], "BOT_SHUTDOWN")

        # Generate final report
        logger.info("Generating final performance report...")
        self.performance_tracker.generate_performance_report()
        self.performance_tracker.export_json()
        self.performance_tracker.export_csv()

        # Log summary
        runtime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        logger.info("="*70)
        logger.info("24/7 TRADING BOT STOPPED")
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Total Trades: {len(self.performance_tracker.trades)}")
        logger.info(f"Final Capital: ${self.current_capital:,.2f}")
        logger.info(f"Total P/L: ${self.current_capital - self.get_initial_capital():.2f}")
        logger.info("="*70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='24/7 Trading Bot')
    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'demo', 'live'],
                       help='Trading mode (default: paper)')
    parser.add_argument('--profile', type=str, default='beginner',
                       choices=['beginner', 'novice', 'advanced'],
                       help='Risk profile (default: beginner)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')

    args = parser.parse_args()

    # Create and start bot
    mode = TradingMode(args.mode)
    bot = TradingBot24x7(mode=mode, profile=args.profile, config_path=args.config)

    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        bot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
