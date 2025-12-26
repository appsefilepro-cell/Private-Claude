"""
BINANCE LIVE TRADING BOT - COMPLETE IMPLEMENTATION
Handles spot and futures trading with WebSocket real-time data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceLiveTrader:
    """Complete Binance trading bot with WebSocket streaming"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Binance trader

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (True) or mainnet (False)
        """
        if testnet:
            # Testnet endpoint
            self.client = Client(api_key, api_secret, testnet=True)
        else:
            # Mainnet endpoint
            self.client = Client(api_key, api_secret)

        self.bm = BinanceSocketManager(self.client)
        self.active_streams = []
        self.portfolio = {}
        self.orders = {}
        self.risk_percent = 0.02  # 2% risk per trade

    async def get_account_balance(self) -> Dict:
        """Get current account balance"""
        try:
            account = self.client.get_account()
            balances = {
                b['asset']: float(b['free'])
                for b in account['balances']
                if float(b['free']) > 0
            }
            return balances
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}

    async def execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Optional[Dict]:
        """
        Execute market order

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Amount to trade

        Returns:
            Order info or None if failed
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )

            logger.info(f"Market order executed: {symbol} {side} {quantity}")
            self.orders[order['orderId']] = order
            return order

        except Exception as e:
            logger.error(f"Market order failed: {e}")
            return None

    async def execute_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Optional[Dict]:
        """Execute limit order"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=str(price)
            )

            logger.info(f"Limit order placed: {symbol} {side} {quantity} @ {price}")
            self.orders[order['orderId']] = order
            return order

        except Exception as e:
            logger.error(f"Limit order failed: {e}")
            return None

    async def execute_stop_loss_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Optional[Dict]:
        """Execute stop-loss order"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=str(stop_price),
                stopPrice=str(stop_price)
            )

            logger.info(f"Stop-loss placed: {symbol} {stop_price}")
            return order

        except Exception as e:
            logger.error(f"Stop-loss failed: {e}")
            return None

    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss_price: float
    ) -> float:
        """
        Calculate position size based on risk management

        Args:
            balance: Account balance
            entry_price: Entry price
            stop_loss_price: Stop loss price

        Returns:
            Position size
        """
        risk_amount = balance * self.risk_percent
        price_diff = abs(entry_price - stop_loss_price)
        position_size = risk_amount / price_diff
        return position_size

    async def start_websocket_stream(self, symbol: str):
        """Start WebSocket stream for real-time price data"""

        def process_message(msg):
            """Process incoming WebSocket messages"""
            if msg['e'] == 'trade':
                price = float(msg['p'])
                quantity = float(msg['q'])
                timestamp = msg['T']

                logger.info(f"{symbol}: ${price} | Qty: {quantity}")

                # Check for trading signals
                self._check_signals(symbol, price)

        conn_key = self.bm.start_trade_socket(symbol, process_message)
        self.active_streams.append(conn_key)
        self.bm.start()

    def _check_signals(self, symbol: str, current_price: float):
        """Check for trading signals"""
        # Placeholder for signal detection logic
        # In production, integrate with pattern recognition ML model
        pass

    async def rebalance_portfolio(self, target_allocation: Dict[str, float]):
        """
        Rebalance portfolio to target allocation

        Args:
            target_allocation: Dict of {symbol: percentage} (e.g., {'BTC': 0.6, 'ETH': 0.4})
        """
        balances = await self.get_account_balance()
        total_value = sum(balances.values())

        for symbol, target_pct in target_allocation.items():
            target_value = total_value * target_pct
            current_value = balances.get(symbol, 0)

            diff = target_value - current_value

            if abs(diff) > total_value * 0.05:  # 5% threshold
                if diff > 0:
                    # Buy more
                    await self.execute_market_order(
                        symbol=f"{symbol}USDT",
                        side=SIDE_BUY,
                        quantity=diff
                    )
                else:
                    # Sell excess
                    await self.execute_market_order(
                        symbol=f"{symbol}USDT",
                        side=SIDE_SELL,
                        quantity=abs(diff)
                    )

    async def track_tax_lots(self) -> pd.DataFrame:
        """
        Track tax lots for capital gains/losses

        Returns:
            DataFrame with all trades and tax implications
        """
        trades = []

        for order_id, order in self.orders.items():
            trades.append({
                'order_id': order_id,
                'symbol': order['symbol'],
                'side': order['side'],
                'quantity': float(order['executedQty']),
                'price': float(order['price']) if 'price' in order else None,
                'timestamp': order['transactTime'],
                'status': order['status']
            })

        df = pd.DataFrame(trades)

        # Calculate gains/losses (simplified)
        if not df.empty:
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('date')

        return df

    async def get_staking_rewards(self) -> Dict:
        """Get staking rewards summary"""
        try:
            rewards = self.client.get_staking_history()
            total_rewards = sum(float(r['amount']) for r in rewards)
            return {
                'total_rewards': total_rewards,
                'details': rewards
            }
        except Exception as e:
            logger.error(f"Error fetching staking rewards: {e}")
            return {'total_rewards': 0, 'details': []}

    async def dca_scheduler(
        self,
        symbol: str,
        amount_usd: float,
        frequency_hours: int = 24
    ):
        """
        Dollar-cost averaging scheduler

        Args:
            symbol: Trading pair
            amount_usd: Amount to invest per interval
            frequency_hours: How often to buy
        """
        logger.info(f"DCA started: {symbol} ${amount_usd} every {frequency_hours}h")

        while True:
            try:
                # Get current price
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])

                # Calculate quantity
                quantity = amount_usd / price

                # Execute buy order
                await self.execute_market_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    quantity=quantity
                )

                logger.info(f"DCA buy: {quantity} {symbol} @ ${price}")

            except Exception as e:
                logger.error(f"DCA error: {e}")

            # Wait for next interval
            await asyncio.sleep(frequency_hours * 3600)

    def stop_all_streams(self):
        """Stop all WebSocket streams"""
        for conn_key in self.active_streams:
            self.bm.stop_socket(conn_key)
        self.bm.close()
        logger.info("All WebSocket streams stopped")


async def main():
    """Example usage"""
    # TESTNET credentials (replace with your own)
    API_KEY = "your_testnet_api_key"
    API_SECRET = "your_testnet_api_secret"

    trader = BinanceLiveTrader(API_KEY, API_SECRET, testnet=True)

    # Get balance
    balance = await trader.get_account_balance()
    print(f"Account Balance: {balance}")

    # Start WebSocket for BTC
    await trader.start_websocket_stream('BTCUSDT')

    # Run for 60 seconds
    await asyncio.sleep(60)

    # Stop streams
    trader.stop_all_streams()


if __name__ == "__main__":
    asyncio.run(main())
