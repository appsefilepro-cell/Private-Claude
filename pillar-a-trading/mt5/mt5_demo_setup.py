#!/usr/bin/env python3
"""
MT5 DEMO ACCOUNT SETUP & CONFIGURATION SYSTEM
Complete automation for MT5 demo account creation, connection, and paper trading setup

Features:
- Auto-connect to multiple MT5 demo brokers
- Create and manage demo accounts
- Paper trading environment setup
- Account health monitoring
- Multi-broker rotation
- Trade execution testing
- Performance tracking
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
import time
import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MT5Account:
    """MT5 Account Configuration"""
    broker: str
    server: str
    login: int
    password: str
    account_type: str  # demo, paper, live
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    leverage: int
    currency: str
    status: str  # active, disconnected, error
    last_connected: str
    created_at: str


@dataclass
class BrokerConfig:
    """Broker Configuration for Demo Account Creation"""
    name: str
    server: str
    demo_server: str
    supported_symbols: List[str]
    min_deposit: float
    max_leverage: int
    spread_type: str  # fixed, variable
    commission: float
    trading_hours: str
    supports_crypto: bool
    supports_stocks: bool
    api_available: bool


class MT5DemoSetup:
    """
    Complete MT5 Demo Account Setup and Management System
    Handles multiple brokers, account creation, and paper trading setup
    """

    def __init__(self, data_dir: str = "/home/user/Private-Claude/pillar-a-trading/data"):
        """
        Initialize MT5 Demo Setup System

        Args:
            data_dir: Directory for storing account data and databases
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "mt5_accounts.db"
        self.config_path = self.data_dir / "mt5_config.json"
        self.trades_path = self.data_dir / "mt5_demo_trades.json"

        # Initialize databases
        self.init_database()

        # MT5 state
        self.mt5_initialized = False
        self.active_accounts = []
        self.current_account = None

        # Default broker configurations
        self.brokers = self._load_default_brokers()

        # Paper trading settings
        self.paper_trading_enabled = True
        self.paper_balance = 10000.0  # Starting paper balance
        self.paper_trades = []

        logger.info("MT5 Demo Setup System initialized")

    def _load_default_brokers(self) -> List[BrokerConfig]:
        """Load default broker configurations"""
        return [
            BrokerConfig(
                name="ICMarkets",
                server="ICMarketsSC-Demo",
                demo_server="ICMarketsSC-Demo",
                supported_symbols=["EURUSD", "GBPUSD", "USDJPY", "GOLD", "US30"],
                min_deposit=200.0,
                max_leverage=500,
                spread_type="variable",
                commission=7.0,
                trading_hours="24/5",
                supports_crypto=True,
                supports_stocks=True,
                api_available=True
            ),
            BrokerConfig(
                name="XM",
                server="XMGlobal-Demo",
                demo_server="XMGlobal-Demo 3",
                supported_symbols=["EURUSD", "GBPUSD", "USDJPY", "GOLD", "BTCUSD"],
                min_deposit=5.0,
                max_leverage=888,
                spread_type="variable",
                commission=0.0,
                trading_hours="24/7",
                supports_crypto=True,
                supports_stocks=True,
                api_available=True
            ),
            BrokerConfig(
                name="Pepperstone",
                server="Pepperstone-Demo",
                demo_server="Pepperstone-Demo",
                supported_symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "SPX500"],
                min_deposit=200.0,
                max_leverage=500,
                spread_type="variable",
                commission=3.5,
                trading_hours="24/5",
                supports_crypto=False,
                supports_stocks=True,
                api_available=True
            ),
            BrokerConfig(
                name="OANDA",
                server="OANDA-Demo",
                demo_server="OANDA-Demo",
                supported_symbols=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
                min_deposit=0.0,
                max_leverage=50,
                spread_type="variable",
                commission=0.0,
                trading_hours="24/5",
                supports_crypto=False,
                supports_stocks=False,
                api_available=True
            ),
            BrokerConfig(
                name="FXCM",
                server="FXCM-Demo",
                demo_server="FXCM-USDDemo01",
                supported_symbols=["EURUSD", "GBPUSD", "USDJPY", "GOLD"],
                min_deposit=50.0,
                max_leverage=400,
                spread_type="variable",
                commission=0.04,
                trading_hours="24/5",
                supports_crypto=False,
                supports_stocks=True,
                api_available=True
            )
        ]

    def init_database(self):
        """Initialize SQLite database for account management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker TEXT NOT NULL,
                server TEXT NOT NULL,
                login INTEGER NOT NULL UNIQUE,
                password TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                equity REAL DEFAULT 0.0,
                margin REAL DEFAULT 0.0,
                free_margin REAL DEFAULT 0.0,
                margin_level REAL DEFAULT 0.0,
                leverage INTEGER DEFAULT 100,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'active',
                last_connected TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Trades table for demo trading
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_login INTEGER NOT NULL,
                ticket INTEGER,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                volume REAL NOT NULL,
                open_price REAL NOT NULL,
                close_price REAL,
                stop_loss REAL,
                take_profit REAL,
                profit REAL DEFAULT 0.0,
                commission REAL DEFAULT 0.0,
                swap REAL DEFAULT 0.0,
                open_time TEXT NOT NULL,
                close_time TEXT,
                status TEXT DEFAULT 'open',
                comment TEXT,
                FOREIGN KEY (account_login) REFERENCES accounts(login)
            )
        """)

        # Account performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_login INTEGER NOT NULL,
                date TEXT NOT NULL,
                balance REAL,
                equity REAL,
                profit REAL,
                trades_count INTEGER,
                win_rate REAL,
                FOREIGN KEY (account_login) REFERENCES accounts(login)
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    # ============================================================
    # MT5 INITIALIZATION & CONNECTION
    # ============================================================

    def initialize_mt5(self) -> bool:
        """Initialize MT5 terminal"""
        if self.mt5_initialized:
            logger.info("MT5 already initialized")
            return True

        try:
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                return False

            self.mt5_initialized = True
            version = mt5.version()
            logger.info(f"MT5 initialized successfully. Version: {version}")
            return True

        except Exception as e:
            logger.error(f"Exception during MT5 initialization: {e}")
            return False

    def shutdown_mt5(self):
        """Shutdown MT5 terminal"""
        if self.mt5_initialized:
            mt5.shutdown()
            self.mt5_initialized = False
            logger.info("MT5 shutdown successfully")

    def connect_demo_account(
        self,
        login: int,
        password: str,
        server: str,
        broker: str = "Unknown"
    ) -> bool:
        """
        Connect to MT5 demo account

        Args:
            login: Account login number
            password: Account password
            server: Broker server name
            broker: Broker name for tracking

        Returns:
            True if connection successful
        """
        if not self.initialize_mt5():
            return False

        try:
            # Authorize with account
            authorized = mt5.login(login, password, server)

            if not authorized:
                error = mt5.last_error()
                logger.error(f"Login failed for {login}@{server}: {error}")
                return False

            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False

            # Create account object
            account = MT5Account(
                broker=broker,
                server=server,
                login=login,
                password=password,
                account_type="demo",
                balance=account_info.balance,
                equity=account_info.equity,
                margin=account_info.margin,
                free_margin=account_info.margin_free,
                margin_level=account_info.margin_level,
                leverage=account_info.leverage,
                currency=account_info.currency,
                status="active",
                last_connected=datetime.now().isoformat(),
                created_at=datetime.now().isoformat()
            )

            # Save to database
            self._save_account(account)

            self.current_account = account
            self.active_accounts.append(account)

            logger.info(f"✓ Connected to {broker} demo account {login}")
            logger.info(f"  Balance: {account.balance} {account.currency}")
            logger.info(f"  Equity: {account.equity} {account.currency}")
            logger.info(f"  Leverage: 1:{account.leverage}")

            return True

        except Exception as e:
            logger.error(f"Exception connecting to account: {e}")
            return False

    def _save_account(self, account: MT5Account):
        """Save account to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO accounts
                (broker, server, login, password, account_type, balance, equity,
                 margin, free_margin, margin_level, leverage, currency, status,
                 last_connected, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.broker, account.server, account.login, account.password,
                account.account_type, account.balance, account.equity,
                account.margin, account.free_margin, account.margin_level,
                account.leverage, account.currency, account.status,
                account.last_connected, account.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving account: {e}")
        finally:
            conn.close()

    def get_saved_accounts(self) -> List[MT5Account]:
        """Retrieve all saved accounts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM accounts WHERE status = 'active'")
        rows = cursor.fetchall()
        conn.close()

        accounts = []
        for row in rows:
            account = MT5Account(
                broker=row[1],
                server=row[2],
                login=row[3],
                password=row[4],
                account_type=row[5],
                balance=row[6],
                equity=row[7],
                margin=row[8],
                free_margin=row[9],
                margin_level=row[10],
                leverage=row[11],
                currency=row[12],
                status=row[13],
                last_connected=row[14],
                created_at=row[15]
            )
            accounts.append(account)

        return accounts

    # ============================================================
    # DEMO ACCOUNT TESTING & VALIDATION
    # ============================================================

    def test_connection(self) -> Dict:
        """Test current MT5 connection and return status"""
        if not self.mt5_initialized:
            return {"status": "error", "message": "MT5 not initialized"}

        try:
            account_info = mt5.account_info()
            if account_info is None:
                return {"status": "error", "message": "No account connected"}

            terminal_info = mt5.terminal_info()
            symbols = mt5.symbols_total()

            result = {
                "status": "success",
                "account": {
                    "login": account_info.login,
                    "server": account_info.server,
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "margin_level": account_info.margin_level,
                    "currency": account_info.currency,
                    "leverage": account_info.leverage
                },
                "terminal": {
                    "company": terminal_info.company,
                    "name": terminal_info.name,
                    "path": terminal_info.path,
                    "connected": terminal_info.connected,
                    "trade_allowed": terminal_info.trade_allowed
                },
                "symbols_available": symbols
            }

            return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_account_info(self) -> Optional[Dict]:
        """Get detailed current account information"""
        if not self.mt5_initialized:
            logger.error("MT5 not initialized")
            return None

        account_info = mt5.account_info()
        if account_info is None:
            return None

        return {
            "login": account_info.login,
            "server": account_info.server,
            "balance": account_info.balance,
            "equity": account_info.equity,
            "profit": account_info.profit,
            "margin": account_info.margin,
            "margin_free": account_info.margin_free,
            "margin_level": account_info.margin_level,
            "leverage": account_info.leverage,
            "currency": account_info.currency,
            "company": account_info.company,
            "name": account_info.name
        }

    def test_market_data(self, symbol: str = "EURUSD") -> Dict:
        """Test market data retrieval"""
        if not self.mt5_initialized:
            return {"status": "error", "message": "MT5 not initialized"}

        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {"status": "error", "message": f"Symbol {symbol} not found"}

            # Get latest tick
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return {"status": "error", "message": f"No tick data for {symbol}"}

            # Get recent bars
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)

            return {
                "status": "success",
                "symbol": symbol,
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": tick.ask - tick.bid,
                "volume": tick.volume,
                "time": datetime.fromtimestamp(tick.time).isoformat(),
                "bars_retrieved": len(rates) if rates is not None else 0
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ============================================================
    # PAPER TRADING EXECUTION
    # ============================================================

    def execute_demo_order(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "Demo trade"
    ) -> Optional[Dict]:
        """
        Execute demo/paper trading order

        Args:
            symbol: Trading symbol
            order_type: 'BUY' or 'SELL'
            volume: Trade volume in lots
            stop_loss: Stop loss price
            take_profit: Take profit price
            comment: Trade comment

        Returns:
            Order result dictionary
        """
        if not self.mt5_initialized:
            logger.error("MT5 not initialized")
            return None

        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None

            # Enable symbol if not enabled
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol {symbol}")
                    return None

            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {symbol}")
                return None

            # Determine order type and price
            if order_type.upper() == "BUY":
                price = tick.ask
                mt5_order_type = mt5.ORDER_TYPE_BUY
            else:
                price = tick.bid
                mt5_order_type = mt5.ORDER_TYPE_SELL

            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_order_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Add SL/TP if provided
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit

            # Send order
            result = mt5.order_send(request)

            if result is None:
                logger.error("Order send failed")
                return None

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.retcode} - {result.comment}")
                return None

            # Save trade to database
            self._save_demo_trade({
                "ticket": result.order,
                "symbol": symbol,
                "order_type": order_type,
                "volume": volume,
                "open_price": price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "open_time": datetime.now().isoformat(),
                "comment": comment
            })

            logger.info(f"✓ Demo order executed: {order_type} {volume} {symbol} @ {price}")

            return {
                "status": "success",
                "ticket": result.order,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "price": price,
                "sl": stop_loss,
                "tp": take_profit
            }

        except Exception as e:
            logger.error(f"Exception executing order: {e}")
            return None

    def _save_demo_trade(self, trade: Dict):
        """Save demo trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO demo_trades
                (account_login, ticket, symbol, order_type, volume, open_price,
                 stop_loss, take_profit, open_time, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_account.login if self.current_account else 0,
                trade.get("ticket"),
                trade["symbol"],
                trade["order_type"],
                trade["volume"],
                trade["open_price"],
                trade.get("stop_loss"),
                trade.get("take_profit"),
                trade["open_time"],
                trade.get("comment", "")
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving demo trade: {e}")
        finally:
            conn.close()

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.mt5_initialized:
            return []

        positions = mt5.positions_get()
        if positions is None:
            return []

        result = []
        for pos in positions:
            result.append({
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                "volume": pos.volume,
                "open_price": pos.price_open,
                "current_price": pos.price_current,
                "profit": pos.profit,
                "sl": pos.sl,
                "tp": pos.tp,
                "open_time": datetime.fromtimestamp(pos.time).isoformat()
            })

        return result

    # ============================================================
    # MULTI-BROKER MANAGEMENT
    # ============================================================

    def setup_all_demo_accounts(self) -> Dict:
        """Setup and test connections to all configured brokers"""
        results = {
            "total_brokers": len(self.brokers),
            "successful": 0,
            "failed": 0,
            "accounts": []
        }

        for broker in self.brokers:
            logger.info(f"\nTesting broker: {broker.name}")
            logger.info(f"Server: {broker.demo_server}")

            # Note: Actual login credentials would need to be obtained
            # This is a framework - users need to create demo accounts manually
            result = {
                "broker": broker.name,
                "server": broker.demo_server,
                "status": "configured",
                "message": "Demo account needs to be created at broker website"
            }

            results["accounts"].append(result)

        return results

    def rotate_broker(self) -> bool:
        """Rotate to next available broker account"""
        saved_accounts = self.get_saved_accounts()

        if not saved_accounts:
            logger.warning("No saved accounts available")
            return False

        # Find next account
        current_index = 0
        if self.current_account:
            for i, acc in enumerate(saved_accounts):
                if acc.login == self.current_account.login:
                    current_index = i
                    break

        next_index = (current_index + 1) % len(saved_accounts)
        next_account = saved_accounts[next_index]

        # Connect to next account
        return self.connect_demo_account(
            login=next_account.login,
            password=next_account.password,
            server=next_account.server,
            broker=next_account.broker
        )

    # ============================================================
    # UTILITIES & REPORTING
    # ============================================================

    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        report = []
        report.append("=" * 60)
        report.append("MT5 DEMO ACCOUNT STATUS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Connection status
        test = self.test_connection()
        report.append(f"MT5 Status: {test['status']}")

        if test['status'] == 'success':
            acc = test['account']
            report.append(f"\nActive Account:")
            report.append(f"  Login: {acc['login']}")
            report.append(f"  Server: {acc['server']}")
            report.append(f"  Balance: {acc['balance']} {acc['currency']}")
            report.append(f"  Equity: {acc['equity']} {acc['currency']}")
            report.append(f"  Margin Level: {acc['margin_level']:.2f}%")
            report.append(f"  Leverage: 1:{acc['leverage']}")

        # Open positions
        positions = self.get_open_positions()
        report.append(f"\nOpen Positions: {len(positions)}")
        for pos in positions:
            report.append(f"  {pos['symbol']} {pos['type']} {pos['volume']} lots")
            report.append(f"    Profit: {pos['profit']:.2f}")

        # Saved accounts
        saved = self.get_saved_accounts()
        report.append(f"\nSaved Accounts: {len(saved)}")
        for acc in saved:
            report.append(f"  {acc.broker} - {acc.login} ({acc.status})")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


def main():
    """Demo setup main execution"""
    print("\n" + "="*60)
    print("MT5 DEMO ACCOUNT SETUP & CONFIGURATION")
    print("="*60 + "\n")

    # Initialize setup system
    setup = MT5DemoSetup()

    # Test MT5 initialization
    if setup.initialize_mt5():
        print("✓ MT5 initialized successfully")
    else:
        print("✗ MT5 initialization failed")
        return

    # Display available brokers
    print(f"\nConfigured Brokers: {len(setup.brokers)}")
    for broker in setup.brokers:
        print(f"  - {broker.name} ({broker.demo_server})")
        print(f"    Leverage: 1:{broker.max_leverage}")
        print(f"    Crypto: {broker.supports_crypto}")

    # Test connection (if account configured)
    print("\n" + "-"*60)
    print("Testing Connection & Market Data")
    print("-"*60)

    test_result = setup.test_connection()
    print(f"Connection Status: {test_result['status']}")

    # Test market data
    market_test = setup.test_market_data("EURUSD")
    if market_test['status'] == 'success':
        print(f"\nMarket Data Test (EURUSD):")
        print(f"  Bid: {market_test['bid']}")
        print(f"  Ask: {market_test['ask']}")
        print(f"  Spread: {market_test['spread']:.5f}")

    # Generate status report
    print("\n" + setup.generate_status_report())

    # Cleanup
    setup.shutdown_mt5()
    print("\n✓ Setup complete. MT5 shutdown.")


if __name__ == "__main__":
    main()
