#!/usr/bin/env python3
"""
9 AM DUAL/TRIPLE SHORT STRATEGY LAUNCHER
- Big Short + Momentum Short + Technical Breakdown Short
- Paper by default; can be switched to live in config/env
- Optional wait-until-9:00 local time (skip via SKIP_WAIT_FOR_9AM=1)
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Ensure imports resolve
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pillar_a_trading.strategies.big_short_strategy import BigShortStrategy
from pillar_a_trading.strategies.momentum_short_strategy import MomentumShortStrategy
from pillar_a_trading.strategies.technical_breakdown_short_strategy import TechnicalBreakdownShortStrategy
from paper_trade_executor import PaperTradeExecutor

# Logging
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"trading_9am_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-16s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LAUNCHER_9AM")


def load_env(env_path: Path) -> None:
    """Load a simple KEY=VALUE .env file if present (no external deps)."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()

        # Basic validation for critical parameters to avoid dangerous misconfigurations.
        if key == "RISK_PER_TRADE":
            try:
                risk = float(val)
            except ValueError:
                logger.error("Invalid RISK_PER_TRADE value %r in %s; must be a float between 0 and 1.", val, env_path)
                raise ValueError(f"Invalid RISK_PER_TRADE value {val!r}; must be a float between 0 and 1.")
            if not (0.0 < risk <= 1.0):
                logger.error("Out-of-range RISK_PER_TRADE value %r in %s; must be in (0, 1].", val, env_path)
                raise ValueError(f"Out-of-range RISK_PER_TRADE value {val!r}; must be in (0, 1].")

        if key == "MAX_POSITIONS":
            try:
                max_positions = int(val)
            except ValueError:
                logger.error("Invalid MAX_POSITIONS value %r in %s; must be a positive integer.", val, env_path)
                raise ValueError(f"Invalid MAX_POSITIONS value {val!r}; must be a positive integer.")
            if max_positions <= 0:
                logger.error("Non-positive MAX_POSITIONS value %r in %s; must be a positive integer.", val, env_path)
                raise ValueError(f"Non-positive MAX_POSITIONS value {val!r}; must be a positive integer.")

        os.environ.setdefault(key, val)
def wait_until_9am(skip_wait: bool) -> None:
    if skip_wait:
        return
    now = datetime.now()
    if now.hour >= 9:
        return
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    seconds = (target - now).total_seconds()
    logger.info(f"Waiting {int(seconds//60)} minutes until 9:00 AM to launch...")
    time.sleep(max(0, seconds))


def synth_market_data() -> List[Dict[str, Any]]:
    """Synthetic market snapshots; replace with real feeds for production."""
    return [
        {
            "symbol": "OVERVALUED_TECH",
            "pe_ratio": 150,
            "pb_ratio": 8,
            "debt_equity": 4.5,
            "rsi": 82,
            "vix": 12,
            "price_below_sma_20": True,
            "volume_spike": True,
            "bearish_pattern": True,
            "news_sentiment": "extremely_bullish",
            "revenue_growth": -8,
            "accounting_irregularities": False,
            "price": 120,
            "ma_50": 70,
            "avg_volume": 1_000_000,
            "volume": 3_500_000,
            "bearish_divergence": True,
            "failed_breakout": True,
            "support_level": 125,
            "ma_200": 80,
            "pattern": "double_top",
            "macd": "bearish",
        },
        {
            "symbol": "BUBBLE_STOCK",
            "pe_ratio": "N/A",
            "pb_ratio": 15,
            "debt_equity": 6.2,
            "rsi": 88,
            "vix": 10,
            "price_below_sma_20": False,
            "volume_spike": True,
            "bearish_pattern": True,
            "news_sentiment": "euphoric",
            "revenue_growth": -15,
            "accounting_irregularities": True,
            "price": 90,
            "ma_50": 50,
            "avg_volume": 800_000,
            "volume": 2_000_000,
            "bearish_divergence": False,
            "failed_breakout": True,
            "support_level": 95,
            "ma_200": 60,
            "pattern": "head_and_shoulders",
            "macd": "bearish",
        },
    ]


def collect_signals(strategies, market_data: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []
    for snapshot in market_data:
        symbol = snapshot.get("symbol", "UNKNOWN")
        for strat in strategies:
            sig = strat.analyze_for_short(symbol, snapshot)
            if sig.get("action") in {"SHORT", "SHORT_SMALL"} and sig.get("confidence", 0) >= threshold:
                signals.append(sig)
    # Sort by confidence descending
    signals.sort(key=lambda s: s.get("confidence", 0), reverse=True)
    return signals


def main() -> int:
    env_file = PROJECT_ROOT / "config" / ".env"
    load_env(env_file)

    environment = os.getenv("ENVIRONMENT", os.getenv("TRADING_MODE", "paper")).lower()
    confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.9"))
    risk_per_trade = float(os.getenv("RISK_PER_TRADE", "0.02"))
    max_positions = int(os.getenv("MAX_POSITIONS", "5"))
    initial_balance = float(os.getenv("INITIAL_BALANCE", "100000"))
    skip_wait = os.getenv("SKIP_WAIT_FOR_9AM", "0") == "1"

    logger.info("=" * 80)
    logger.info("9 AM DUAL/TRIPLE SHORT STRATEGY LAUNCHER")
    logger.info("=" * 80)
    logger.info(f"Environment: {environment.upper()} | Confidence >= {confidence_threshold:.2f}")
    logger.info(f"Risk per trade: {risk_per_trade:.2%} | Max positions: {max_positions}")
    logger.info(f"Initial balance: ${initial_balance:,.2f}")
    logger.info(f"Skip wait for 9 AM: {skip_wait}")
    logger.info("=" * 80)

    wait_until_9am(skip_wait)

    # Initialize strategies
    strategies = [
        BigShortStrategy(),
        MomentumShortStrategy(),
        TechnicalBreakdownShortStrategy(),
    ]

    executor = PaperTradeExecutor(balance=initial_balance, risk_per_trade=risk_per_trade)

    iteration = 0
    try:
        while True:
            iteration += 1
            logger.info("-" * 60)
            logger.info(f"Iteration {iteration} @ {datetime.now().strftime('%H:%M:%S')}")

            market_data = synth_market_data()
            signals = collect_signals(strategies, market_data, confidence_threshold)

            executed = 0
            for sig in signals:
                if executed >= max_positions:
                    break
                pos = executor.open_short(sig)
                result = executor.close_position(pos)
                executed += 1
                logger.info(
                    f"TRADE {executed}/{max_positions}: {pos.symbol} | {pos.strategy} | "
                    f"conf {pos.confidence:.2%} | win={result['win']} | pnl={result['pnl']:.2f} | "
                    f"balance={result['balance']:.2f}"
                )

            stats = executor.stats()
            logger.info(
                f"STATS: trades={stats['total_trades']} wins={stats['wins']} "
                f"losses={stats['losses']} win_rate={stats['win_rate']:.1f}% "
                f"pnl={stats['realized_pnl']:.2f} balance={stats['balance']:.2f}"
            )

            # For demo, loop every 30s. Adjust to real cadence when live data wired.
            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("Shutdown requested. Exiting cleanly.")
        final = executor.stats()
        logger.info(
            f"FINAL: trades={final['total_trades']} wins={final['wins']} losses={final['losses']} "
            f"win_rate={final['win_rate']:.1f}% pnl={final['realized_pnl']:.2f} "
            f"balance={final['balance']:.2f}"
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
