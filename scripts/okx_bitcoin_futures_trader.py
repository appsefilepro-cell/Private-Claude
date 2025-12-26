#!/usr/bin/env python3
"""
OKX Bitcoin Futures Trading Bot
Trades Bitcoin futures with ML pattern detection and adaptive learning
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
import sys
import logging
import requests
from typing import List, Dict, Tuple, Optional
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('okx_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OKXBitcoinFuturesTrader:
    """OKX Bitcoin Futures Trading Bot with ML Pattern Detection"""

    def __init__(self, config_path: str = '/home/user/Private-Claude/MT5_AND_OKX_TRADING_CONFIG.json'):
        self.config_path = config_path
        self.exchange = None
        self.trading_active = False
        self.trade_history = []
        self.winning_patterns = {}
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'win_rate': 0,
            'best_trade': 0,
            'worst_trade': 0
        }
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            self.okx_config = self.config['okx_account']
            self.api_key = self.okx_config['api_key']
            self.secret_key = self.okx_config['secret_key']
            self.passphrase = self.okx_config.get('passphrase', '')

            # Get Zapier webhook
            self.zapier_webhook = self.config.get('zapier_integration', {}).get('okx_zapier_integration', {}).get('webhook_url')

            # Get trading pairs
            self.trading_pairs = self.config.get('okx_bitcoin_futures_pairs', {}).get('perpetual_swaps', [])

            logger.info("OKX Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def connect(self, demo_mode: bool = True) -> bool:
        """Connect to OKX exchange"""
        try:
            # Initialize CCXT OKX exchange
            self.exchange = ccxt.okx({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'password': self.passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',  # For perpetual futures
                }
            })

            # Set to demo mode if specified
            if demo_mode:
                self.exchange.set_sandbox_mode(True)
                logger.info("✓ Connected to OKX in DEMO mode")
            else:
                logger.warning("⚠ Connected to OKX in LIVE mode - real money at risk!")

            # Test connection
            balance = self.exchange.fetch_balance()
            logger.info(f"  Account balance: {balance.get('USDT', {}).get('total', 0)} USDT")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to OKX: {e}")
            return False

    def get_available_symbols(self) -> List[str]:
        """Get available Bitcoin futures symbols"""
        try:
            markets = self.exchange.load_markets()
            btc_futures = [
                symbol for symbol in markets
                if 'BTC' in symbol and 'SWAP' in symbol
            ]
            logger.info(f"Found {len(btc_futures)} Bitcoin futures symbols")
            return btc_futures
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []

    def fetch_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for analysis"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for trading signals"""
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['signal']

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

        # Volume analysis
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']

        return df

    def detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect candlestick patterns"""
        if len(df) < 10:
            return {'pattern': 'NONE', 'signal': 'NONE', 'confidence': 0}

        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]

        # Calculate candle properties
        body = abs(last_candle['close'] - last_candle['open'])
        range_val = last_candle['high'] - last_candle['low']
        upper_shadow = last_candle['high'] - max(last_candle['open'], last_candle['close'])
        lower_shadow = min(last_candle['open'], last_candle['close']) - last_candle['low']

        signal = 'NONE'
        confidence = 0
        pattern = 'NONE'

        # Bullish Engulfing
        if (prev_candle['close'] < prev_candle['open'] and
            last_candle['close'] > last_candle['open'] and
            last_candle['open'] < prev_candle['close'] and
            last_candle['close'] > prev_candle['open']):
            signal = 'BUY'
            confidence = 0.80
            pattern = 'BULLISH_ENGULFING'

        # Bearish Engulfing
        elif (prev_candle['close'] > prev_candle['open'] and
              last_candle['close'] < last_candle['open'] and
              last_candle['open'] > prev_candle['close'] and
              last_candle['close'] < prev_candle['open']):
            signal = 'SELL'
            confidence = 0.80
            pattern = 'BEARISH_ENGULFING'

        # Hammer (bullish)
        elif range_val > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.3:
            signal = 'BUY'
            confidence = 0.70
            pattern = 'HAMMER'

        # Shooting Star (bearish)
        elif range_val > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.3:
            signal = 'SELL'
            confidence = 0.70
            pattern = 'SHOOTING_STAR'

        # Morning Star (bullish)
        elif len(df) >= 3:
            third_last = df.iloc[-3]
            if (third_last['close'] < third_last['open'] and
                prev_candle['close'] < third_last['close'] and
                last_candle['close'] > last_candle['open'] and
                last_candle['close'] > (third_last['open'] + third_last['close']) / 2):
                signal = 'BUY'
                confidence = 0.85
                pattern = 'MORNING_STAR'

        # Evening Star (bearish)
        elif len(df) >= 3:
            third_last = df.iloc[-3]
            if (third_last['close'] > third_last['open'] and
                prev_candle['close'] > third_last['close'] and
                last_candle['close'] < last_candle['open'] and
                last_candle['close'] < (third_last['open'] + third_last['close']) / 2):
                signal = 'SELL'
                confidence = 0.85
                pattern = 'EVENING_STAR'

        return {
            'pattern': pattern,
            'signal': signal,
            'confidence': confidence
        }

    def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a symbol for trading opportunities"""
        try:
            # Fetch OHLCV data
            df = self.fetch_ohlcv(symbol, timeframe='15m', limit=100)
            if df is None or len(df) < 50:
                return None

            # Calculate indicators
            df = self.calculate_technical_indicators(df)

            # Detect candlestick patterns
            pattern_analysis = self.detect_candlestick_patterns(df)

            # Get latest values
            latest = df.iloc[-1]
            signal = 'NONE'
            confidence = 0

            # Multi-factor analysis
            factors = []

            # 1. Candlestick pattern
            if pattern_analysis['signal'] != 'NONE':
                factors.append({
                    'factor': 'candlestick_pattern',
                    'signal': pattern_analysis['signal'],
                    'weight': pattern_analysis['confidence']
                })

            # 2. MACD
            if pd.notna(latest['macd']) and pd.notna(latest['signal']):
                if latest['macd'] > latest['signal'] and latest['macd_histogram'] > 0:
                    factors.append({'factor': 'macd', 'signal': 'BUY', 'weight': 0.15})
                elif latest['macd'] < latest['signal'] and latest['macd_histogram'] < 0:
                    factors.append({'factor': 'macd', 'signal': 'SELL', 'weight': 0.15})

            # 3. RSI
            if pd.notna(latest['rsi']):
                if latest['rsi'] < 30:
                    factors.append({'factor': 'rsi', 'signal': 'BUY', 'weight': 0.20})
                elif latest['rsi'] > 70:
                    factors.append({'factor': 'rsi', 'signal': 'SELL', 'weight': 0.20})

            # 4. Moving Average Crossover
            if pd.notna(latest['sma_20']) and pd.notna(latest['sma_50']):
                if latest['sma_20'] > latest['sma_50'] and latest['close'] > latest['sma_20']:
                    factors.append({'factor': 'ma_crossover', 'signal': 'BUY', 'weight': 0.15})
                elif latest['sma_20'] < latest['sma_50'] and latest['close'] < latest['sma_20']:
                    factors.append({'factor': 'ma_crossover', 'signal': 'SELL', 'weight': 0.15})

            # 5. Bollinger Bands
            if pd.notna(latest['bb_lower']) and pd.notna(latest['bb_upper']):
                if latest['close'] < latest['bb_lower']:
                    factors.append({'factor': 'bollinger', 'signal': 'BUY', 'weight': 0.15})
                elif latest['close'] > latest['bb_upper']:
                    factors.append({'factor': 'bollinger', 'signal': 'SELL', 'weight': 0.15})

            # Calculate weighted signal
            if factors:
                buy_weight = sum(f['weight'] for f in factors if f['signal'] == 'BUY')
                sell_weight = sum(f['weight'] for f in factors if f['signal'] == 'SELL')

                if buy_weight > sell_weight and buy_weight > 0.50:
                    signal = 'BUY'
                    confidence = min(buy_weight, 1.0)
                elif sell_weight > buy_weight and sell_weight > 0.50:
                    signal = 'SELL'
                    confidence = min(sell_weight, 1.0)

            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'pattern': pattern_analysis['pattern'],
                'current_price': latest['close'],
                'rsi': latest['rsi'],
                'macd': latest['macd'],
                'factors': factors
            }

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None

    def calculate_position_size(self, symbol: str, risk_percent: float = 1.0) -> float:
        """Calculate position size based on account balance and risk"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)

            if usdt_balance <= 0:
                return 0

            # Risk amount
            risk_amount = usdt_balance * (risk_percent / 100.0)

            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']

            # Calculate position size (contracts/amount)
            # For conservative approach, use small position
            position_size = min(risk_amount / current_price, usdt_balance * 0.02)  # Max 2% of balance

            return round(position_size, 6)

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.001  # Minimum position

    def place_order(self, symbol: str, side: str, amount: float, order_type: str = 'market') -> Optional[Dict]:
        """Place an order on OKX"""
        try:
            # Place order
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side.lower(),
                amount=amount
            )

            logger.info(f"✓ Order placed: {side} {amount} {symbol}")

            order_info = {
                'account': 'OKX',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'order_id': order.get('id'),
                'timestamp': datetime.now().isoformat(),
                'status': order.get('status')
            }

            # Send to Zapier
            self.send_to_zapier(order_info, 'order_placed')

            # Add to trade history
            self.trade_history.append(order_info)
            self.performance_metrics['total_trades'] += 1

            return order_info

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def close_position(self, symbol: str) -> bool:
        """Close an open position"""
        try:
            # Get current position
            positions = self.exchange.fetch_positions([symbol])

            for position in positions:
                if position['contracts'] != 0:
                    side = 'sell' if position['side'] == 'long' else 'buy'
                    amount = abs(position['contracts'])

                    # Close position
                    order = self.exchange.create_order(
                        symbol=symbol,
                        type='market',
                        side=side,
                        amount=amount,
                        params={'reduceOnly': True}
                    )

                    logger.info(f"✓ Position closed: {symbol}")

                    # Calculate P&L
                    pnl = position.get('unrealizedPnl', 0)

                    close_info = {
                        'account': 'OKX',
                        'symbol': symbol,
                        'pnl': pnl,
                        'timestamp': datetime.now().isoformat()
                    }

                    # Send to Zapier
                    self.send_to_zapier(close_info, 'position_closed')

                    # Update performance metrics
                    if pnl > 0:
                        self.performance_metrics['winning_trades'] += 1
                        self.analyze_winning_trade(symbol, pnl)
                    else:
                        self.performance_metrics['losing_trades'] += 1

                    self.performance_metrics['total_profit'] += pnl
                    self.performance_metrics['best_trade'] = max(self.performance_metrics['best_trade'], pnl)
                    self.performance_metrics['worst_trade'] = min(self.performance_metrics['worst_trade'], pnl)

                    # Calculate win rate
                    if self.performance_metrics['total_trades'] > 0:
                        self.performance_metrics['win_rate'] = (
                            self.performance_metrics['winning_trades'] /
                            self.performance_metrics['total_trades'] * 100
                        )

                    return True

            return False

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    def analyze_winning_trade(self, symbol: str, pnl: float):
        """Analyze winning trades for ML learning"""
        if symbol not in self.winning_patterns:
            self.winning_patterns[symbol] = {
                'count': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'success_rate': 0
            }

        self.winning_patterns[symbol]['count'] += 1
        self.winning_patterns[symbol]['total_profit'] += pnl
        self.winning_patterns[symbol]['avg_profit'] = (
            self.winning_patterns[symbol]['total_profit'] /
            self.winning_patterns[symbol]['count']
        )

        logger.info(f"ML Learning: {symbol} winning pattern. Wins: {self.winning_patterns[symbol]['count']}, Avg profit: ${self.winning_patterns[symbol]['avg_profit']:.2f}")

        # Save to file for persistent learning
        self.save_learning_data()

    def save_learning_data(self):
        """Save ML learning data to file"""
        try:
            learning_data = {
                'winning_patterns': self.winning_patterns,
                'performance_metrics': self.performance_metrics,
                'timestamp': datetime.now().isoformat()
            }

            with open('/home/user/Private-Claude/okx_ml_learning.json', 'w') as f:
                json.dump(learning_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving learning data: {e}")

    def load_learning_data(self):
        """Load ML learning data from file"""
        try:
            if os.path.exists('/home/user/Private-Claude/okx_ml_learning.json'):
                with open('/home/user/Private-Claude/okx_ml_learning.json', 'r') as f:
                    learning_data = json.load(f)
                    self.winning_patterns = learning_data.get('winning_patterns', {})
                    logger.info("Loaded ML learning data from previous sessions")
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")

    def send_to_zapier(self, data: Dict, event_type: str):
        """Send trade data to Zapier webhook"""
        if not self.zapier_webhook:
            return

        payload = {
            'event_type': event_type,
            'account_type': 'OKX',
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        try:
            response = requests.post(self.zapier_webhook, json=payload, timeout=5)
            if response.status_code == 200:
                logger.debug(f"Sent to Zapier: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send to Zapier: {e}")

    def manage_open_positions(self):
        """Manage open positions - close if profit/loss targets reached"""
        try:
            positions = self.exchange.fetch_positions()

            for position in positions:
                if position['contracts'] == 0:
                    continue

                symbol = position['symbol']
                pnl = position.get('unrealizedPnl', 0)

                # Close if profit target or stop loss reached
                if pnl >= 30 or pnl <= -20:
                    logger.info(f"Closing {symbol} - P&L: ${pnl:.2f}")
                    self.close_position(symbol)
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Error managing positions: {e}")

    def trading_loop(self):
        """Main trading loop"""
        logger.info("Starting OKX Bitcoin Futures trading loop...")

        # Load previous learning data
        self.load_learning_data()

        while self.trading_active:
            try:
                # Get available symbols
                symbols = self.get_available_symbols()
                if not symbols:
                    symbols = self.trading_pairs

                logger.info(f"Scanning {len(symbols)} symbols...")

                # Analyze symbols
                signals = []
                for symbol in symbols[:5]:  # Limit to first 5 symbols
                    analysis = self.analyze_symbol(symbol)
                    if analysis and analysis['signal'] != 'NONE' and analysis['confidence'] > 0.65:
                        signals.append(analysis)
                        logger.info(f"Signal: {analysis['signal']} {symbol} (confidence: {analysis['confidence']:.2f}, pattern: {analysis['pattern']})")
                    time.sleep(2)

                # Execute trades
                if signals:
                    # Sort by confidence
                    signals.sort(key=lambda x: x['confidence'], reverse=True)

                    # Place orders (max 2 per cycle)
                    for signal in signals[:2]:
                        symbol = signal['symbol']
                        side = signal['signal'].lower()

                        # Calculate position size
                        amount = self.calculate_position_size(symbol, risk_percent=0.5)

                        if amount > 0:
                            self.place_order(symbol, side, amount)
                            time.sleep(2)

                # Manage existing positions
                self.manage_open_positions()

                # Generate report
                self.generate_report()

                # Wait 15 minutes before next scan
                logger.info("Waiting 15 minutes before next scan...")
                time.sleep(900)

            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)

    def start_trading(self, demo_mode: bool = True):
        """Start trading"""
        if not self.connect(demo_mode=demo_mode):
            logger.error("Failed to connect to OKX")
            return

        self.trading_active = True
        logger.info("=" * 60)
        logger.info("OKX BITCOIN FUTURES TRADING STARTED")
        logger.info("Mode: DEMO" if demo_mode else "Mode: LIVE - REAL MONEY AT RISK!")
        logger.info("=" * 60)

        try:
            self.trading_loop()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop_trading()

    def stop_trading(self):
        """Stop trading"""
        self.trading_active = False
        logger.info("Trading stopped")
        self.generate_report()

    def generate_report(self):
        """Generate trading report"""
        logger.info("=" * 60)
        logger.info("OKX TRADING REPORT")
        logger.info("=" * 60)
        logger.info(f"Total Trades: {self.performance_metrics['total_trades']}")
        logger.info(f"Winning Trades: {self.performance_metrics['winning_trades']}")
        logger.info(f"Losing Trades: {self.performance_metrics['losing_trades']}")
        logger.info(f"Win Rate: {self.performance_metrics['win_rate']:.2f}%")
        logger.info(f"Total Profit: ${self.performance_metrics['total_profit']:.2f}")
        logger.info(f"Best Trade: ${self.performance_metrics['best_trade']:.2f}")
        logger.info(f"Worst Trade: ${self.performance_metrics['worst_trade']:.2f}")
        logger.info("=" * 60)

        # Send report to Zapier
        self.send_to_zapier(self.performance_metrics, 'trading_report')


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='OKX Bitcoin Futures Trading Bot')
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo', help='Trading mode')
    args = parser.parse_args()

    logger.info("OKX Bitcoin Futures Trader Starting...")

    trader = OKXBitcoinFuturesTrader()

    demo_mode = args.mode == 'demo'

    try:
        trader.start_trading(demo_mode=demo_mode)
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal")
        trader.stop_trading()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        trader.stop_trading()


if __name__ == "__main__":
    main()
