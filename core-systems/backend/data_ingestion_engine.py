"""
DATA INGESTION ENGINE - COMPLETE BACKEND IMPLEMENTATION
Robust data ingestion from multiple sources with trading logic execution
Database transaction management, error recovery, and performance optimization

Role 2 of Agent X5 Implementation
"""

import asyncio
import json
import logging
import os
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import time
from collections import defaultdict
import aiohttp
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Data source types"""
    CSV = "csv"
    JSON = "json"
    API = "api"
    DATABASE = "database"
    WEBSOCKET = "websocket"
    BINANCE = "binance"
    MT5 = "mt5"
    ROBINHOOD = "robinhood"


class IngestionStatus(Enum):
    """Ingestion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ValidationLevel(Enum):
    """Data validation levels"""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"


@dataclass
class DataSource:
    """Data source configuration"""
    source_id: str
    source_type: DataSourceType
    name: str
    connection_params: Dict[str, Any]
    validation_level: ValidationLevel = ValidationLevel.BASIC
    batch_size: int = 1000
    max_retries: int = 3
    retry_delay: int = 5
    enabled: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['source_type'] = self.source_type.value
        data['validation_level'] = self.validation_level.value
        return data


@dataclass
class IngestionJob:
    """Data ingestion job"""
    job_id: str
    source: DataSource
    status: IngestionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_failed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'source': self.source.to_dict(),
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'records_processed': self.records_processed,
            'records_failed': self.records_failed,
            'errors': self.errors,
            'metadata': self.metadata
        }


