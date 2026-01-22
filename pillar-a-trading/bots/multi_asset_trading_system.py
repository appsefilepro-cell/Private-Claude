#!/usr/bin/env python3
"""
Multi-Asset Trading System
Supports: Shorting, Options, Forex, Cryptocurrency, USD Crypto Pairs, US Indices
Runs on both Paper and Sandbox environments
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiAssetTrader")


class AssetClass(Enum):
    """Asset classes supported"""

    SHORTING = "shorting"
    OPTIONS = "options"
    FOREX = "forex"
    CRYPTO = "crypto"
    USD_CRYPTO_PAIRS = "usd_crypto_pairs"
    US_INDICES = "us_indices"


class TradingEnvironment(Enum):
    """Trading environments"""

    PAPER = "paper"
    SANDBOX = "sandbox"
    LIVE = "live"


class ShortingBot:
    """Bot for short selling stocks"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"ShortingBot-{environment.value}"
        logger.info(f"✅ {self.name} initialized")

    def analyze_short_opportunity(self, symbol: str, data: Dict) -> Optional[Dict]:
        """
        Analyze if stock is a good short candidate

        Criteria:
        - Overvalued based on P/E ratio
        - Bearish technical patterns
        - High RSI (overbought)
        - Negative news sentiment
        """
        signal = {
            "symbol": symbol,
            "action": "SHORT",
            "asset_class": "SHORTING",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "reasons": [],
        }

        # Check for bearish patterns
        if data.get("rsi", 50) > 70:
            signal["confidence"] += 0.25
            signal["reasons"].append("RSI overbought (>70)")

        if data.get("pe_ratio", 0) > 50:
            signal["confidence"] += 0.20
            signal["reasons"].append("P/E ratio excessive (>50)")

        if data.get("price_below_sma_20", False):
            signal["confidence"] += 0.25
            signal["reasons"].append("Price below 20-day SMA")

        if data.get("volume_spike", False):
            signal["confidence"] += 0.15
            signal["reasons"].append("Volume spike detected")

        if data.get("bearish_pattern", False):
            signal["confidence"] += 0.15
            signal["reasons"].append("Bearish candlestick pattern")

        if signal["confidence"] >= 0.70:
            signal["status"] = "EXECUTE"
            logger.info(
                f"🔻 {self.name}: SHORT signal for {symbol} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_short(self, signal: Dict) -> Dict:
        """Execute short sell order"""
        order = {
            "bot": self.name,
            "order_type": "SHORT_SELL",
            "symbol": signal["symbol"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(f"📤 {self.name}: Executed SHORT on {signal['symbol']}")
        return order


class OptionsBot:
    """Bot for options trading (calls and puts)"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"OptionsBot-{environment.value}"
        logger.info(f"✅ {self.name} initialized")

    def analyze_option_opportunity(self, symbol: str, data: Dict) -> Optional[Dict]:
        """
        Analyze options trading opportunities

        Strategies:
        - Covered calls (sell calls on owned stock)
        - Protective puts (buy puts to hedge)
        - Bullish call spreads
        - Bearish put spreads
        - Iron condors (neutral markets)
        """
        signal = {
            "symbol": symbol,
            "action": None,
            "asset_class": "OPTIONS",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "strategy": None,
            "reasons": [],
        }

        volatility = data.get("implied_volatility", 0.30)
        price_trend = data.get("trend", "neutral")

        # High volatility = good for selling options (covered calls)
        if volatility > 0.40 and price_trend == "bullish":
            signal["action"] = "SELL_CALL"
            signal["strategy"] = "COVERED_CALL"
            signal["confidence"] = 0.75
            signal["reasons"].append(f"High IV ({volatility:.2%}) + bullish trend")

        # Low volatility + strong trend = good for buying options
        elif volatility < 0.25 and price_trend in ["bullish", "bearish"]:
            signal["action"] = "BUY_CALL" if price_trend == "bullish" else "BUY_PUT"
            signal["strategy"] = "DIRECTIONAL_TRADE"
            signal["confidence"] = 0.70
            signal["reasons"].append(f"Low IV ({volatility:.2%}) + {price_trend} trend")

        # Neutral market = iron condor
        elif volatility > 0.30 and price_trend == "neutral":
            signal["action"] = "IRON_CONDOR"
            signal["strategy"] = "IRON_CONDOR"
            signal["confidence"] = 0.65
            signal["reasons"].append(f"High IV ({volatility:.2%}) + neutral market")

        if signal["confidence"] >= 0.65:
            signal["status"] = "EXECUTE"
            logger.info(
                f"📊 {self.name}: {signal['strategy']} for {symbol} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_option_trade(self, signal: Dict) -> Dict:
        """Execute options trade"""
        order = {
            "bot": self.name,
            "order_type": "OPTIONS",
            "symbol": signal["symbol"],
            "action": signal["action"],
            "strategy": signal["strategy"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(
            f"📤 {self.name}: Executed {signal['strategy']} on {signal['symbol']}"
        )
        return order


class ForexBot:
    """Bot for forex trading (currency pairs)"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"ForexBot-{environment.value}"
        self.major_pairs = [
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "USD/CHF",
            "AUD/USD",
            "USD/CAD",
            "NZD/USD",
        ]
        logger.info(
            f"✅ {self.name} initialized - Monitoring {len(self.major_pairs)} major pairs"
        )

    def analyze_forex_pair(self, pair: str, data: Dict) -> Optional[Dict]:
        """
        Analyze forex pair for trading opportunities

        Strategies:
        - Trend following on major pairs
        - Interest rate differential trading
        - Technical breakouts
        - Support/resistance levels
        """
        signal = {
            "pair": pair,
            "action": None,
            "asset_class": "FOREX",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "reasons": [],
        }

        # Trend analysis
        if data.get("sma_50", 0) > data.get("sma_200", 0):
            signal["action"] = "BUY"
            signal["confidence"] += 0.30
            signal["reasons"].append("Bullish trend (SMA 50 > SMA 200)")
        elif data.get("sma_50", 0) < data.get("sma_200", 0):
            signal["action"] = "SELL"
            signal["confidence"] += 0.30
            signal["reasons"].append("Bearish trend (SMA 50 < SMA 200)")

        # RSI confirmation
        rsi = data.get("rsi", 50)
        if signal["action"] == "BUY" and rsi < 40:
            signal["confidence"] += 0.25
            signal["reasons"].append("RSI oversold (<40)")
        elif signal["action"] == "SELL" and rsi > 60:
            signal["confidence"] += 0.25
            signal["reasons"].append("RSI overbought (>60)")

        # Volume confirmation
        if data.get("volume_above_average", False):
            signal["confidence"] += 0.20
            signal["reasons"].append("Volume above average")

        # Interest rate differential
        if data.get("interest_rate_favorable", False):
            signal["confidence"] += 0.15
            signal["reasons"].append("Favorable interest rate differential")

        if signal["confidence"] >= 0.75 and signal["action"]:
            signal["status"] = "EXECUTE"
            logger.info(
                f"💱 {self.name}: {signal['action']} {pair} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_forex_trade(self, signal: Dict) -> Dict:
        """Execute forex trade"""
        order = {
            "bot": self.name,
            "order_type": "FOREX",
            "pair": signal["pair"],
            "action": signal["action"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(f"📤 {self.name}: Executed {signal['action']} on {signal['pair']}")
        return order


class CryptoBot:
    """Bot for cryptocurrency trading"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"CryptoBot-{environment.value}"
        self.supported_crypto = [
            "BTC",
            "ETH",
            "SOL",
            "ADA",
            "DOT",
            "LINK",
            "AVAX",
            "MATIC",
        ]
        logger.info(
            f"✅ {self.name} initialized - Trading {len(self.supported_crypto)} cryptocurrencies"
        )

    def analyze_crypto(self, symbol: str, data: Dict) -> Optional[Dict]:
        """
        Analyze cryptocurrency for trading opportunities

        Strategies:
        - Momentum trading
        - Breakout patterns
        - Volume analysis
        - On-chain metrics
        """
        signal = {
            "symbol": symbol,
            "action": None,
            "asset_class": "CRYPTO",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "reasons": [],
        }

        # Price momentum
        momentum = data.get("momentum_score", 0)
        if momentum > 0.6:
            signal["action"] = "BUY"
            signal["confidence"] += 0.30
            signal["reasons"].append(f"Strong upward momentum ({momentum:.2f})")
        elif momentum < -0.6:
            signal["action"] = "SELL"
            signal["confidence"] += 0.30
            signal["reasons"].append(f"Strong downward momentum ({momentum:.2f})")

        # Volume analysis
        if data.get("volume_breakout", False):
            signal["confidence"] += 0.25
            signal["reasons"].append("Volume breakout detected")

        # Technical patterns
        if data.get("bullish_pattern", False) and signal["action"] == "BUY":
            signal["confidence"] += 0.20
            signal["reasons"].append("Bullish pattern confirmed")
        elif data.get("bearish_pattern", False) and signal["action"] == "SELL":
            signal["confidence"] += 0.20
            signal["reasons"].append("Bearish pattern confirmed")

        # On-chain metrics (for BTC/ETH)
        if symbol in ["BTC", "ETH"] and data.get("on_chain_bullish", False):
            signal["confidence"] += 0.15
            signal["reasons"].append("Bullish on-chain metrics")

        if signal["confidence"] >= 0.70 and signal["action"]:
            signal["status"] = "EXECUTE"
            logger.info(
                f"₿ {self.name}: {signal['action']} {symbol} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_crypto_trade(self, signal: Dict) -> Dict:
        """Execute cryptocurrency trade"""
        order = {
            "bot": self.name,
            "order_type": "CRYPTO",
            "symbol": signal["symbol"],
            "action": signal["action"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(
            f"📤 {self.name}: Executed {signal['action']} on {signal['symbol']}"
        )
        return order


class USDCryptoPairsBot:
    """Bot specifically for USD cryptocurrency pairs (BTC/USD, ETH/USD, etc.)"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"USDCryptoPairsBot-{environment.value}"
        self.pairs = ["BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD", "DOT/USD", "LINK/USD"]
        logger.info(f"✅ {self.name} initialized - Trading {len(self.pairs)} USD pairs")

    def analyze_usd_crypto_pair(self, pair: str, data: Dict) -> Optional[Dict]:
        """
        Analyze USD crypto pairs
        Combines crypto analysis with USD strength analysis
        """
        signal = {
            "pair": pair,
            "action": None,
            "asset_class": "USD_CRYPTO_PAIRS",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "reasons": [],
        }

        # Crypto strength
        crypto_strength = data.get("crypto_strength", 0)
        # USD strength (DXY index)
        usd_strength = data.get("usd_strength", 0)

        # Strong crypto + weak USD = BUY
        if crypto_strength > 0.6 and usd_strength < -0.3:
            signal["action"] = "BUY"
            signal["confidence"] += 0.40
            signal["reasons"].append("Strong crypto + weak USD")

        # Weak crypto + strong USD = SELL
        elif crypto_strength < -0.6 and usd_strength > 0.3:
            signal["action"] = "SELL"
            signal["confidence"] += 0.40
            signal["reasons"].append("Weak crypto + strong USD")

        # Technical confirmation
        if data.get("breakout", False):
            signal["confidence"] += 0.30
            signal["reasons"].append("Price breakout confirmed")

        # Volume
        if data.get("high_volume", False):
            signal["confidence"] += 0.20
            signal["reasons"].append("High trading volume")

        if signal["confidence"] >= 0.75 and signal["action"]:
            signal["status"] = "EXECUTE"
            logger.info(
                f"💵₿ {self.name}: {signal['action']} {pair} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_usd_crypto_trade(self, signal: Dict) -> Dict:
        """Execute USD crypto pair trade"""
        order = {
            "bot": self.name,
            "order_type": "USD_CRYPTO_PAIR",
            "pair": signal["pair"],
            "action": signal["action"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(f"📤 {self.name}: Executed {signal['action']} on {signal['pair']}")
        return order


class USIndicesBot:
    """Bot for US stock indices (SPY, QQQ, DIA, IWM)"""

    def __init__(self, environment: TradingEnvironment):
        self.environment = environment
        self.name = f"USIndicesBot-{environment.value}"
        self.indices = {
            "SPY": "S&P 500 ETF",
            "QQQ": "Nasdaq-100 ETF",
            "DIA": "Dow Jones Industrial Average ETF",
            "IWM": "Russell 2000 ETF",
        }
        logger.info(
            f"✅ {self.name} initialized - Trading {len(self.indices)} US indices"
        )

    def analyze_index(self, symbol: str, data: Dict) -> Optional[Dict]:
        """
        Analyze US indices for trading opportunities

        Strategies:
        - Trend following
        - Index breakouts
        - VIX correlation
        - Economic data correlation
        """
        signal = {
            "symbol": symbol,
            "name": self.indices.get(symbol, symbol),
            "action": None,
            "asset_class": "US_INDICES",
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.0,
            "reasons": [],
        }

        # Trend analysis
        if data.get("above_200_sma", False):
            signal["action"] = "BUY"
            signal["confidence"] += 0.30
            signal["reasons"].append("Price above 200-day SMA")

        # VIX analysis (low VIX = bullish for indices)
        vix = data.get("vix", 20)
        if vix < 15 and signal["action"] == "BUY":
            signal["confidence"] += 0.25
            signal["reasons"].append(f"Low VIX ({vix}) - low fear")
        elif vix > 30:
            signal["action"] = "SELL"
            signal["confidence"] += 0.25
            signal["reasons"].append(f"High VIX ({vix}) - high fear")

        # Volume confirmation
        if data.get("volume_above_average", False):
            signal["confidence"] += 0.20
            signal["reasons"].append("Volume above average")

        # Economic sentiment
        if data.get("economic_data_positive", False):
            signal["confidence"] += 0.15
            signal["reasons"].append("Positive economic data")

        if signal["confidence"] >= 0.70 and signal["action"]:
            signal["status"] = "EXECUTE"
            logger.info(
                f"📈 {self.name}: {signal['action']} {symbol} @ {signal['confidence']:.2%}"
            )
            return signal

        return None

    def execute_index_trade(self, signal: Dict) -> Dict:
        """Execute US index trade"""
        order = {
            "bot": self.name,
            "order_type": "US_INDEX",
            "symbol": signal["symbol"],
            "name": signal["name"],
            "action": signal["action"],
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment.value,
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "status": (
                "SIMULATED"
                if self.environment != TradingEnvironment.LIVE
                else "PENDING"
            ),
        }

        logger.info(
            f"📤 {self.name}: Executed {signal['action']} on {signal['symbol']}"
        )
        return order


class MultiAssetOrchestrator:
    """Orchestrates all trading bots across all asset classes"""

    def __init__(self):
        self.bots = {}
        self.initialize_all_bots()

    def initialize_all_bots(self):
        """Initialize all bots for both paper and sandbox environments"""
        logger.info("=" * 70)
        logger.info("🚀 INITIALIZING MULTI-ASSET TRADING SYSTEM")
        logger.info("=" * 70)

        for env in [TradingEnvironment.PAPER, TradingEnvironment.SANDBOX]:
            self.bots[env.value] = {
                "shorting": ShortingBot(env),
                "options": OptionsBot(env),
                "forex": ForexBot(env),
                "crypto": CryptoBot(env),
                "usd_crypto_pairs": USDCryptoPairsBot(env),
                "us_indices": USIndicesBot(env),
            }

        logger.info(f"✅ Initialized {len(self.bots) * 6} bots across 2 environments")
        logger.info("=" * 70)

    def get_bot(self, asset_class: str, environment: str):
        """Get specific bot by asset class and environment"""
        return self.bots.get(environment, {}).get(asset_class)

    def get_all_active_bots(self) -> List[Dict]:
        """Get status of all active bots"""
        active_bots = []

        for env, bots in self.bots.items():
            for asset_class, bot in bots.items():
                active_bots.append(
                    {
                        "name": bot.name,
                        "asset_class": asset_class,
                        "environment": env,
                        "status": "ACTIVE",
                    }
                )

        return active_bots


def main():
    """Main entry point - demo of multi-asset system"""
    print(
        """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║           MULTI-ASSET TRADING SYSTEM                              ║
    ║  Shorting | Options | Forex | Crypto | USD Pairs | US Indices    ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    )

    orchestrator = MultiAssetOrchestrator()

    # Show all active bots
    active_bots = orchestrator.get_all_active_bots()
    print(f"\n✅ {len(active_bots)} bots active:\n")

    for bot in active_bots:
        print(f"  • {bot['name']} - {bot['environment'].upper()}")

    print("\n" + "=" * 70)
    print("Multi-asset trading system ready for deployment")
    print("=" * 70)


if __name__ == "__main__":
    main()
