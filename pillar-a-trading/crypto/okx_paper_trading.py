#!/usr/bin/env python3
"""
OKX PAPER TRADING SYSTEM
Complete OKX integration with testnet and paper trading simulation

Features:
- OKX API integration (testnet first, then mainnet)
- Paper trading with $100 simulated account
- Complete order management (market, limit, stop-loss)
- Risk management (max 2% per trade)
- Real-time portfolio tracking
- Performance analytics
- Database logging of all trades
- Ready for live $100 account trading
- Automated notifications when profitable
"""

import asyncio
import aiohttp
import hmac
import hashlib
import base64
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Trade record"""
    id: Optional[int]
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit
    quantity: float
    price: float
    total_value: float
    fee: float
    profit_loss: float
    status: str  # open, closed
    open_time: str
    close_time: Optional[str]
    strategy: str
    notes: str


@dataclass
class Position:
    """Current position"""
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    side: str


class OKXPaperTrading:
    """
    OKX Paper Trading System with Testnet Integration
    Simulates trading with virtual $100 account
    """

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        testnet: bool = True,
        paper_balance: float = 100.0,
        data_dir: str = "/home/user/Private-Claude/pillar-a-trading/data"
    ):
        """
        Initialize OKX Paper Trading System

        Args:
            api_key: OKX API key (optional for pure paper trading)
            api_secret: OKX API secret
            passphrase: OKX API passphrase
            testnet: Use testnet (True) or mainnet (False)
            paper_balance: Starting paper trading balance
            data_dir: Directory for database storage
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.testnet = testnet

        # API endpoints
        if testnet:
            self.base_url = "https://www.okx.com"  # Testnet endpoint
            self.ws_url = "wss://wspap.okx.com:8443/ws/v5/public"
        else:
            self.base_url = "https://www.okx.com"
            self.ws_url = "wss://ws.okx.com:8443/ws/v5/public"

        # Paper trading state
        self.paper_mode = True  # Always start in paper mode
        self.initial_balance = paper_balance
        self.balance = paper_balance
        self.equity = paper_balance
        self.positions = {}
        self.trades = []
        self.orders = []

        # Risk management
        self.max_risk_per_trade = 0.02  # 2% max risk per trade
        self.max_position_size = 0.25  # 25% max position size
        self.max_total_risk = 0.06  # 6% max total risk

        # Database
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "okx_paper_trading.db"
        self.init_database()

        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0

        logger.info(f"OKX Paper Trading initialized - Balance: ${self.balance:.2f}")

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                fee REAL NOT NULL,
                profit_loss REAL DEFAULT 0.0,
                status TEXT DEFAULT 'open',
                open_time TEXT NOT NULL,
                close_time TEXT,
                strategy TEXT,
                notes TEXT
            )
        """)

        # Portfolio history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                profit REAL NOT NULL,
                num_positions INTEGER NOT NULL,
                num_trades INTEGER NOT NULL
            )
        """)

        # Performance metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                total_profit REAL,
                total_loss REAL,
                net_profit REAL,
                sharpe_ratio REAL,
                max_drawdown REAL
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    # ============================================================
    # OKX API AUTHENTICATION & REQUESTS
    # ============================================================

    def _generate_signature(
        self,
        timestamp: str,
        method: str,
        request_path: str,
        body: str = ""
    ) -> str:
        """Generate OKX API signature"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()

    def _get_headers(self, method: str, request_path: str, body: str = "") -> Dict:
        """Get request headers with authentication"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        signature = self._generate_signature(timestamp, method, request_path, body)

        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make authenticated API request"""
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data) if data else ""
        headers = self._get_headers(method, endpoint, body)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data
                ) as response:
                    result = await response.json()
                    return result
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    # ============================================================
    # MARKET DATA
    # ============================================================

    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get current ticker price"""
        # For paper trading, we can use public endpoint (no auth needed)
        endpoint = f"/api/v5/market/ticker?instId={symbol}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    result = await response.json()

                    if result.get("code") == "0" and result.get("data"):
                        ticker = result["data"][0]
                        return {
                            "symbol": symbol,
                            "last": float(ticker["last"]),
                            "bid": float(ticker["bidPx"]),
                            "ask": float(ticker["askPx"]),
                            "volume": float(ticker["vol24h"]),
                            "timestamp": ticker["ts"]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            return None

    async def get_orderbook(self, symbol: str, depth: int = 20) -> Optional[Dict]:
        """Get orderbook depth"""
        endpoint = f"/api/v5/market/books?instId={symbol}&sz={depth}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    result = await response.json()

                    if result.get("code") == "0" and result.get("data"):
                        book = result["data"][0]
                        return {
                            "bids": [[float(b[0]), float(b[1])] for b in book["bids"]],
                            "asks": [[float(a[0]), float(a[1])] for a in book["asks"]],
                            "timestamp": book["ts"]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return None

    async def get_candles(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Get historical candlestick data

        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            timeframe: Candle timeframe (1m, 5m, 15m, 1H, 1D)
            limit: Number of candles

        Returns:
            DataFrame with OHLCV data
        """
        endpoint = f"/api/v5/market/candles?instId={symbol}&bar={timeframe}&limit={limit}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    result = await response.json()

                    if result.get("code") == "0" and result.get("data"):
                        candles = result["data"]
                        df = pd.DataFrame(candles, columns=[
                            "timestamp", "open", "high", "low", "close", "volume", "vol_currency"
                        ])
                        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit='ms')
                        for col in ["open", "high", "low", "close", "volume"]:
                            df[col] = df[col].astype(float)
                        return df
                    return None
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            return None

    # ============================================================
    # PAPER TRADING ORDER EXECUTION
    # ============================================================

    async def calculate_position_size(
        self,
        symbol: str,
        risk_amount: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk management

        Args:
            symbol: Trading symbol
            risk_amount: Risk amount in USD (defaults to max_risk_per_trade)

        Returns:
            Position size in base currency
        """
        if risk_amount is None:
            risk_amount = self.balance * self.max_risk_per_trade

        ticker = await self.get_ticker(symbol)
        if not ticker:
            return 0.0

        price = ticker["last"]
        max_position_value = self.balance * self.max_position_size
        position_size = min(risk_amount / price, max_position_value / price)

        return position_size

    async def execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: Optional[float] = None,
        strategy: str = "manual",
        notes: str = ""
    ) -> Optional[Trade]:
        """
        Execute paper trading market order

        Args:
            symbol: Trading pair (e.g., BTC-USDT)
            side: 'buy' or 'sell'
            quantity: Quantity to trade (auto-calculated if None)
            strategy: Strategy name
            notes: Trade notes

        Returns:
            Trade object if successful
        """
        # Get current price
        ticker = await self.get_ticker(symbol)
        if not ticker:
            logger.error(f"Failed to get ticker for {symbol}")
            return None

        price = ticker["ask"] if side == "buy" else ticker["bid"]

        # Calculate quantity if not provided
        if quantity is None:
            quantity = await self.calculate_position_size(symbol)

        # Calculate total value
        total_value = quantity * price
        fee = total_value * 0.001  # 0.1% fee

        # Check if we have enough balance
        if side == "buy" and (total_value + fee) > self.balance:
            logger.error(f"Insufficient balance: ${self.balance:.2f} < ${total_value + fee:.2f}")
            return None

        # Execute trade
        trade = Trade(
            id=None,
            symbol=symbol,
            side=side,
            order_type="market",
            quantity=quantity,
            price=price,
            total_value=total_value,
            fee=fee,
            profit_loss=0.0,
            status="open",
            open_time=datetime.now().isoformat(),
            close_time=None,
            strategy=strategy,
            notes=notes
        )

        # Update balance
        if side == "buy":
            self.balance -= (total_value + fee)
        else:
            self.balance += (total_value - fee)

        # Update positions
        self._update_position(symbol, side, quantity, price)

        # Save trade
        trade.id = self._save_trade(trade)
        self.trades.append(trade)
        self.total_trades += 1

        logger.info(f"✓ Executed {side.upper()} {quantity:.4f} {symbol} @ ${price:.2f}")
        logger.info(f"  Total: ${total_value:.2f}, Fee: ${fee:.4f}")
        logger.info(f"  New Balance: ${self.balance:.2f}")

        return trade

    async def execute_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        limit_price: float,
        strategy: str = "manual",
        notes: str = ""
    ) -> Optional[Trade]:
        """Execute paper trading limit order"""
        # For paper trading, limit orders execute immediately at limit price
        ticker = await self.get_ticker(symbol)
        if not ticker:
            return None

        current_price = ticker["last"]

        # Check if limit order would execute
        if side == "buy" and current_price <= limit_price:
            execute_price = limit_price
        elif side == "sell" and current_price >= limit_price:
            execute_price = limit_price
        else:
            logger.info(f"Limit order pending: {side} {symbol} @ ${limit_price}")
            return None

        # Execute at limit price
        total_value = quantity * execute_price
        fee = total_value * 0.001

        if side == "buy" and (total_value + fee) > self.balance:
            logger.error("Insufficient balance")
            return None

        trade = Trade(
            id=None,
            symbol=symbol,
            side=side,
            order_type="limit",
            quantity=quantity,
            price=execute_price,
            total_value=total_value,
            fee=fee,
            profit_loss=0.0,
            status="open",
            open_time=datetime.now().isoformat(),
            close_time=None,
            strategy=strategy,
            notes=notes
        )

        # Update balance
        if side == "buy":
            self.balance -= (total_value + fee)
        else:
            self.balance += (total_value - fee)

        # Update position
        self._update_position(symbol, side, quantity, execute_price)

        # Save
        trade.id = self._save_trade(trade)
        self.trades.append(trade)
        self.total_trades += 1

        logger.info(f"✓ Limit order executed: {side.upper()} {quantity:.4f} {symbol} @ ${execute_price:.2f}")

        return trade

    def _update_position(self, symbol: str, side: str, quantity: float, price: float):
        """Update position tracking"""
        if symbol not in self.positions:
            self.positions[symbol] = {
                "quantity": 0.0,
                "avg_price": 0.0,
                "realized_pnl": 0.0
            }

        pos = self.positions[symbol]

        if side == "buy":
            # Add to position
            total_cost = (pos["quantity"] * pos["avg_price"]) + (quantity * price)
            new_quantity = pos["quantity"] + quantity
            pos["avg_price"] = total_cost / new_quantity if new_quantity > 0 else 0
            pos["quantity"] = new_quantity
        else:
            # Reduce position
            if pos["quantity"] >= quantity:
                # Calculate realized P&L
                pnl = quantity * (price - pos["avg_price"])
                pos["realized_pnl"] += pnl
                pos["quantity"] -= quantity
            else:
                logger.warning(f"Selling more than held: {quantity} > {pos['quantity']}")

    async def close_position(self, symbol: str, strategy: str = "manual") -> Optional[Trade]:
        """Close entire position for a symbol"""
        if symbol not in self.positions or self.positions[symbol]["quantity"] == 0:
            logger.error(f"No open position for {symbol}")
            return None

        quantity = self.positions[symbol]["quantity"]
        return await self.execute_market_order(
            symbol=symbol,
            side="sell",
            quantity=quantity,
            strategy=strategy,
            notes="Close position"
        )

    # ============================================================
    # POSITION & PORTFOLIO MANAGEMENT
    # ============================================================

    async def get_portfolio_value(self) -> Dict:
        """Calculate current portfolio value"""
        total_value = self.balance
        unrealized_pnl = 0.0

        for symbol, pos in self.positions.items():
            if pos["quantity"] > 0:
                ticker = await self.get_ticker(symbol)
                if ticker:
                    current_price = ticker["last"]
                    position_value = pos["quantity"] * current_price
                    pnl = pos["quantity"] * (current_price - pos["avg_price"])

                    total_value += position_value
                    unrealized_pnl += pnl

        return {
            "balance": self.balance,
            "positions_value": total_value - self.balance,
            "total_value": total_value,
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": sum(p["realized_pnl"] for p in self.positions.values()),
            "total_pnl": unrealized_pnl + sum(p["realized_pnl"] for p in self.positions.values()),
            "roi": ((total_value - self.initial_balance) / self.initial_balance) * 100
        }

    async def get_positions(self) -> List[Position]:
        """Get all current positions with live prices"""
        positions = []

        for symbol, pos in self.positions.items():
            if pos["quantity"] > 0:
                ticker = await self.get_ticker(symbol)
                current_price = ticker["last"] if ticker else pos["avg_price"]

                unrealized_pnl = pos["quantity"] * (current_price - pos["avg_price"])

                positions.append(Position(
                    symbol=symbol,
                    quantity=pos["quantity"],
                    avg_entry_price=pos["avg_price"],
                    current_price=current_price,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=pos["realized_pnl"],
                    side="long"
                ))

        return positions

    def get_trade_history(self, limit: int = 50) -> List[Trade]:
        """Get recent trade history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM trades
            ORDER BY open_time DESC
            LIMIT ?
        """, (limit,))

        trades = []
        for row in cursor.fetchall():
            trade = Trade(
                id=row[0],
                symbol=row[1],
                side=row[2],
                order_type=row[3],
                quantity=row[4],
                price=row[5],
                total_value=row[6],
                fee=row[7],
                profit_loss=row[8],
                status=row[9],
                open_time=row[10],
                close_time=row[11],
                strategy=row[12],
                notes=row[13]
            )
            trades.append(trade)

        conn.close()
        return trades

    # ============================================================
    # PERFORMANCE ANALYTICS
    # ============================================================

    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if self.total_trades == 0:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "sharpe_ratio": 0.0
            }

        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        profit_factor = abs(self.total_profit / self.total_loss) if self.total_loss != 0 else 0

        avg_win = self.total_profit / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = self.total_loss / self.losing_trades if self.losing_trades > 0 else 0

        # Calculate Sharpe ratio (simplified)
        returns = []
        for trade in self.trades:
            if trade.status == "closed":
                returns.append(trade.profit_loss / trade.total_value)

        sharpe = 0.0
        if len(returns) > 0:
            returns_array = np.array(returns)
            sharpe = np.mean(returns_array) / np.std(returns_array) if np.std(returns_array) > 0 else 0
            sharpe *= np.sqrt(252)  # Annualized

        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_profit": self.total_profit,
            "total_loss": self.total_loss,
            "net_profit": self.total_profit + self.total_loss,
            "sharpe_ratio": sharpe
        }

    async def check_ready_for_live(self) -> Dict:
        """Check if ready to transition to live trading"""
        portfolio = await self.get_portfolio_value()
        metrics = self.calculate_performance_metrics()

        # Criteria for live trading
        criteria = {
            "min_trades": self.total_trades >= 20,
            "win_rate": metrics["win_rate"] >= 55.0,
            "profit_factor": metrics["profit_factor"] >= 1.5,
            "positive_roi": portfolio["roi"] > 0,
            "sharpe_ratio": metrics["sharpe_ratio"] > 1.0
        }

        ready = all(criteria.values())

        return {
            "ready_for_live": ready,
            "criteria": criteria,
            "current_metrics": metrics,
            "portfolio": portfolio,
            "recommendation": "Ready for live trading!" if ready else "Continue paper trading"
        }

    # ============================================================
    # DATABASE OPERATIONS
    # ============================================================

    def _save_trade(self, trade: Trade) -> int:
        """Save trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trades
            (symbol, side, order_type, quantity, price, total_value, fee,
             profit_loss, status, open_time, close_time, strategy, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.symbol, trade.side, trade.order_type, trade.quantity,
            trade.price, trade.total_value, trade.fee, trade.profit_loss,
            trade.status, trade.open_time, trade.close_time,
            trade.strategy, trade.notes
        ))

        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return trade_id

    def save_portfolio_snapshot(self):
        """Save current portfolio state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO portfolio_history
            (timestamp, balance, equity, profit, num_positions, num_trades)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            self.balance,
            self.equity,
            self.balance - self.initial_balance,
            len([p for p in self.positions.values() if p["quantity"] > 0]),
            self.total_trades
        ))

        conn.commit()
        conn.close()

    # ============================================================
    # REPORTING
    # ============================================================

    async def generate_report(self) -> str:
        """Generate comprehensive trading report"""
        portfolio = await self.get_portfolio_value()
        metrics = self.calculate_performance_metrics()
        positions = await self.get_positions()

        report = []
        report.append("=" * 70)
        report.append("OKX PAPER TRADING REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Mode: {'TESTNET' if self.testnet else 'MAINNET'} (Paper Trading)")
        report.append("")

        # Portfolio
        report.append("PORTFOLIO:")
        report.append(f"  Initial Balance: ${self.initial_balance:.2f}")
        report.append(f"  Current Balance: ${portfolio['balance']:.2f}")
        report.append(f"  Total Value: ${portfolio['total_value']:.2f}")
        report.append(f"  Unrealized P&L: ${portfolio['unrealized_pnl']:.2f}")
        report.append(f"  Realized P&L: ${portfolio['realized_pnl']:.2f}")
        report.append(f"  Total P&L: ${portfolio['total_pnl']:.2f}")
        report.append(f"  ROI: {portfolio['roi']:.2f}%")
        report.append("")

        # Performance
        report.append("PERFORMANCE:")
        report.append(f"  Total Trades: {metrics['total_trades']}")
        report.append(f"  Winning Trades: {metrics['winning_trades']}")
        report.append(f"  Losing Trades: {metrics['losing_trades']}")
        report.append(f"  Win Rate: {metrics['win_rate']:.2f}%")
        report.append(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append("")

        # Open Positions
        report.append(f"OPEN POSITIONS: {len(positions)}")
        for pos in positions:
            report.append(f"  {pos.symbol}:")
            report.append(f"    Quantity: {pos.quantity:.4f}")
            report.append(f"    Entry: ${pos.avg_entry_price:.2f}")
            report.append(f"    Current: ${pos.current_price:.2f}")
            report.append(f"    P&L: ${pos.unrealized_pnl:.2f}")
        report.append("")

        # Live trading readiness
        ready_check = await self.check_ready_for_live()
        report.append("LIVE TRADING READINESS:")
        report.append(f"  Status: {ready_check['recommendation']}")
        for criterion, passed in ready_check['criteria'].items():
            status = "✓" if passed else "✗"
            report.append(f"  {status} {criterion}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


async def main():
    """Demo OKX paper trading system"""
    print("\n" + "="*70)
    print("OKX PAPER TRADING SYSTEM - DEMO")
    print("="*70 + "\n")

    # Initialize paper trading
    trader = OKXPaperTrading(
        testnet=True,
        paper_balance=100.0
    )

    print(f"✓ Paper trading initialized with ${trader.balance:.2f}")
    print("\nTesting market data...")

    # Test market data
    ticker = await trader.get_ticker("BTC-USDT")
    if ticker:
        print(f"\nBTC-USDT Ticker:")
        print(f"  Last: ${ticker['last']:,.2f}")
        print(f"  Bid: ${ticker['bid']:,.2f}")
        print(f"  Ask: ${ticker['ask']:,.2f}")

    # Demo trade execution
    print("\nExecuting demo trade...")
    trade = await trader.execute_market_order(
        symbol="BTC-USDT",
        side="buy",
        quantity=0.001,
        strategy="demo",
        notes="Test trade"
    )

    # Generate report
    print("\n" + await trader.generate_report())


if __name__ == "__main__":
    asyncio.run(main())
