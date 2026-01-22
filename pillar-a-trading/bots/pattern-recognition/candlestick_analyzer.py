"""
Candlestick Pattern Recognition Bot
Identifies the 12 key patterns from Candlestick Trading Bible
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CandlestickAnalyzer")


class CandlestickPattern:
    """Candlestick pattern definitions and detection"""

    # Pattern definitions from Candlestick Trading Bible
    BULLISH_PATTERNS = [
        "HAMMER",
        "INVERTED_HAMMER",
        "BULLISH_ENGULFING",
        "MORNING_STAR",
        "THREE_WHITE_SOLDIERS",
        "DRAGONFLY_DOJI",
    ]

    BEARISH_PATTERNS = [
        "SHOOTING_STAR",
        "HANGING_MAN",
        "BEARISH_ENGULFING",
        "EVENING_STAR",
        "THREE_BLACK_CROWS",
        "GRAVESTONE_DOJI",
    ]

    @staticmethod
    def detect_hammer(candles: List[Dict]) -> Tuple[bool, float]:
        """
        Detect Hammer pattern
        - Small body at top of candle
        - Long lower shadow (2x body)
        - Little to no upper shadow
        """
        if len(candles) < 1:
            return False, 0.0

        c = candles[-1]
        body = abs(c["close"] - c["open"])
        lower_shadow = min(c["open"], c["close"]) - c["low"]
        upper_shadow = c["high"] - max(c["open"], c["close"])

        is_hammer = lower_shadow >= 2 * body and upper_shadow <= 0.1 * body and body > 0

        confidence = 0.75 if is_hammer else 0.0
        return is_hammer, confidence

    @staticmethod
    def detect_engulfing(
        candles: List[Dict], bullish: bool = True
    ) -> Tuple[bool, float]:
        """
        Detect Bullish or Bearish Engulfing pattern
        - Two candles
        - Second candle completely engulfs first candle's body
        """
        if len(candles) < 2:
            return False, 0.0

        prev = candles[-2]
        curr = candles[-1]

        prev_body_top = max(prev["open"], prev["close"])
        prev_body_bottom = min(prev["open"], prev["close"])
        curr_body_top = max(curr["open"], curr["close"])
        curr_body_bottom = min(curr["open"], curr["close"])

        if bullish:
            # Bullish engulfing: prev is red, curr is green and engulfs
            is_engulfing = (
                prev["close"] < prev["open"]  # Previous is bearish
                and curr["close"] > curr["open"]  # Current is bullish
                and curr_body_bottom < prev_body_bottom
                and curr_body_top > prev_body_top
            )
        else:
            # Bearish engulfing: prev is green, curr is red and engulfs
            is_engulfing = (
                prev["close"] > prev["open"]  # Previous is bullish
                and curr["close"] < curr["open"]  # Current is bearish
                and curr_body_bottom < prev_body_bottom
                and curr_body_top > prev_body_top
            )

        confidence = 0.80 if is_engulfing else 0.0
        return is_engulfing, confidence

    @staticmethod
    def detect_doji(candles: List[Dict]) -> Tuple[str, float]:
        """
        Detect Doji patterns (Dragonfly, Gravestone, Long-Legged)
        - Open and close are nearly equal
        - Various shadow configurations
        """
        if len(candles) < 1:
            return None, 0.0

        c = candles[-1]
        body = abs(c["close"] - c["open"])
        total_range = c["high"] - c["low"]

        if total_range == 0:
            return None, 0.0

        body_ratio = body / total_range

        # Doji if body is very small relative to range
        if body_ratio > 0.1:
            return None, 0.0

        lower_shadow = min(c["open"], c["close"]) - c["low"]
        upper_shadow = c["high"] - max(c["open"], c["close"])

        # Dragonfly Doji: long lower shadow, no upper shadow
        if lower_shadow > 2 * body and upper_shadow < 0.1 * total_range:
            return "DRAGONFLY_DOJI", 0.70

        # Gravestone Doji: long upper shadow, no lower shadow
        if upper_shadow > 2 * body and lower_shadow < 0.1 * total_range:
            return "GRAVESTONE_DOJI", 0.70

        # Long-legged Doji: long shadows on both sides
        if lower_shadow > body and upper_shadow > body:
            return "LONG_LEGGED_DOJI", 0.60

        return "DOJI", 0.50

    @staticmethod
    def detect_morning_star(candles: List[Dict]) -> Tuple[bool, float]:
        """
        Detect Morning Star pattern (bullish reversal)
        - Three candles
        - First: long bearish
        - Second: small body (star)
        - Third: long bullish
        """
        if len(candles) < 3:
            return False, 0.0

        first = candles[-3]
        star = candles[-2]
        third = candles[-1]

        first_body = abs(first["close"] - first["open"])
        star_body = abs(star["close"] - star["open"])
        third_body = abs(third["close"] - third["open"])

        is_morning_star = (
            first["close"] < first["open"]  # First is bearish
            and star_body < first_body * 0.3  # Star has small body
            and third["close"] > third["open"]  # Third is bullish
            and third_body > first_body * 0.5  # Third has substantial body
            and third["close"]
            > (first["open"] + first["close"]) / 2  # Third closes above midpoint
        )

        confidence = 0.85 if is_morning_star else 0.0
        return is_morning_star, confidence

    @staticmethod
    def detect_evening_star(candles: List[Dict]) -> Tuple[bool, float]:
        """
        Detect Evening Star pattern (bearish reversal)
        - Three candles (inverse of Morning Star)
        """
        if len(candles) < 3:
            return False, 0.0

        first = candles[-3]
        star = candles[-2]
        third = candles[-1]

        first_body = abs(first["close"] - first["open"])
        star_body = abs(star["close"] - star["open"])
        third_body = abs(third["close"] - third["open"])

        is_evening_star = (
            first["close"] > first["open"]  # First is bullish
            and star_body < first_body * 0.3  # Star has small body
            and third["close"] < third["open"]  # Third is bearish
            and third_body > first_body * 0.5  # Third has substantial body
            and third["close"]
            < (first["open"] + first["close"]) / 2  # Third closes below midpoint
        )

        confidence = 0.85 if is_evening_star else 0.0
        return is_evening_star, confidence


class CandlestickAnalyzer:
    """Main analyzer for processing market data and detecting patterns"""

    def __init__(self, pair: str = "BTC/USD"):
        self.pair = pair
        self.pattern_detector = CandlestickPattern()
        self.signal_history = []
        logger.info(f"Candlestick Analyzer initialized for {pair}")

    def analyze(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        Analyze candles and generate trading signal

        Args:
            candles: List of candle dictionaries with OHLCV data

        Returns:
            Signal dictionary
        """
        if len(candles) < 3:
            return self._no_signal("Insufficient candle data")

        # Check all patterns
        signals = []

        # Hammer (bullish)
        is_hammer, conf = self.pattern_detector.detect_hammer(candles)
        if is_hammer:
            signals.append(("HAMMER", "BUY", conf))

        # Bullish Engulfing
        is_bullish_eng, conf = self.pattern_detector.detect_engulfing(
            candles, bullish=True
        )
        if is_bullish_eng:
            signals.append(("BULLISH_ENGULFING", "BUY", conf))

        # Bearish Engulfing
        is_bearish_eng, conf = self.pattern_detector.detect_engulfing(
            candles, bullish=False
        )
        if is_bearish_eng:
            signals.append(("BEARISH_ENGULFING", "SELL", conf))

        # Morning Star (bullish)
        is_morning_star, conf = self.pattern_detector.detect_morning_star(candles)
        if is_morning_star:
            signals.append(("MORNING_STAR", "BUY", conf))

        # Evening Star (bearish)
        is_evening_star, conf = self.pattern_detector.detect_evening_star(candles)
        if is_evening_star:
            signals.append(("EVENING_STAR", "SELL", conf))

        # Doji patterns
        doji_type, conf = self.pattern_detector.detect_doji(candles)
        if doji_type:
            signal_type = (
                "BUY"
                if "DRAGONFLY" in doji_type
                else "SELL" if "GRAVESTONE" in doji_type else "HOLD"
            )
            signals.append((doji_type, signal_type, conf))

        # Return highest confidence signal
        if signals:
            best_signal = max(signals, key=lambda x: x[2])
            return self._create_signal(
                best_signal[0], best_signal[1], best_signal[2], candles[-1]
            )

        return self._no_signal("No patterns detected")

    def analyze_pattern(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        Alias for analyze() method - analyzes candles for patterns

        Args:
            candles: List of candle dictionaries with OHLCV data

        Returns:
            Signal dictionary
        """
        return self.analyze(candles)

    def _create_signal(
        self, pattern: str, signal_type: str, confidence: float, last_candle: Dict
    ) -> Dict[str, Any]:
        """Create a trading signal"""
        signal = {
            "timestamp": datetime.now().isoformat(),
            "pair": self.pair,
            "pattern": pattern,
            "type": signal_type,
            "confidence": confidence,
            "price": last_candle["close"],
            "volume": last_candle.get("volume", 0),
        }

        self.signal_history.append(signal)
        logger.info(f"Signal generated: {pattern} - {signal_type} @ {confidence:.2f}")

        return signal

    def _no_signal(self, reason: str) -> Dict[str, Any]:
        """Create a no-signal response"""
        return {
            "timestamp": datetime.now().isoformat(),
            "pair": self.pair,
            "pattern": None,
            "type": "HOLD",
            "confidence": 0.0,
            "reason": reason,
        }

    def save_signals(self, output_file: str = "signals.json") -> None:
        """Save signal history to file"""
        try:
            with open(output_file, "w") as f:
                json.dump(self.signal_history, f, indent=2)
            logger.info(f"Signals saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving signals: {e}")


def main():
    """Example usage"""
    # Sample candle data (would come from exchange API in production)
    sample_candles = [
        {"open": 50000, "high": 51000, "low": 49500, "close": 49800, "volume": 100},
        {"open": 49800, "high": 49900, "low": 48000, "close": 48500, "volume": 150},
        {"open": 48500, "high": 50000, "low": 48200, "close": 49800, "volume": 200},
    ]

    analyzer = CandlestickAnalyzer("BTC/USD")
    signal = analyzer.analyze(sample_candles)

    print(json.dumps(signal, indent=2))
    analyzer.save_signals()


if __name__ == "__main__":
    main()
