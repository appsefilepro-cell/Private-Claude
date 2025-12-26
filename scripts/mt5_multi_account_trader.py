#!/usr/bin/env python3
"""
MetaTrader 5 Multi-Account Trading Bot
Connects to 3 MT5 demo accounts and trades all available pairs
"""

import MetaTrader5 as mt5
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
from queue import Queue

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MT5Account:
    """Represents a single MT5 trading account"""

    def __init__(self, account_config: Dict, zapier_webhook: str = None):
        self.login = int(account_config['login'])
        self.password = account_config['password']
        self.server = account_config['server']
        self.account_number = account_config['account_number']
        self.account_type = account_config['account_type']
        self.leverage = account_config['leverage']
        self.zapier_webhook = zapier_webhook
        self.connected = False
        self.trade_history = []
        self.winning_patterns = {}

    def connect(self) -> bool:
        """Connect to MT5 account"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed for account {self.login}")
                return False

            authorized = mt5.login(login=self.login, server=self.server, password=self.password)
            if not authorized:
                logger.error(f"Failed to connect to account {self.login}, error: {mt5.last_error()}")
                mt5.shutdown()
                return False

            self.connected = True
            logger.info(f"✓ Connected to MT5 Account {self.account_number}: {self.login}")

            # Get account info
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"  Balance: ${account_info.balance:.2f}")
                logger.info(f"  Equity: ${account_info.equity:.2f}")
                logger.info(f"  Leverage: {account_info.leverage}")

            return True

        except Exception as e:
            logger.error(f"Error connecting to account {self.login}: {e}")
            return False

    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info(f"Disconnected from account {self.login}")

    def get_available_symbols(self) -> List[str]:
        """Get all available trading symbols"""
        if not self.connected:
            return []

        symbols = mt5.symbols_get()
        if symbols is None:
            logger.error(f"Failed to get symbols for account {self.login}")
            return []

        # Filter to get tradeable symbols
        tradeable_symbols = [s.name for s in symbols if s.visible and s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL]
        logger.info(f"Account {self.login}: Found {len(tradeable_symbols)} tradeable symbols")
        return tradeable_symbols

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get information about a symbol"""
        if not self.connected:
            return None

        info = mt5.symbol_info(symbol)
        if info is None:
            return None

        return {
            'symbol': symbol,
            'bid': info.bid,
            'ask': info.ask,
            'spread': info.spread,
            'point': info.point,
            'trade_contract_size': info.trade_contract_size,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step
        }

    def calculate_lot_size(self, symbol: str, risk_percent: float = 1.0) -> float:
        """Calculate position size based on account balance and risk"""
        account_info = mt5.account_info()
        if not account_info:
            return 0.01  # Default minimum lot

        balance = account_info.balance
        risk_amount = balance * (risk_percent / 100.0)

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return 0.01

        # Calculate lot size (simplified - should include stop loss distance)
        lot_size = risk_amount / (symbol_info.trade_contract_size * symbol_info.point * 100)

        # Round to volume step
        lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        lot_size = round(lot_size / symbol_info.volume_step) * symbol_info.volume_step

        return lot_size

    def analyze_pattern(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M15) -> Dict:
        """Analyze candlestick patterns for trading signals"""
        if not self.connected:
            return {'signal': 'NONE', 'confidence': 0}

        # Get historical data
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
        if rates is None or len(rates) < 10:
            return {'signal': 'NONE', 'confidence': 0}

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # Simple pattern detection
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
            confidence = 0.75
            pattern = 'BULLISH_ENGULFING'

        # Bearish Engulfing
        elif (prev_candle['close'] > prev_candle['open'] and
              last_candle['close'] < last_candle['open'] and
              last_candle['open'] > prev_candle['close'] and
              last_candle['close'] < prev_candle['open']):
            signal = 'SELL'
            confidence = 0.75
            pattern = 'BEARISH_ENGULFING'

        # Hammer (bullish)
        elif (lower_shadow > body * 2 and upper_shadow < body * 0.3 and range_val > 0):
            signal = 'BUY'
            confidence = 0.65
            pattern = 'HAMMER'

        # Shooting Star (bearish)
        elif (upper_shadow > body * 2 and lower_shadow < body * 0.3 and range_val > 0):
            signal = 'SELL'
            confidence = 0.65
            pattern = 'SHOOTING_STAR'

        # Calculate moving averages for additional confirmation
        if len(df) >= 20:
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean() if len(df) >= 50 else df['close'].rolling(window=20).mean()

            current_price = last_candle['close']
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]

            # Confirm signals with MA
            if signal == 'BUY' and current_price > sma_20 and sma_20 > sma_50:
                confidence += 0.15
            elif signal == 'SELL' and current_price < sma_20 and sma_20 < sma_50:
                confidence += 0.15

        return {
            'signal': signal,
            'confidence': min(confidence, 1.0),
            'pattern': pattern,
            'symbol': symbol,
            'current_price': last_candle['close']
        }

    def place_order(self, symbol: str, order_type: str, volume: float, stop_loss_pips: int = 20, take_profit_pips: int = 30) -> Optional[Dict]:
        """Place a market order"""
        if not self.connected:
            logger.error(f"Cannot place order - not connected to account {self.login}")
            return None

        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}")
                return None

        # Prepare order request
        point = symbol_info.point
        price = symbol_info.ask if order_type == 'BUY' else symbol_info.bid

        # Calculate SL and TP
        if order_type == 'BUY':
            sl = price - stop_loss_pips * point * 10
            tp = price + take_profit_pips * point * 10
            trade_type = mt5.ORDER_TYPE_BUY
        else:
            sl = price + stop_loss_pips * point * 10
            tp = price - take_profit_pips * point * 10
            trade_type = mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": trade_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": f"ML Pattern Trading - {self.account_number}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)

        if result is None:
            logger.error(f"Order send failed for {symbol}")
            return None

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None

        order_info = {
            'account': self.login,
            'account_number': self.account_number,
            'symbol': symbol,
            'type': order_type,
            'volume': volume,
            'price': price,
            'sl': sl,
            'tp': tp,
            'order_id': result.order,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"✓ Order placed: {order_type} {volume} {symbol} @ {price}")

        # Send to Zapier
        self.send_to_zapier(order_info, 'order_placed')

        # Add to trade history
        self.trade_history.append(order_info)

        return order_info

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.connected:
            return []

        positions = mt5.positions_get()
        if positions is None:
            return []

        return [{
            'ticket': p.ticket,
            'symbol': p.symbol,
            'type': 'BUY' if p.type == mt5.POSITION_TYPE_BUY else 'SELL',
            'volume': p.volume,
            'price_open': p.price_open,
            'price_current': p.price_current,
            'profit': p.profit,
            'sl': p.sl,
            'tp': p.tp
        } for p in positions]

    def close_position(self, ticket: int) -> bool:
        """Close a position"""
        if not self.connected:
            return False

        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False

        position = position[0]

        # Prepare close request
        symbol = position.symbol
        symbol_info = mt5.symbol_info(symbol)

        if position.type == mt5.POSITION_TYPE_BUY:
            trade_type = mt5.ORDER_TYPE_SELL
            price = symbol_info.bid
        else:
            trade_type = mt5.ORDER_TYPE_BUY
            price = symbol_info.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position.volume,
            "type": trade_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"✓ Position {ticket} closed with profit: ${position.profit:.2f}")

            # Send to Zapier
            close_info = {
                'account': self.login,
                'ticket': ticket,
                'symbol': symbol,
                'profit': position.profit,
                'timestamp': datetime.now().isoformat()
            }
            self.send_to_zapier(close_info, 'position_closed')

            # Analyze if it was a winning trade
            if position.profit > 0:
                self.analyze_winning_trade(position)

            return True

        return False

    def analyze_winning_trade(self, position):
        """Analyze winning trades for ML pattern learning"""
        symbol = position.symbol
        if symbol not in self.winning_patterns:
            self.winning_patterns[symbol] = {
                'count': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'patterns': {}
            }

        self.winning_patterns[symbol]['count'] += 1
        self.winning_patterns[symbol]['total_profit'] += position.profit
        self.winning_patterns[symbol]['avg_profit'] = (
            self.winning_patterns[symbol]['total_profit'] /
            self.winning_patterns[symbol]['count']
        )

        logger.info(f"ML Learning: {symbol} winning pattern detected. Total wins: {self.winning_patterns[symbol]['count']}")

    def send_to_zapier(self, data: Dict, event_type: str):
        """Send trade data to Zapier webhook"""
        if not self.zapier_webhook:
            return

        payload = {
            'event_type': event_type,
            'account_type': 'MT5',
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        try:
            response = requests.post(self.zapier_webhook, json=payload, timeout=5)
            if response.status_code == 200:
                logger.debug(f"Sent to Zapier: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send to Zapier: {e}")

    def get_account_stats(self) -> Dict:
        """Get account statistics"""
        if not self.connected:
            return {}

        account_info = mt5.account_info()
        if not account_info:
            return {}

        return {
            'account': self.login,
            'account_number': self.account_number,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'profit': account_info.profit,
            'margin': account_info.margin,
            'margin_free': account_info.margin_free,
            'margin_level': account_info.margin_level if account_info.margin > 0 else 0,
            'open_positions': len(self.get_open_positions()),
            'total_trades': len(self.trade_history),
            'timestamp': datetime.now().isoformat()
        }


class MT5MultiAccountTrader:
    """Manages trading across multiple MT5 accounts"""

    def __init__(self, config_path: str = '/home/user/Private-Claude/MT5_AND_OKX_TRADING_CONFIG.json'):
        self.config_path = config_path
        self.accounts: List[MT5Account] = []
        self.trading_active = False
        self.trade_queue = Queue()
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            logger.info("Configuration loaded successfully")

            # Get Zapier webhook
            zapier_webhook = self.config.get('zapier_integration', {}).get('metatrader_zapier_integration', {}).get('webhook_url')

            # Initialize accounts
            for acc_config in self.config['metatrader5_accounts']:
                account = MT5Account(acc_config, zapier_webhook)
                self.accounts.append(account)

            logger.info(f"Initialized {len(self.accounts)} MT5 accounts")

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def connect_all_accounts(self) -> bool:
        """Connect to all MT5 accounts"""
        logger.info("Connecting to all MT5 accounts...")

        success_count = 0
        for account in self.accounts:
            if account.connect():
                success_count += 1
            time.sleep(2)  # Wait between connections

        logger.info(f"Connected to {success_count}/{len(self.accounts)} accounts")
        return success_count > 0

    def disconnect_all_accounts(self):
        """Disconnect from all accounts"""
        for account in self.accounts:
            account.disconnect()

    def get_target_symbols(self) -> List[str]:
        """Get list of target symbols to trade"""
        pairs_config = self.config.get('metatrader5_pairs', {})

        symbols = []
        for category in ['forex_majors', 'forex_crosses', 'forex_exotics', 'crypto_cfd']:
            symbols.extend(pairs_config.get(category, []))

        # Clean up symbols (remove descriptions in parentheses)
        cleaned_symbols = []
        for symbol in symbols:
            if '(' in symbol:
                symbol = symbol.split('(')[0].strip()
            cleaned_symbols.append(symbol)

        return cleaned_symbols

    def scan_for_signals(self, account: MT5Account) -> List[Dict]:
        """Scan all symbols for trading signals"""
        if not account.connected:
            return []

        available_symbols = account.get_available_symbols()
        target_symbols = self.get_target_symbols()

        # Match available symbols with targets
        matched_symbols = []
        for target in target_symbols:
            for available in available_symbols:
                if target.replace('/', '') in available or target in available:
                    matched_symbols.append(available)
                    break

        logger.info(f"Account {account.account_number}: Scanning {len(matched_symbols)} symbols")

        signals = []
        for symbol in matched_symbols[:40]:  # Limit to first 40 symbols
            try:
                analysis = account.analyze_pattern(symbol)
                if analysis['signal'] != 'NONE' and analysis['confidence'] > 0.65:
                    signals.append(analysis)
                time.sleep(0.1)  # Small delay between scans
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")

        return signals

    def execute_trades(self, account: MT5Account, signals: List[Dict], max_trades: int = 3):
        """Execute trades based on signals"""
        if not account.connected:
            return

        # Check current positions
        open_positions = account.get_open_positions()
        if len(open_positions) >= 10:
            logger.info(f"Account {account.account_number}: Max positions reached")
            return

        # Sort signals by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)

        trades_executed = 0
        for signal in signals[:max_trades]:
            if trades_executed >= max_trades:
                break

            symbol = signal['symbol']
            order_type = signal['signal']

            # Calculate position size
            lot_size = account.calculate_lot_size(symbol, risk_percent=1.0)

            # Place order
            order = account.place_order(
                symbol=symbol,
                order_type=order_type,
                volume=lot_size,
                stop_loss_pips=20,
                take_profit_pips=30
            )

            if order:
                trades_executed += 1
                time.sleep(1)

        logger.info(f"Account {account.account_number}: Executed {trades_executed} trades")

    def manage_positions(self, account: MT5Account):
        """Manage open positions - close if needed"""
        if not account.connected:
            return

        positions = account.get_open_positions()

        for position in positions:
            # Close if profit reached or loss exceeded
            if position['profit'] >= 30 or position['profit'] <= -20:
                account.close_position(position['ticket'])
                time.sleep(0.5)

    def trading_loop_for_account(self, account: MT5Account):
        """Main trading loop for a single account"""
        logger.info(f"Starting trading loop for account {account.account_number}")

        while self.trading_active:
            try:
                # Scan for signals
                signals = self.scan_for_signals(account)

                # Execute trades if signals found
                if signals:
                    logger.info(f"Account {account.account_number}: Found {len(signals)} signals")
                    self.execute_trades(account, signals, max_trades=2)

                # Manage existing positions
                self.manage_positions(account)

                # Get account stats
                stats = account.get_account_stats()
                if stats:
                    logger.info(f"Account {account.account_number}: Balance=${stats['balance']:.2f}, Equity=${stats['equity']:.2f}, Positions={stats['open_positions']}")

                # Wait before next cycle (15 minutes)
                time.sleep(900)

            except Exception as e:
                logger.error(f"Error in trading loop for account {account.account_number}: {e}")
                time.sleep(60)

    def start_trading(self):
        """Start trading on all accounts"""
        if not self.connect_all_accounts():
            logger.error("Failed to connect to accounts")
            return

        self.trading_active = True
        logger.info("=" * 60)
        logger.info("STARTING 24-HOUR TRADING MARATHON")
        logger.info("=" * 60)

        # Start trading threads for each account
        threads = []
        for account in self.accounts:
            if account.connected:
                thread = threading.Thread(target=self.trading_loop_for_account, args=(account,))
                thread.daemon = True
                thread.start()
                threads.append(thread)

        # Monitor and report
        try:
            while self.trading_active:
                time.sleep(3600)  # Report every hour
                self.generate_report()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop_trading()

    def stop_trading(self):
        """Stop trading and disconnect"""
        self.trading_active = False
        time.sleep(5)
        self.disconnect_all_accounts()
        logger.info("Trading stopped")

    def generate_report(self):
        """Generate trading report"""
        logger.info("=" * 60)
        logger.info("TRADING REPORT")
        logger.info("=" * 60)

        total_trades = 0
        total_profit = 0

        for account in self.accounts:
            if account.connected:
                stats = account.get_account_stats()
                total_trades += stats.get('total_trades', 0)
                total_profit += stats.get('profit', 0)

                logger.info(f"Account {account.account_number}:")
                logger.info(f"  Trades: {stats.get('total_trades', 0)}")
                logger.info(f"  Profit: ${stats.get('profit', 0):.2f}")
                logger.info(f"  Balance: ${stats.get('balance', 0):.2f}")

        logger.info(f"\nTOTAL ACROSS ALL ACCOUNTS:")
        logger.info(f"  Total Trades: {total_trades}")
        logger.info(f"  Total Profit: ${total_profit:.2f}")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    logger.info("MT5 Multi-Account Trader Starting...")

    trader = MT5MultiAccountTrader()

    try:
        trader.start_trading()
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal")
        trader.stop_trading()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        trader.stop_trading()


if __name__ == "__main__":
    main()
