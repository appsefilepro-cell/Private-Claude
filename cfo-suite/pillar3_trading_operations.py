#!/usr/bin/env python3
"""
PILLAR 3: TRADING OPERATIONS
Complete trading management including bot coordination, portfolio tracking, risk management, and analytics
Part of Agent 5.0 CFO Suite
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3


class TradingMode(Enum):
    """Trading mode"""
    PAPER = "paper"
    DEMO = "demo"
    LIVE = "live"


class TradeStatus(Enum):
    """Trade status"""
    PENDING = "pending"
    EXECUTED = "executed"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PositionStatus(Enum):
    """Position status"""
    OPEN = "open"
    CLOSED = "closed"
    PENDING_CLOSE = "pending_close"


class RiskLevel(Enum):
    """Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class Trade:
    """Trade record"""
    id: str
    bot_id: str
    symbol: str
    side: str  # buy/sell
    quantity: float
    entry_price: float
    exit_price: Optional[float]
    entry_time: str
    exit_time: Optional[str]
    status: str
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]
    fees: float
    strategy: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Position:
    """Position record"""
    id: str
    bot_id: str
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pl: float
    unrealized_pl_percent: float
    status: str
    opened_at: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class TradingBot:
    """Trading bot configuration"""
    id: str
    name: str
    mode: str
    strategy: str
    risk_profile: str
    status: str  # active, paused, stopped
    capital: float
    max_position_size: float
    max_daily_trades: int
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None


@dataclass
class RiskMetric:
    """Risk assessment metric"""
    id: str
    timestamp: str
    portfolio_value: float
    total_exposure: float
    max_drawdown: float
    sharpe_ratio: float
    var_95: float  # Value at Risk 95%
    risk_level: str
    alerts: List[str]