@dataclass
class ValidationResult:
    """Data validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fields_validated: int
    validation_time: float

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TradingSignal:
    """Trading signal from data analysis"""
    signal_id: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    timestamp: datetime
    indicators: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DatabaseManager:
    """Database transaction management"""

    def __init__(self, db_path: str = "/tmp/data_ingestion.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self.initialize_database()

    def initialize_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_jobs (
                job_id TEXT PRIMARY KEY,
                source_id TEXT,
                source_type TEXT,
                status TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                records_processed INTEGER,
                records_failed INTEGER,
                errors TEXT,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                source_id TEXT,
                record_type TEXT,
                data TEXT,
                ingested_at TEXT,
                FOREIGN KEY (job_id) REFERENCES ingestion_jobs(job_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                signal_id TEXT PRIMARY KEY,
                symbol TEXT,
                signal_type TEXT,
                confidence REAL,
                price REAL,
                timestamp TEXT,
                indicators TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                source TEXT,
                ingested_at TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_symbol
            ON market_data(symbol, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol
            ON trading_signals(symbol, timestamp)
        """)

        self.conn.commit()
        logger.info("Database initialized")

    def save_ingestion_job(self, job: IngestionJob):
        """Save ingestion job to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ingestion_jobs
                (job_id, source_id, source_type, status, created_at, started_at,
                 completed_at, records_processed, records_failed, errors, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id,
                job.source.source_id,
                job.source.source_type.value,
                job.status.value,
                job.created_at.isoformat(),
                job.started_at.isoformat() if job.started_at else None,
                job.completed_at.isoformat() if job.completed_at else None,
                job.records_processed,
                job.records_failed,
                json.dumps(job.errors),
                json.dumps(job.metadata)
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            self.conn.rollback()

    def save_raw_data(self, job_id: str, source_id: str, record_type: str, data: Dict):
        """Save raw data record"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO raw_data
                (job_id, source_id, record_type, data, ingested_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                job_id,
                source_id,
                record_type,
                json.dumps(data),
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
            self.conn.rollback()

    def save_trading_signal(self, signal: TradingSignal):
        """Save trading signal"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO trading_signals
                (signal_id, symbol, signal_type, confidence, price, timestamp,
                 indicators, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.signal_id,
                signal.symbol,
                signal.signal_type,
                signal.confidence,
                signal.price,
                signal.timestamp.isoformat(),
                json.dumps(signal.indicators),
                json.dumps(signal.metadata),
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            self.conn.rollback()

    def save_market_data(self, symbol: str, timestamp: datetime, ohlcv: Dict, source: str):
        """Save market data (OHLCV)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO market_data
                (symbol, timestamp, open, high, low, close, volume, source, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                timestamp.isoformat(),
                ohlcv.get('open'),
                ohlcv.get('high'),
                ohlcv.get('low'),
                ohlcv.get('close'),
                ohlcv.get('volume'),
                source,
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving market data: {e}")
            self.conn.rollback()

    def get_market_data(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get market data as DataFrame"""
        query = "SELECT * FROM market_data WHERE symbol = ?"
        params = [symbol]

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " ORDER BY timestamp ASC"

        df = pd.read_sql_query(query, self.conn, params=params)
        return df

    def get_trading_signals(
        self,
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[Dict]:
        """Get trading signals"""
        query = "SELECT * FROM trading_signals WHERE confidence >= ?"
        params = [min_confidence]

        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)

        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)

        query += " ORDER BY timestamp DESC LIMIT 100"

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]

        signals = []
        for row in cursor.fetchall():
            signal = dict(zip(columns, row))
            signal['indicators'] = json.loads(signal['indicators'])
            signal['metadata'] = json.loads(signal['metadata'])
            signals.append(signal)

        return signals

    def begin_transaction(self):
        """Begin database transaction"""
        self.conn.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """Commit database transaction"""
        self.conn.commit()

    def rollback_transaction(self):
        """Rollback database transaction"""
        self.conn.rollback()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class DataValidator:
    """Data validation pipeline"""

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.BASIC):
        """
        Initialize data validator

        Args:
            validation_level: Level of validation to perform
        """
        self.validation_level = validation_level

    def validate(self, data: Dict, schema: Optional[Dict] = None) -> ValidationResult:
        """
        Validate data

        Args:
            data: Data to validate
            schema: Optional schema for validation

        Returns:
            Validation result
        """
        start_time = time.time()
        errors = []
        warnings = []

        if self.validation_level == ValidationLevel.NONE:
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                fields_validated=0,
                validation_time=time.time() - start_time
            )

        # Basic validation
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                fields_validated=0,
                validation_time=time.time() - start_time
            )

        fields_validated = 0

        # Check for required fields
        if schema:
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
                fields_validated += 1

            # Type checking
            field_types = schema.get('types', {})
            for field, expected_type in field_types.items():
                if field in data:
                    if not isinstance(data[field], expected_type):
                        errors.append(
                            f"Field {field} has wrong type: "
                            f"expected {expected_type}, got {type(data[field])}"
                        )
                    fields_validated += 1

        # Comprehensive validation
        if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.COMPREHENSIVE]:
            # Check for null values
            for key, value in data.items():
                if value is None:
                    warnings.append(f"Field {key} is null")
                fields_validated += 1

            # Check for empty strings
            for key, value in data.items():
                if isinstance(value, str) and not value.strip():
                    warnings.append(f"Field {key} is empty string")

        # Comprehensive additional checks
        if self.validation_level == ValidationLevel.COMPREHENSIVE:
            # Check for suspicious values
            for key, value in data.items():
                if isinstance(value, (int, float)) and value < 0:
                    warnings.append(f"Field {key} has negative value: {value}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fields_validated=fields_validated,
            validation_time=time.time() - start_time
        )


class CSVIngestionStrategy:
    """CSV file ingestion strategy"""

    async def ingest(self, file_path: str, batch_size: int = 1000) -> List[Dict]:
        """Ingest data from CSV file"""
        records = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []

                for row in reader:
                    batch.append(row)

                    if len(batch) >= batch_size:
                        records.extend(batch)
                        batch = []

                # Add remaining records
                if batch:
                    records.extend(batch)

            logger.info(f"CSV ingestion complete: {len(records)} records from {file_path}")
            return records

        except Exception as e:
            logger.error(f"CSV ingestion error: {e}")
            return []


class JSONIngestionStrategy:
    """JSON file ingestion strategy"""

    async def ingest(self, file_path: str) -> List[Dict]:
        """Ingest data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Check for common data array keys
                for key in ['data', 'records', 'items', 'results']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
                else:
                    records = [data]
            else:
                records = []

            logger.info(f"JSON ingestion complete: {len(records)} records from {file_path}")
            return records

        except Exception as e:
            logger.error(f"JSON ingestion error: {e}")
            return []


class APIIngestionStrategy:
    """API data ingestion strategy"""

    async def ingest(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth: Optional[tuple] = None
    ) -> List[Dict]:
        """Ingest data from API endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    headers=headers,
                    auth=aiohttp.BasicAuth(*auth) if auth else None
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Handle different response structures
                        if isinstance(data, list):
                            records = data
                        elif isinstance(data, dict):
                            # Common API response patterns
                            for key in ['data', 'records', 'items', 'results']:
                                if key in data and isinstance(data[key], list):
                                    records = data[key]
                                    break
                            else:
                                records = [data]
                        else:
                            records = []

                        logger.info(f"API ingestion complete: {len(records)} records from {endpoint}")
                        return records
                    else:
                        logger.error(f"API error: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"API ingestion error: {e}")
            return []


class BinanceIngestionStrategy:
    """Binance API ingestion strategy"""

    def __init__(self, api_key: str, api_secret: str):
        """Initialize Binance ingestion"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com"

    async def ingest_klines(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100
    ) -> List[Dict]:
        """Ingest candlestick data"""
        try:
            endpoint = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Transform klines to OHLCV format
                        records = []
                        for kline in data:
                            records.append({
                                'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[5]),
                                'symbol': symbol
                            })

                        logger.info(f"Binance klines ingested: {len(records)} for {symbol}")
                        return records
                    else:
                        logger.error(f"Binance API error: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Binance ingestion error: {e}")
            return []

    async def ingest_ticker(self, symbol: str) -> Optional[Dict]:
        """Ingest current ticker data"""
        try:
            endpoint = f"{self.base_url}/api/v3/ticker/24hr"
            params = {'symbol': symbol}

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'symbol': data['symbol'],
                            'price': float(data['lastPrice']),
                            'volume': float(data['volume']),
                            'change_percent': float(data['priceChangePercent']),
                            'high': float(data['highPrice']),
                            'low': float(data['lowPrice']),
                            'timestamp': datetime.now()
                        }
                    return None

        except Exception as e:
            logger.error(f"Binance ticker error: {e}")
            return None


class MT5IngestionStrategy:
    """MT5 (MetaTrader 5) ingestion strategy"""

    def __init__(self):
        """Initialize MT5 ingestion"""
        self.mt5_available = False
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            self.mt5_available = True
        except ImportError:
            logger.warning("MetaTrader5 not available")

    async def ingest_bars(
        self,
        symbol: str,
        timeframe: int,
        count: int = 100
    ) -> List[Dict]:
        """Ingest bar data from MT5"""
        if not self.mt5_available:
            logger.error("MT5 not available")
            return []

        try:
            if not self.mt5.initialize():
                logger.error("MT5 initialization failed")
                return []

            # Get bars
            rates = self.mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

            if rates is None or len(rates) == 0:
                logger.warning(f"No data for {symbol}")
                return []

            # Convert to dict format
            records = []
            for rate in rates:
                records.append({
                    'timestamp': datetime.fromtimestamp(rate['time']),
                    'open': float(rate['open']),
                    'high': float(rate['high']),
                    'low': float(rate['low']),
                    'close': float(rate['close']),
                    'volume': float(rate['tick_volume']),
                    'symbol': symbol
                })

            self.mt5.shutdown()
            logger.info(f"MT5 bars ingested: {len(records)} for {symbol}")
            return records

        except Exception as e:
            logger.error(f"MT5 ingestion error: {e}")
            return []


class TradingLogicExecutor:
    """Trading logic execution engine"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize trading logic executor

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    async def analyze_market_data(self, symbol: str) -> Optional[TradingSignal]:
        """
        Analyze market data and generate trading signals

        Args:
            symbol: Trading symbol

        Returns:
            Trading signal or None
        """
        try:
            # Get recent market data
            df = self.db.get_market_data(
                symbol,
                start_time=datetime.now() - timedelta(days=7)
            )

            if df.empty:
                logger.warning(f"No market data for {symbol}")
                return None

            # Calculate technical indicators
            indicators = self._calculate_indicators(df)

            # Generate signal
            signal = self._generate_signal(symbol, df, indicators)

            if signal:
                self.db.save_trading_signal(signal)

            return signal

        except Exception as e:
            logger.error(f"Error analyzing market data: {e}")
            return None

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}

        try:
            # Simple Moving Average (SMA)
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()

            # Exponential Moving Average (EMA)
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()

            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()

            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # Get latest values
            latest = df.iloc[-1]
            indicators['sma_20'] = float(latest['sma_20']) if not pd.isna(latest['sma_20']) else None
            indicators['sma_50'] = float(latest['sma_50']) if not pd.isna(latest['sma_50']) else None
            indicators['rsi'] = float(latest['rsi']) if not pd.isna(latest['rsi']) else None
            indicators['macd'] = float(latest['macd']) if not pd.isna(latest['macd']) else None
            indicators['macd_signal'] = float(latest['macd_signal']) if not pd.isna(latest['macd_signal']) else None

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")

        return indicators

    def _generate_signal(
        self,
        symbol: str,
        df: pd.DataFrame,
        indicators: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate trading signal based on indicators"""
        try:
            latest_price = float(df.iloc[-1]['close'])
            signal_type = "HOLD"
            confidence = 0.5

            # Simple signal logic
            rsi = indicators.get('rsi')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')

            if rsi and macd and macd_signal:
                # Buy signals
                if rsi < 30 and macd > macd_signal:
                    signal_type = "BUY"
                    confidence = 0.75

                # Sell signals
                elif rsi > 70 and macd < macd_signal:
                    signal_type = "SELL"
                    confidence = 0.75

                # Moderate buy
                elif rsi < 40:
                    signal_type = "BUY"
                    confidence = 0.60

                # Moderate sell
                elif rsi > 60:
                    signal_type = "SELL"
                    confidence = 0.60

            if signal_type != "HOLD":
                signal_id = hashlib.md5(
                    f"{symbol}_{signal_type}_{int(time.time())}".encode()
                ).hexdigest()[:16]

                return TradingSignal(
                    signal_id=signal_id,
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=confidence,
                    price=latest_price,
                    timestamp=datetime.now(),
                    indicators=indicators
                )

            return None

        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None


class DataIngestionEngine:
    """Main data ingestion engine"""

    def __init__(self, db_path: str = "/tmp/data_ingestion.db"):
        """
        Initialize data ingestion engine

        Args:
            db_path: Path to database file
        """
        self.db = DatabaseManager(db_path)
        self.validator = DataValidator()
        self.trading_executor = TradingLogicExecutor(self.db)

        # Ingestion strategies
        self.csv_strategy = CSVIngestionStrategy()
        self.json_strategy = JSONIngestionStrategy()
        self.api_strategy = APIIngestionStrategy()
        self.mt5_strategy = MT5IngestionStrategy()

        self.jobs: Dict[str, IngestionJob] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)

    def generate_job_id(self, source_id: str) -> str:
        """Generate unique job ID"""
        timestamp = str(int(time.time()))
        data = f"{source_id}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    async def create_ingestion_job(self, source: DataSource) -> str:
        """
        Create new ingestion job

        Args:
            source: Data source configuration

        Returns:
            Job ID
        """
        job_id = self.generate_job_id(source.source_id)

        job = IngestionJob(
            job_id=job_id,
            source=source,
            status=IngestionStatus.PENDING,
            created_at=datetime.now()
        )

        self.jobs[job_id] = job
        self.db.save_ingestion_job(job)

        logger.info(f"Ingestion job created: {job_id}")
        return job_id

    async def execute_job(self, job_id: str):
        """
        Execute ingestion job

        Args:
            job_id: Job ID to execute
        """
        if job_id not in self.jobs:
            logger.error(f"Job not found: {job_id}")
            return

        job = self.jobs[job_id]
        job.status = IngestionStatus.IN_PROGRESS
        job.started_at = datetime.now()
        self.db.save_ingestion_job(job)

        retry_count = 0
        max_retries = job.source.max_retries

        while retry_count <= max_retries:
            try:
                # Ingest data based on source type
                records = await self._ingest_from_source(job.source)

                # Process records in batches
                await self._process_records(job, records)

                # Mark as completed
                job.status = IngestionStatus.COMPLETED
                job.completed_at = datetime.now()
                self.db.save_ingestion_job(job)

                logger.info(f"Job completed: {job_id} ({job.records_processed} records)")
                break

            except Exception as e:
                logger.error(f"Job error: {e}")
                job.errors.append(str(e))

                retry_count += 1
                if retry_count <= max_retries:
                    job.status = IngestionStatus.RETRYING
                    logger.info(f"Retrying job {job_id} (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(job.source.retry_delay)
                else:
                    job.status = IngestionStatus.FAILED
                    job.completed_at = datetime.now()
                    self.db.save_ingestion_job(job)
                    logger.error(f"Job failed: {job_id}")
                    break

    async def _ingest_from_source(self, source: DataSource) -> List[Dict]:
        """Ingest data from source"""
        params = source.connection_params

        if source.source_type == DataSourceType.CSV:
            return await self.csv_strategy.ingest(
                params['file_path'],
                source.batch_size
            )

        elif source.source_type == DataSourceType.JSON:
            return await self.json_strategy.ingest(params['file_path'])

        elif source.source_type == DataSourceType.API:
            return await self.api_strategy.ingest(
                params['endpoint'],
                params.get('params'),
                params.get('headers'),
                params.get('auth')
            )

        elif source.source_type == DataSourceType.BINANCE:
            binance = BinanceIngestionStrategy(
                params['api_key'],
                params['api_secret']
            )
            return await binance.ingest_klines(
                params['symbol'],
                params.get('interval', '1h'),
                params.get('limit', 100)
            )

        elif source.source_type == DataSourceType.MT5:
            return await self.mt5_strategy.ingest_bars(
                params['symbol'],
                params['timeframe'],
                params.get('count', 100)
            )

        else:
            logger.error(f"Unsupported source type: {source.source_type}")
            return []

    async def _process_records(self, job: IngestionJob, records: List[Dict]):
        """Process ingested records"""
        for record in records:
            try:
                # Validate record
                validation = self.validator.validate(record)

                if not validation.is_valid:
                    job.records_failed += 1
                    job.errors.extend(validation.errors)
                    continue

                # Save raw data
                self.db.save_raw_data(
                    job.job_id,
                    job.source.source_id,
                    'market_data',
                    record
                )

                # If market data, save to market_data table
                if all(k in record for k in ['timestamp', 'open', 'high', 'low', 'close', 'symbol']):
                    self.db.save_market_data(
                        record['symbol'],
                        record['timestamp'],
                        {
                            'open': record['open'],
                            'high': record['high'],
                            'low': record['low'],
                            'close': record['close'],
                            'volume': record.get('volume', 0)
                        },
                        job.source.source_id
                    )

                job.records_processed += 1

            except Exception as e:
                logger.error(f"Error processing record: {e}")
                job.records_failed += 1
                job.errors.append(str(e))

        # Save job progress
        self.db.save_ingestion_job(job)

    async def run_batch_ingestion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """
        Run batch ingestion for multiple sources

        Args:
            sources: List of data sources

        Returns:
            Batch ingestion report
        """
        logger.info(f"Starting batch ingestion: {len(sources)} sources")

        # Create jobs
        job_ids = []
        for source in sources:
            if source.enabled:
                job_id = await self.create_ingestion_job(source)
                job_ids.append(job_id)

        # Execute jobs in parallel
        tasks = [self.execute_job(job_id) for job_id in job_ids]
        await asyncio.gather(*tasks)

        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs': len(job_ids),
            'jobs': []
        }

        for job_id in job_ids:
            if job_id in self.jobs:
                report['jobs'].append(self.jobs[job_id].to_dict())

        logger.info("Batch ingestion complete")
        return report

    def shutdown(self):
        """Shutdown engine"""
        self.executor.shutdown(wait=True)
        self.db.close()
        logger.info("Data ingestion engine shutdown")


# Example usage
async def main():
    """Example usage of Data Ingestion Engine"""

    # Initialize engine
    engine = DataIngestionEngine()

    # Create data sources
    sources = [
        DataSource(
            source_id="binance_btc",
            source_type=DataSourceType.BINANCE,
            name="Binance BTC/USDT",
            connection_params={
                'api_key': 'your_api_key',
                'api_secret': 'your_api_secret',
                'symbol': 'BTCUSDT',
                'interval': '1h',
                'limit': 100
            },
            validation_level=ValidationLevel.BASIC,
            batch_size=100
        )
    ]

    # Run batch ingestion
    print("🔄 Running batch ingestion...")
    report = await engine.run_batch_ingestion(sources)

    print(f"\n✓ Batch Ingestion Complete:")
    print(f"  Total Jobs: {report['total_jobs']}")
    for job in report['jobs']:
        print(f"  - {job['source']['name']}: {job['records_processed']} records")

    # Analyze market data
    print("\n📊 Analyzing market data...")
    signal = await engine.trading_executor.analyze_market_data('BTCUSDT')
    if signal:
        print(f"✓ Trading Signal Generated:")
        print(f"  Symbol: {signal.symbol}")
        print(f"  Type: {signal.signal_type}")
        print(f"  Confidence: {signal.confidence:.2%}")
        print(f"  Price: ${signal.price}")

    # Shutdown
    engine.shutdown()
    print("\n✓ Engine shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
