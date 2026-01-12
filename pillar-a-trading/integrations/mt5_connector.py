#!/usr/bin/env python3
"""
MetaTrader 5 (MT5) Integration
Connects Agent X2.0 trading system to MT5 platform
Supports both demo and live accounts
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MT5Connector')


class MT5Connector:
    """
    MetaTrader 5 Platform Connector

    NOTE: Requires MetaTrader5 Python library
    Install with: pip install MetaTrader5
    """

    def __init__(self, account_type: str = "demo"):
        """
        Initialize MT5 connector

        Args:
            account_type: "demo" or "live"
        """
        self.account_type = account_type
        self.connected = False
        self.mt5 = None
        self.account_info = {}

        # Load credentials
        self.login = int(os.getenv('MT5_LOGIN', '0'))
        self.password = os.getenv('MT5_PASSWORD', '')
        self.server = os.getenv('MT5_SERVER', 'Demo-Server')

        logger.info(f"✅ MT5Connector initialized for {account_type.upper()} account")

    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            # Try to import MT5 library
            try:
                import MetaTrader5 as mt5
                self.mt5 = mt5
            except ImportError:
                logger.error("❌ MetaTrader5 library not installed")
                logger.info("   Install with: pip install MetaTrader5")
                return False

            # Initialize MT5
            if not self.mt5.initialize():
                logger.error(f"❌ MT5 initialization failed: {self.mt5.last_error()}")
                return False

            # Login
            if self.login and self.password:
                authorized = self.mt5.login(self.login, password=self.password, server=self.server)

                if not authorized:
                    logger.error(f"❌ MT5 login failed: {self.mt5.last_error()}")
                    self.mt5.shutdown()
                    return False

                self.connected = True
                self.account_info = self._get_account_info()

                logger.info(f"✅ Connected to MT5 - {self.account_type.upper()}")
                logger.info(f"   Account: {self.account_info.get('login', 'N/A')}")
                logger.info(f"   Server: {self.account_info.get('server', 'N/A')}")
                logger.info(f"   Balance: ${self.account_info.get('balance', 0):,.2f}")
                logger.info(f"   Equity: ${self.account_info.get('equity', 0):,.2f}")

                return True
            else:
                logger.warning("⚠️  MT5 credentials not configured")
                logger.info("   Set MT5_LOGIN, MT5_PASSWORD, MT5_SERVER in .env file")
                return False

        except Exception as e:
            logger.error(f"❌ MT5 connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from MT5"""
        if self.mt5:
            self.mt5.shutdown()
            self.connected = False
            logger.info("🔌 Disconnected from MT5")

    def _get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.connected or not self.mt5:
            return {}

        account = self.mt5.account_info()
        if account is None:
            return {}

        return {
            'login': account.login,
            'server': account.server,
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'margin_free': account.margin_free,
            'margin_level': account.margin_level,
            'profit': account.profit,
            'currency': account.currency,
            'leverage': account.leverage,
            'trade_mode': account.trade_mode,
            'limit_orders': account.limit_orders,
            'margin_so_call': account.margin_so_call,
            'margin_so_so': account.margin_so_so
        }

    def get_symbols(self, filter_str: str = "*") -> List[str]:
        """Get available trading symbols"""
        if not self.connected or not self.mt5:
            return []

        symbols = self.mt5.symbols_get(filter_str)
        if symbols is None:
            return []

        return [s.name for s in symbols]

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get information about a specific symbol"""
        if not self.connected or not self.mt5:
            return None

        info = self.mt5.symbol_info(symbol)
        if info is None:
            return None

        return {
            'name': info.name,
            'description': info.description,
            'currency_base': info.currency_base,
            'currency_profit': info.currency_profit,
            'currency_margin': info.currency_margin,
            'digits': info.digits,
            'trade_contract_size': info.trade_contract_size,
            'trade_mode': info.trade_mode,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step,
            'spread': info.spread,
            'bid': info.bid,
            'ask': info.ask
        }

    def get_market_data(self, symbol: str, timeframe: str = "H1", bars: int = 100) -> Optional[List[Dict]]:
        """
        Get historical market data

        Args:
            symbol: Trading symbol (e.g., "EURUSD", "BTCUSD")
            timeframe: Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN1)
            bars: Number of bars to retrieve
        """
        if not self.connected or not self.mt5:
            return None

        # Map timeframe string to MT5 constant
        timeframe_map = {
            'M1': self.mt5.TIMEFRAME_M1,
            'M5': self.mt5.TIMEFRAME_M5,
            'M15': self.mt5.TIMEFRAME_M15,
            'M30': self.mt5.TIMEFRAME_M30,
            'H1': self.mt5.TIMEFRAME_H1,
            'H4': self.mt5.TIMEFRAME_H4,
            'D1': self.mt5.TIMEFRAME_D1,
            'W1': self.mt5.TIMEFRAME_W1,
            'MN1': self.mt5.TIMEFRAME_MN1
        }

        tf = timeframe_map.get(timeframe, self.mt5.TIMEFRAME_H1)

        rates = self.mt5.copy_rates_from_pos(symbol, tf, 0, bars)
        if rates is None:
            logger.error(f"Failed to get data for {symbol}")
            return None

        candles = []
        for rate in rates:
            candles.append({
                'time': datetime.fromtimestamp(rate['time']).isoformat(),
                'open': rate['open'],
                'high': rate['high'],
                'low': rate['low'],
                'close': rate['close'],
                'volume': rate['tick_volume']
            })

        return candles

    def place_order(self, symbol: str, order_type: str, volume: float,
                    price: float = None, sl: float = None, tp: float = None,
                    comment: str = "Agent X2.0") -> Optional[Dict]:
        """
        Place a trading order

        Args:
            symbol: Trading symbol
            order_type: "BUY" or "SELL"
            volume: Lot size
            price: Limit price (None for market order)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
        """
        if not self.connected or not self.mt5:
            logger.warning("⚠️  Not connected to MT5")
            return None

        # Get symbol info
        symbol_info = self.mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"❌ Symbol {symbol} not found")
            return None

        # Prepare request
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": self.mt5.ORDER_TYPE_BUY if order_type == "BUY" else self.mt5.ORDER_TYPE_SELL,
            "price": price if price else (symbol_info.ask if order_type == "BUY" else symbol_info.bid),
            "sl": sl if sl else 0.0,
            "tp": tp if tp else 0.0,
            "deviation": 20,
            "magic": 202412,
            "comment": comment,
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = self.mt5.order_send(request)

        if result is None:
            logger.error(f"❌ Order failed: {self.mt5.last_error()}")
            return None

        if result.retcode != self.mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Order rejected: {result.retcode} - {result.comment}")
            return None

        logger.info(f"✅ Order executed: {order_type} {volume} {symbol} @ {result.price}")

        return {
            'ticket': result.order,
            'symbol': symbol,
            'order_type': order_type,
            'volume': volume,
            'price': result.price,
            'comment': comment,
            'time': datetime.now().isoformat()
        }

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.connected or not self.mt5:
            return []

        positions = self.mt5.positions_get()
        if positions is None:
            return []

        result = []
        for pos in positions:
            result.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == 0 else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'sl': pos.sl,
                'tp': pos.tp,
                'time': datetime.fromtimestamp(pos.time).isoformat(),
                'comment': pos.comment
            })

        return result

    def close_position(self, ticket: int) -> bool:
        """Close an open position by ticket"""
        if not self.connected or not self.mt5:
            return False

        position = self.mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            logger.error(f"❌ Position {ticket} not found")
            return False

        pos = position[0]

        # Prepare close request
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": self.mt5.ORDER_TYPE_SELL if pos.type == 0 else self.mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": self.mt5.symbol_info_tick(pos.symbol).bid if pos.type == 0 else self.mt5.symbol_info_tick(pos.symbol).ask,
            "deviation": 20,
            "magic": 202412,
            "comment": "Close by Agent X2.0",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }

        result = self.mt5.order_send(request)

        if result.retcode != self.mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Failed to close position: {result.comment}")
            return False

        logger.info(f"✅ Closed position #{ticket} with profit: ${pos.profit:.2f}")
        return True

    def get_trading_history(self, days: int = 7) -> List[Dict]:
        """Get trading history for the last N days"""
        if not self.connected or not self.mt5:
            return []

        from datetime import timedelta

        date_to = datetime.now()
        date_from = date_to - timedelta(days=days)

        deals = self.mt5.history_deals_get(date_from, date_to)
        if deals is None:
            return []

        result = []
        for deal in deals:
            result.append({
                'ticket': deal.ticket,
                'order': deal.order,
                'symbol': deal.symbol,
                'type': 'BUY' if deal.type == 0 else 'SELL',
                'volume': deal.volume,
                'price': deal.price,
                'profit': deal.profit,
                'commission': deal.commission,
                'swap': deal.swap,
                'time': datetime.fromtimestamp(deal.time).isoformat(),
                'comment': deal.comment
            })

        return result


class MT5TradingBot:
    """Trading bot that integrates Agent X2.0 with MT5"""

    def __init__(self, account_type: str = "demo"):
        self.connector = MT5Connector(account_type)
        self.active = False

    def start(self):
        """Start the MT5 trading bot"""
        logger.info("=" * 70)
        logger.info("🚀 STARTING MT5 TRADING BOT")
        logger.info("=" * 70)

        # Connect to MT5
        if self.connector.connect():
            self.active = True
            logger.info("✅ MT5 Trading Bot is ACTIVE")
            logger.info("=" * 70)

            # Show account status
            self.show_account_status()

            return True
        else:
            logger.error("❌ Failed to start MT5 Trading Bot")
            logger.info("   Please configure MT5 credentials in .env file:")
            logger.info("   MT5_LOGIN=your_account_number")
            logger.info("   MT5_PASSWORD=your_password")
            logger.info("   MT5_SERVER=your_broker_server")
            return False

    def show_account_status(self):
        """Display account status"""
        info = self.connector.account_info
        positions = self.connector.get_open_positions()

        print("\n📊 ACCOUNT STATUS")
        print("=" * 70)
        print(f"Account: {info.get('login', 'N/A')}")
        print(f"Server: {info.get('server', 'N/A')}")
        print(f"Balance: ${info.get('balance', 0):,.2f}")
        print(f"Equity: ${info.get('equity', 0):,.2f}")
        print(f"Profit: ${info.get('profit', 0):,.2f}")
        print(f"Open Positions: {len(positions)}")
        print("=" * 70)

        if positions:
            print("\n💼 OPEN POSITIONS")
            print("=" * 70)
            for pos in positions:
                print(f"#{pos['ticket']} - {pos['type']} {pos['volume']} {pos['symbol']} @ {pos['price_open']}")
                print(f"  Current: {pos['price_current']} | P/L: ${pos['profit']:.2f}")

    def stop(self):
        """Stop the MT5 trading bot"""
        self.active = False
        self.connector.disconnect()
        logger.info("🛑 MT5 Trading Bot stopped")


def main():
    """Main entry point - demo of MT5 integration"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║              METATRADER 5 (MT5) INTEGRATION                       ║
    ║            Connect Agent X2.0 to MT5 Platform                     ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Try demo account first
    bot = MT5TradingBot(account_type="demo")

    if bot.start():
        print("\n✅ MT5 Integration ready!")
        print("\nAvailable symbols:")

        # Show some popular symbols
        for symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'XAUUSD'][:5]:
            info = bot.connector.get_symbol_info(symbol)
            if info:
                print(f"  • {symbol}: Bid={info['bid']:.5f}, Ask={info['ask']:.5f}, Spread={info['spread']}")

        bot.stop()
    else:
        print("\n⚠️  MT5 not configured")
        print("\nTo connect your MT5 account, add to config/.env:")
        print("  MT5_LOGIN=your_account_number")
        print("  MT5_PASSWORD=your_password")
        print("  MT5_SERVER=your_broker_server")


if __name__ == "__main__":
    main()