class TradingOperations:
    """
    Complete trading operations management system
    Handles bot coordination, portfolio tracking, risk management, and performance analytics
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize trading operations"""
        if data_dir is None:
            self.base_dir = Path(__file__).parent
            self.data_dir = self.base_dir / 'data' / 'trading'
        else:
            self.data_dir = data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / 'logs' / 'trading'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.logger = logging.getLogger('TradingOps')
        handler = logging.FileHandler(
            self.logs_dir / f'trading_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize database
        self.db_path = self.data_dir / 'trading.db'
        self.init_database()

        # Trading strategies
        self.strategies = {
            'momentum': 'Trend following with momentum indicators',
            'mean_reversion': 'Buy low, sell high based on statistical mean',
            'breakout': 'Trade on price breakouts from consolidation',
            'scalping': 'Quick trades for small profits',
            'swing': 'Hold positions for days/weeks',
            'arbitrage': 'Exploit price differences across markets'
        }

        # Risk profiles
        self.risk_profiles = {
            'conservative': {'max_position': 0.05, 'max_leverage': 1.0, 'stop_loss': 0.02},
            'moderate': {'max_position': 0.10, 'max_leverage': 2.0, 'stop_loss': 0.03},
            'aggressive': {'max_position': 0.20, 'max_leverage': 3.0, 'stop_loss': 0.05}
        }

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trading bots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mode TEXT NOT NULL,
                strategy TEXT NOT NULL,
                risk_profile TEXT NOT NULL,
                status TEXT NOT NULL,
                capital REAL NOT NULL,
                max_position_size REAL NOT NULL,
                max_daily_trades INTEGER NOT NULL,
                started_at TEXT,
                stopped_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                bot_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                status TEXT NOT NULL,
                profit_loss REAL,
                profit_loss_percent REAL,
                fees REAL DEFAULT 0,
                strategy TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES bots (id)
            )
        ''')

        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                bot_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                unrealized_pl REAL NOT NULL,
                unrealized_pl_percent REAL NOT NULL,
                status TEXT NOT NULL,
                opened_at TEXT NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES bots (id)
            )
        ''')

        # Risk metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                portfolio_value REAL NOT NULL,
                total_exposure REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                var_95 REAL NOT NULL,
                risk_level TEXT NOT NULL,
                alerts TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        self.logger.info("Trading database initialized successfully")

    # ==================== BOT MANAGEMENT ====================

    def register_bot(self, bot: TradingBot) -> str:
        """Register a new trading bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO bots
            (id, name, mode, strategy, risk_profile, status, capital,
             max_position_size, max_daily_trades, started_at, stopped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bot.id,
            bot.name,
            bot.mode,
            bot.strategy,
            bot.risk_profile,
            bot.status,
            bot.capital,
            bot.max_position_size,
            bot.max_daily_trades,
            bot.started_at,
            bot.stopped_at
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Bot registered: {bot.name} ({bot.id}) - {bot.strategy}")
        return bot.id

    def update_bot_status(self, bot_id: str, status: str) -> bool:
        """Update bot status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        if status == 'active':
            cursor.execute(
                "UPDATE bots SET status = ?, started_at = ? WHERE id = ?",
                (status, timestamp, bot_id)
            )
        elif status in ['paused', 'stopped']:
            cursor.execute(
                "UPDATE bots SET status = ?, stopped_at = ? WHERE id = ?",
                (status, timestamp, bot_id)
            )
        else:
            cursor.execute(
                "UPDATE bots SET status = ? WHERE id = ?",
                (status, bot_id)
            )

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Bot {bot_id} status updated to {status}")

        return updated

    def get_active_bots(self) -> List[TradingBot]:
        """Get all active bots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bots WHERE status = 'active'")
        rows = cursor.fetchall()
        conn.close()

        bots = []
        for row in rows:
            bots.append(TradingBot(
                id=row[0],
                name=row[1],
                mode=row[2],
                strategy=row[3],
                risk_profile=row[4],
                status=row[5],
                capital=row[6],
                max_position_size=row[7],
                max_daily_trades=row[8],
                started_at=row[9],
                stopped_at=row[10]
            ))

        return bots

    # ==================== TRADE MANAGEMENT ====================

    def record_trade(self, trade: Trade) -> str:
        """Record a trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO trades
            (id, bot_id, symbol, side, quantity, entry_price, exit_price,
             entry_time, exit_time, status, profit_loss, profit_loss_percent,
             fees, strategy, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.id,
            trade.bot_id,
            trade.symbol,
            trade.side,
            trade.quantity,
            trade.entry_price,
            trade.exit_price,
            trade.entry_time,
            trade.exit_time,
            trade.status,
            trade.profit_loss,
            trade.profit_loss_percent,
            trade.fees,
            trade.strategy,
            json.dumps(trade.metadata) if trade.metadata else None
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Trade recorded: {trade.symbol} {trade.side} @ {trade.entry_price}")
        return trade.id

    def get_bot_trades(self, bot_id: str, limit: int = 100) -> List[Trade]:
        """Get trades for a specific bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM trades WHERE bot_id = ? ORDER BY entry_time DESC LIMIT ?",
            (bot_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        trades = []
        for row in rows:
            trades.append(Trade(
                id=row[0],
                bot_id=row[1],
                symbol=row[2],
                side=row[3],
                quantity=row[4],
                entry_price=row[5],
                exit_price=row[6],
                entry_time=row[7],
                exit_time=row[8],
                status=row[9],
                profit_loss=row[10],
                profit_loss_percent=row[11],
                fees=row[12],
                strategy=row[13],
                metadata=json.loads(row[14]) if row[14] else None
            ))

        return trades

    # ==================== POSITION MANAGEMENT ====================

    def open_position(self, position: Position) -> str:
        """Open a new position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO positions
            (id, bot_id, symbol, quantity, entry_price, current_price,
             unrealized_pl, unrealized_pl_percent, status, opened_at,
             stop_loss, take_profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            position.id,
            position.bot_id,
            position.symbol,
            position.quantity,
            position.entry_price,
            position.current_price,
            position.unrealized_pl,
            position.unrealized_pl_percent,
            position.status,
            position.opened_at,
            position.stop_loss,
            position.take_profit
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Position opened: {position.symbol} - {position.quantity} @ {position.entry_price}")
        return position.id

    def update_position(self, position_id: str, current_price: float) -> bool:
        """Update position with current price"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get position details
        cursor.execute("SELECT entry_price, quantity FROM positions WHERE id = ?", (position_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False

        entry_price, quantity = row
        unrealized_pl = (current_price - entry_price) * quantity
        unrealized_pl_percent = ((current_price - entry_price) / entry_price) * 100

        cursor.execute('''
            UPDATE positions
            SET current_price = ?, unrealized_pl = ?, unrealized_pl_percent = ?
            WHERE id = ?
        ''', (current_price, unrealized_pl, unrealized_pl_percent, position_id))

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        return updated

    def get_open_positions(self, bot_id: Optional[str] = None) -> List[Position]:
        """Get all open positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if bot_id:
            cursor.execute(
                "SELECT * FROM positions WHERE status = 'open' AND bot_id = ?",
                (bot_id,)
            )
        else:
            cursor.execute("SELECT * FROM positions WHERE status = 'open'")

        rows = cursor.fetchall()
        conn.close()

        positions = []
        for row in rows:
            positions.append(Position(
                id=row[0],
                bot_id=row[1],
                symbol=row[2],
                quantity=row[3],
                entry_price=row[4],
                current_price=row[5],
                unrealized_pl=row[6],
                unrealized_pl_percent=row[7],
                status=row[8],
                opened_at=row[9],
                stop_loss=row[10],
                take_profit=row[11]
            ))

        return positions

    # ==================== RISK MANAGEMENT ====================

    def record_risk_metric(self, metric: RiskMetric) -> str:
        """Record risk assessment metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO risk_metrics
            (id, timestamp, portfolio_value, total_exposure, max_drawdown,
             sharpe_ratio, var_95, risk_level, alerts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.id,
            metric.timestamp,
            metric.portfolio_value,
            metric.total_exposure,
            metric.max_drawdown,
            metric.sharpe_ratio,
            metric.var_95,
            metric.risk_level,
            json.dumps(metric.alerts)
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Risk metric recorded: {metric.risk_level} - Portfolio: ${metric.portfolio_value:,.2f}")
        return metric.id

    def get_current_risk_assessment(self) -> Dict[str, Any]:
        """Get current risk assessment"""
        positions = self.get_open_positions()

        total_exposure = sum(abs(p.unrealized_pl) for p in positions)
        portfolio_value = sum(p.current_price * p.quantity for p in positions)

        # Simple risk calculation
        exposure_ratio = (total_exposure / portfolio_value) if portfolio_value > 0 else 0

        risk_level = RiskLevel.LOW
        if exposure_ratio > 0.30:
            risk_level = RiskLevel.EXTREME
        elif exposure_ratio > 0.20:
            risk_level = RiskLevel.HIGH
        elif exposure_ratio > 0.10:
            risk_level = RiskLevel.MEDIUM

        alerts = []
        if risk_level in [RiskLevel.HIGH, RiskLevel.EXTREME]:
            alerts.append(f"High exposure ratio: {exposure_ratio:.2%}")

        return {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio_value,
            'total_exposure': total_exposure,
            'exposure_ratio': exposure_ratio,
            'risk_level': risk_level.value,
            'open_positions': len(positions),
            'alerts': alerts
        }

    # ==================== PERFORMANCE ANALYTICS ====================

    def calculate_bot_performance(self, bot_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate bot performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Get completed trades
        cursor.execute('''
            SELECT profit_loss, profit_loss_percent, fees
            FROM trades
            WHERE bot_id = ? AND status = 'filled' AND exit_time >= ?
        ''', (bot_id, start_date))

        trades = cursor.fetchall()
        conn.close()

        if not trades:
            return {
                'bot_id': bot_id,
                'period_days': days,
                'total_trades': 0,
                'message': 'No completed trades in period'
            }

        total_pl = sum(t[0] or 0 for t in trades)
        total_fees = sum(t[2] or 0 for t in trades)
        winning_trades = [t for t in trades if (t[0] or 0) > 0]
        losing_trades = [t for t in trades if (t[0] or 0) < 0]

        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        avg_win = sum(t[0] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t[0] for t in losing_trades) / len(losing_trades) if losing_trades else 0

        return {
            'bot_id': bot_id,
            'period_days': days,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_profit_loss': total_pl,
            'total_fees': total_fees,
            'net_profit_loss': total_pl - total_fees,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'calculated_at': datetime.now().isoformat()
        }

    def generate_portfolio_summary(self) -> Dict[str, Any]:
        """Generate comprehensive portfolio summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all active bots
        cursor.execute("SELECT COUNT(*) FROM bots WHERE status = 'active'")
        active_bots = cursor.fetchone()[0]

        # Get open positions
        positions = self.get_open_positions()
        total_unrealized_pl = sum(p.unrealized_pl for p in positions)

        # Get today's trades
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*), SUM(profit_loss)
            FROM trades
            WHERE DATE(entry_time) = ? AND status = 'filled'
        ''', (today,))
        today_trades, today_pl = cursor.fetchone()

        conn.close()

        return {
            'active_bots': active_bots,
            'open_positions': len(positions),
            'total_unrealized_pl': total_unrealized_pl,
            'today_trades': today_trades or 0,
            'today_pl': today_pl or 0,
            'generated_at': datetime.now().isoformat()
        }


def main():
    """Demo and testing"""
    print("\n" + "="*70)
    print("PILLAR 3: TRADING OPERATIONS")
    print("="*70 + "\n")

    trading_ops = TradingOperations()

    # Demo: Register sample bot
    sample_bot = TradingBot(
        id=f"BOT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name="Momentum Trader Alpha",
        mode=TradingMode.PAPER.value,
        strategy="momentum",
        risk_profile="moderate",
        status="active",
        capital=10000.00,
        max_position_size=1000.00,
        max_daily_trades=20,
        started_at=datetime.now().isoformat()
    )
    bot_id = trading_ops.register_bot(sample_bot)
    print(f"Sample bot registered: {sample_bot.name} ({bot_id})")

    # Demo: Record sample trade
    sample_trade = Trade(
        id=f"TRADE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        bot_id=bot_id,
        symbol="BTC/USD",
        side="buy",
        quantity=0.1,
        entry_price=45000.00,
        exit_price=45500.00,
        entry_time=datetime.now().isoformat(),
        exit_time=(datetime.now() + timedelta(hours=2)).isoformat(),
        status=TradeStatus.FILLED.value,
        profit_loss=50.00,
        profit_loss_percent=1.11,
        fees=5.00,
        strategy="momentum"
    )
    trade_id = trading_ops.record_trade(sample_trade)
    print(f"Sample trade recorded: {sample_trade.symbol} - ${sample_trade.profit_loss:,.2f} P/L")

    # Generate reports
    print("\n" + "-"*70)
    print("TRADING REPORTS")
    print("-"*70)

    portfolio = trading_ops.generate_portfolio_summary()
    print(f"\nPortfolio Summary:")
    print(f"  Active Bots: {portfolio['active_bots']}")
    print(f"  Open Positions: {portfolio['open_positions']}")
    print(f"  Total Unrealized P/L: ${portfolio['total_unrealized_pl']:,.2f}")
    print(f"  Today's Trades: {portfolio['today_trades']}")
    print(f"  Today's P/L: ${portfolio['today_pl']:,.2f}")

    risk = trading_ops.get_current_risk_assessment()
    print(f"\nRisk Assessment:")
    print(f"  Portfolio Value: ${risk['portfolio_value']:,.2f}")
    print(f"  Risk Level: {risk['risk_level']}")
    print(f"  Alerts: {len(risk['alerts'])}")

    print("\n" + "="*70)
    print("Trading Operations Module Ready")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
