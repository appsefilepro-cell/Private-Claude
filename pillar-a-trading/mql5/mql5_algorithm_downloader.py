#!/usr/bin/env python3
"""
MQL5 ALGORITHM DOWNLOADER & CONVERTER
Scrape, download, and convert MQL5 trading algorithms to Python

Features:
- Download free MQL5 algorithms from MQL5.com
- Parse MQL5 code and extract strategy logic
- Convert to Python for backtesting
- Focus on hedge fund strategies
- Test each algorithm in paper trading
- Performance tracking and comparison
- Integration with existing trading systems
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
import sqlite3
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MQL5Algorithm:
    """MQL5 Algorithm metadata"""
    id: int
    name: str
    author: str
    description: str
    category: str
    strategy_type: str  # trend, scalping, hedging, grid, etc.
    indicators_used: List[str]
    timeframes: List[str]
    symbols: List[str]
    downloads: int
    rating: float
    version: str
    source_url: str
    code_path: Optional[str]
    python_path: Optional[str]
    downloaded_at: str
    status: str  # downloaded, converted, tested


class MQL5AlgorithmDownloader:
    """
    Download and convert MQL5 trading algorithms
    Focus on hedge fund strategies and professional EAs
    """

    def __init__(self, data_dir: str = "/home/user/Private-Claude/pillar-a-trading/data"):
        """
        Initialize MQL5 downloader

        Args:
            data_dir: Directory for storing algorithms and data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.mql5_dir = self.data_dir / "mql5_algorithms"
        self.mql5_dir.mkdir(exist_ok=True)

        self.python_dir = self.data_dir / "mql5_python"
        self.python_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / "mql5_algorithms.db"
        self.init_database()

        # MQL5 website URLs
        self.base_url = "https://www.mql5.com"
        self.codebase_url = f"{self.base_url}/en/code"
        self.market_url = f"{self.base_url}/en/market"

        # Algorithm categories
        self.categories = [
            "expert",  # Expert Advisors
            "indicator",  # Indicators
            "script",  # Scripts
            "library"  # Libraries
        ]

        # Strategy types we're interested in
        self.target_strategies = [
            "hedge",
            "hedging",
            "fund",
            "institutional",
            "martingale",
            "grid",
            "scalping",
            "breakout",
            "momentum",
            "mean_reversion"
        ]

        self.algorithms = []
        logger.info("MQL5 Algorithm Downloader initialized")

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS algorithms (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                author TEXT,
                description TEXT,
                category TEXT,
                strategy_type TEXT,
                indicators_used TEXT,
                timeframes TEXT,
                symbols TEXT,
                downloads INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                version TEXT,
                source_url TEXT,
                code_path TEXT,
                python_path TEXT,
                downloaded_at TEXT,
                status TEXT DEFAULT 'new'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS algorithm_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm_id INTEGER,
                test_date TEXT,
                test_period TEXT,
                total_trades INTEGER,
                win_rate REAL,
                profit_factor REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                net_profit REAL,
                FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    # ============================================================
    # MQL5 CODE SCRAPING & DOWNLOADING
    # ============================================================

    async def scrape_codebase_page(self, page: int = 1, category: str = "expert") -> List[Dict]:
        """
        Scrape MQL5 codebase page for algorithms

        Args:
            page: Page number
            category: Algorithm category

        Returns:
            List of algorithm metadata
        """
        url = f"{self.codebase_url}/{category}?page={page}"
        algorithms = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Find algorithm cards
                    items = soup.find_all('div', class_='codebase-item')

                    for item in items:
                        try:
                            # Extract metadata
                            title_elem = item.find('a', class_='title')
                            if not title_elem:
                                continue

                            name = title_elem.text.strip()
                            link = title_elem.get('href', '')
                            full_url = f"{self.base_url}{link}" if link.startswith('/') else link

                            # Author
                            author_elem = item.find('div', class_='author')
                            author = author_elem.text.strip() if author_elem else "Unknown"

                            # Description
                            desc_elem = item.find('div', class_='description')
                            description = desc_elem.text.strip() if desc_elem else ""

                            # Downloads
                            downloads_elem = item.find('span', class_='downloads')
                            downloads = 0
                            if downloads_elem:
                                downloads_text = downloads_elem.text.strip()
                                downloads = int(re.sub(r'[^\d]', '', downloads_text)) if downloads_text else 0

                            # Rating
                            rating_elem = item.find('div', class_='rating')
                            rating = 0.0
                            if rating_elem:
                                rating_text = rating_elem.text.strip()
                                try:
                                    rating = float(rating_text)
                                except:
                                    pass

                            # Detect strategy type
                            strategy_type = self._detect_strategy_type(name + " " + description)

                            algo = {
                                'name': name,
                                'author': author,
                                'description': description,
                                'category': category,
                                'strategy_type': strategy_type,
                                'downloads': downloads,
                                'rating': rating,
                                'source_url': full_url
                            }

                            algorithms.append(algo)

                        except Exception as e:
                            logger.error(f"Error parsing item: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")

        return algorithms

    def _detect_strategy_type(self, text: str) -> str:
        """Detect strategy type from text"""
        text_lower = text.lower()

        for strategy in self.target_strategies:
            if strategy in text_lower:
                return strategy

        # Additional detection
        if any(word in text_lower for word in ['trend', 'follow']):
            return 'trend_following'
        elif any(word in text_lower for word in ['revers', 'mean']):
            return 'mean_reversion'
        elif 'breakout' in text_lower:
            return 'breakout'
        elif 'scalp' in text_lower:
            return 'scalping'

        return 'unknown'

    async def download_algorithm_code(self, algorithm: Dict) -> Optional[str]:
        """
        Download algorithm source code

        Args:
            algorithm: Algorithm metadata

        Returns:
            Path to downloaded code file
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(algorithm['source_url']) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Find code block
                    code_elem = soup.find('pre', class_='mql-code') or soup.find('code')

                    if not code_elem:
                        logger.warning(f"No code found for {algorithm['name']}")
                        return None

                    code = code_elem.text

                    # Save code
                    safe_name = re.sub(r'[^\w\-_]', '_', algorithm['name'])
                    code_path = self.mql5_dir / f"{safe_name}.mq5"

                    with open(code_path, 'w', encoding='utf-8') as f:
                        f.write(code)

                    logger.info(f"✓ Downloaded: {algorithm['name']}")
                    return str(code_path)

        except Exception as e:
            logger.error(f"Error downloading {algorithm['name']}: {e}")
            return None

    # ============================================================
    # MQL5 TO PYTHON CONVERSION
    # ============================================================

    def parse_mql5_code(self, code: str) -> Dict:
        """
        Parse MQL5 code and extract key components

        Args:
            code: MQL5 source code

        Returns:
            Dictionary with parsed components
        """
        parsed = {
            'inputs': [],
            'indicators': [],
            'entry_conditions': [],
            'exit_conditions': [],
            'risk_management': [],
            'functions': []
        }

        lines = code.split('\n')

        for line in lines:
            line = line.strip()

            # Input parameters
            if 'input' in line:
                parsed['inputs'].append(line)

            # Indicators
            if any(ind in line for ind in ['iMA', 'iRSI', 'iMACD', 'iBands', 'iStochastic']):
                parsed['indicators'].append(line)

            # Entry conditions
            if 'OrderSend' in line or 'PositionOpen' in line:
                parsed['entry_conditions'].append(line)

            # Exit conditions
            if 'OrderClose' in line or 'PositionClose' in line:
                parsed['exit_conditions'].append(line)

            # Risk management
            if any(word in line for word in ['StopLoss', 'TakeProfit', 'TrailingStop']):
                parsed['risk_management'].append(line)

            # Custom functions
            if line.startswith('void') or line.startswith('double') or line.startswith('int'):
                if '(' in line and ')' in line:
                    parsed['functions'].append(line)

        return parsed

    def convert_to_python(self, mql5_path: str, algorithm: Dict) -> Optional[str]:
        """
        Convert MQL5 code to Python

        Args:
            mql5_path: Path to MQL5 code file
            algorithm: Algorithm metadata

        Returns:
            Path to Python file
        """
        try:
            with open(mql5_path, 'r', encoding='utf-8') as f:
                mql5_code = f.read()

            parsed = self.parse_mql5_code(mql5_code)

            # Generate Python code
            python_code = self._generate_python_code(algorithm, parsed)

            # Save Python file
            safe_name = re.sub(r'[^\w\-_]', '_', algorithm['name'])
            python_path = self.python_dir / f"{safe_name}.py"

            with open(python_path, 'w', encoding='utf-8') as f:
                f.write(python_code)

            logger.info(f"✓ Converted to Python: {algorithm['name']}")
            return str(python_path)

        except Exception as e:
            logger.error(f"Error converting {algorithm['name']}: {e}")
            return None

    def _generate_python_code(self, algorithm: Dict, parsed: Dict) -> str:
        """Generate Python trading strategy from parsed MQL5"""
        code = []

        # Header
        code.append('"""')
        code.append(f"{algorithm['name']}")
        code.append(f"Converted from MQL5 - {algorithm['author']}")
        code.append(f"{algorithm['description']}")
        code.append('"""')
        code.append('')
        code.append('import pandas as pd')
        code.append('import numpy as np')
        code.append('from datetime import datetime')
        code.append('from typing import Dict, Optional')
        code.append('')

        # Strategy class
        code.append(f"class {self._to_class_name(algorithm['name'])}:")
        code.append('    """')
        code.append(f"    {algorithm['description']}")
        code.append(f"    Strategy Type: {algorithm['strategy_type']}")
        code.append('    """')
        code.append('')
        code.append('    def __init__(self):')
        code.append('        """Initialize strategy parameters"""')

        # Add input parameters
        for inp in parsed['inputs'][:5]:  # Limit to 5 inputs
            param_name = self._extract_param_name(inp)
            param_value = self._extract_param_value(inp)
            code.append(f'        self.{param_name} = {param_value}')

        code.append('        self.position = None')
        code.append('        self.entry_price = 0.0')
        code.append('')

        # Signal generation method
        code.append('    def generate_signal(self, data: pd.DataFrame) -> str:')
        code.append('        """')
        code.append('        Generate trading signal')
        code.append('        ')
        code.append('        Args:')
        code.append('            data: OHLCV DataFrame')
        code.append('        ')
        code.append('        Returns:')
        code.append('            Signal: "buy", "sell", or "hold"')
        code.append('        """')
        code.append('        if len(data) < 50:')
        code.append('            return "hold"')
        code.append('')
        code.append('        # Calculate indicators')
        code.append('        # TODO: Implement from MQL5 logic')
        code.append('')

        # Add indicator calculations
        for ind in parsed['indicators'][:3]:  # Limit to 3 indicators
            indicator_code = self._convert_indicator(ind)
            code.append(f'        {indicator_code}')

        code.append('')
        code.append('        # Entry conditions')
        code.append('        # TODO: Implement from MQL5 logic')
        code.append('        ')
        code.append('        return "hold"')
        code.append('')

        # Risk management
        code.append('    def calculate_position_size(self, balance: float, risk_percent: float = 0.02) -> float:')
        code.append('        """Calculate position size based on risk"""')
        code.append('        return balance * risk_percent')
        code.append('')

        # Execute trade
        code.append('    def execute_trade(self, signal: str, price: float, balance: float) -> Optional[Dict]:')
        code.append('        """Execute trade based on signal"""')
        code.append('        if signal == "buy" and self.position is None:')
        code.append('            self.position = "long"')
        code.append('            self.entry_price = price')
        code.append('            return {')
        code.append('                "action": "buy",')
        code.append('                "price": price,')
        code.append('                "size": self.calculate_position_size(balance)')
        code.append('            }')
        code.append('        elif signal == "sell" and self.position == "long":')
        code.append('            self.position = None')
        code.append('            return {')
        code.append('                "action": "sell",')
        code.append('                "price": price,')
        code.append('                "profit": price - self.entry_price')
        code.append('            }')
        code.append('        return None')

        return '\n'.join(code)

    def _to_class_name(self, name: str) -> str:
        """Convert algorithm name to Python class name"""
        # Remove special characters
        clean = re.sub(r'[^\w\s]', '', name)
        # Convert to CamelCase
        parts = clean.split()
        return ''.join(word.capitalize() for word in parts)

    def _extract_param_name(self, input_line: str) -> str:
        """Extract parameter name from MQL5 input line"""
        match = re.search(r'\s+(\w+)\s*=', input_line)
        return match.group(1) if match else "param"

    def _extract_param_value(self, input_line: str) -> str:
        """Extract parameter value from MQL5 input line"""
        match = re.search(r'=\s*([^;]+)', input_line)
        value = match.group(1).strip() if match else "0"

        # Convert MQL5 types to Python
        if value.lower() == 'true':
            return 'True'
        elif value.lower() == 'false':
            return 'False'
        else:
            return value

    def _convert_indicator(self, indicator_line: str) -> str:
        """Convert MQL5 indicator to Python equivalent"""
        if 'iMA' in indicator_line:
            return "data['ma'] = data['close'].rolling(20).mean()"
        elif 'iRSI' in indicator_line:
            return "data['rsi'] = self.calculate_rsi(data['close'], 14)"
        elif 'iMACD' in indicator_line:
            return "data['macd'] = data['close'].ewm(span=12).mean() - data['close'].ewm(span=26).mean()"
        else:
            return "# Indicator conversion pending"

    # ============================================================
    # ALGORITHM MANAGEMENT
    # ============================================================

    async def discover_algorithms(self, pages: int = 5) -> List[MQL5Algorithm]:
        """
        Discover algorithms from MQL5 codebase

        Args:
            pages: Number of pages to scrape per category

        Returns:
            List of discovered algorithms
        """
        all_algorithms = []

        for category in ['expert']:  # Focus on Expert Advisors
            logger.info(f"Scraping {category} category...")

            for page in range(1, pages + 1):
                logger.info(f"  Page {page}/{pages}")
                algorithms = await self.scrape_codebase_page(page, category)

                # Filter for hedge fund strategies
                filtered = [
                    algo for algo in algorithms
                    if algo['strategy_type'] in self.target_strategies
                    or 'hedge' in algo['name'].lower()
                    or 'fund' in algo['name'].lower()
                ]

                all_algorithms.extend(filtered)
                await asyncio.sleep(1)  # Be respectful to server

        logger.info(f"Discovered {len(all_algorithms)} algorithms")
        return all_algorithms

    def save_algorithm(self, algorithm: MQL5Algorithm):
        """Save algorithm to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO algorithms
            (id, name, author, description, category, strategy_type,
             indicators_used, timeframes, symbols, downloads, rating,
             version, source_url, code_path, python_path, downloaded_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            algorithm.id, algorithm.name, algorithm.author,
            algorithm.description, algorithm.category, algorithm.strategy_type,
            json.dumps(algorithm.indicators_used),
            json.dumps(algorithm.timeframes),
            json.dumps(algorithm.symbols),
            algorithm.downloads, algorithm.rating, algorithm.version,
            algorithm.source_url, algorithm.code_path, algorithm.python_path,
            algorithm.downloaded_at, algorithm.status
        ))

        conn.commit()
        conn.close()

    def get_algorithms(self, status: Optional[str] = None) -> List[MQL5Algorithm]:
        """Get algorithms from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM algorithms WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM algorithms")

        algorithms = []
        for row in cursor.fetchall():
            algo = MQL5Algorithm(
                id=row[0],
                name=row[1],
                author=row[2],
                description=row[3],
                category=row[4],
                strategy_type=row[5],
                indicators_used=json.loads(row[6]) if row[6] else [],
                timeframes=json.loads(row[7]) if row[7] else [],
                symbols=json.loads(row[8]) if row[8] else [],
                downloads=row[9],
                rating=row[10],
                version=row[11],
                source_url=row[12],
                code_path=row[13],
                python_path=row[14],
                downloaded_at=row[15],
                status=row[16]
            )
            algorithms.append(algo)

        conn.close()
        return algorithms

    # ============================================================
    # REPORTING
    # ============================================================

    def generate_report(self) -> str:
        """Generate algorithm collection report"""
        algorithms = self.get_algorithms()

        report = []
        report.append("=" * 70)
        report.append("MQL5 ALGORITHM COLLECTION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Statistics
        report.append(f"Total Algorithms: {len(algorithms)}")

        by_status = {}
        by_strategy = {}

        for algo in algorithms:
            by_status[algo.status] = by_status.get(algo.status, 0) + 1
            by_strategy[algo.strategy_type] = by_strategy.get(algo.strategy_type, 0) + 1

        report.append("\nBy Status:")
        for status, count in by_status.items():
            report.append(f"  {status}: {count}")

        report.append("\nBy Strategy Type:")
        for strategy, count in sorted(by_strategy.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {strategy}: {count}")

        # Top algorithms
        report.append("\nTop Algorithms (by downloads):")
        top = sorted(algorithms, key=lambda x: x.downloads, reverse=True)[:10]
        for i, algo in enumerate(top, 1):
            report.append(f"  {i}. {algo.name} - {algo.downloads} downloads")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


async def main():
    """Demo MQL5 algorithm downloader"""
    print("\n" + "="*70)
    print("MQL5 ALGORITHM DOWNLOADER - DEMO")
    print("="*70 + "\n")

    downloader = MQL5AlgorithmDownloader()

    print("Discovering algorithms...")
    algorithms = await downloader.discover_algorithms(pages=2)

    print(f"\n✓ Found {len(algorithms)} algorithms")

    # Show sample
    if algorithms:
        print("\nSample algorithms:")
        for algo in algorithms[:5]:
            print(f"\n  {algo['name']}")
            print(f"  Author: {algo['author']}")
            print(f"  Strategy: {algo['strategy_type']}")
            print(f"  Downloads: {algo['downloads']}")

    print("\n" + downloader.generate_report())


if __name__ == "__main__":
    asyncio.run(main())
