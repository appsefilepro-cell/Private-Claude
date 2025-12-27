"""
PATTERN RECOGNITION ENGINE - COMPLETE TRADING STRATEGY IMPLEMENTATION
Advanced candlestick pattern detection, confidence scoring, and backtesting
Integrates with ML models for real-time pattern scanning and strategy optimization

Role 3 of Agent X5 Implementation
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import time
import numpy as np
import pandas as pd
from collections import defaultdict, deque


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CandlestickPattern(Enum):
    """Candlestick pattern types"""
    DOJI = "doji"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    ENGULFING_BULLISH = "engulfing_bullish"
    ENGULFING_BEARISH = "engulfing_bearish"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    HARAMI_BULLISH = "harami_bullish"
    HARAMI_BEARISH = "harami_bearish"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"


class PatternStrength(Enum):
    """Pattern strength levels"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class TrendDirection(Enum):
    """Market trend direction"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


@dataclass
class Candle:
    """Single candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str

    @property
    def body(self) -> float:
        """Candle body size"""
        return abs(self.close - self.open)

    @property
    def upper_shadow(self) -> float:
        """Upper shadow length"""
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        """Lower shadow length"""
        return min(self.open, self.close) - self.low

    @property
    def is_bullish(self) -> bool:
        """Is bullish candle"""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Is bearish candle"""
        return self.close < self.open

    @property
    def total_range(self) -> float:
        """Total candle range"""
        return self.high - self.low

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'symbol': self.symbol
        }


@dataclass
class PatternMatch:
    """Detected pattern match"""
    pattern_id: str
    pattern_type: CandlestickPattern
    symbol: str
    timestamp: datetime
    confidence: float
    strength: PatternStrength
    candles: List[Candle]
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    expected_direction: Optional[TrendDirection] = None
    historical_success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'strength': self.strength.value,
            'candles': [c.to_dict() for c in self.candles],
            'price_target': self.price_target,
            'stop_loss': self.stop_loss,
            'expected_direction': self.expected_direction.value if self.expected_direction else None,
            'historical_success_rate': self.historical_success_rate,
            'metadata': self.metadata
        }


@dataclass
class BacktestResult:
    """Backtest result for a pattern"""
    pattern_type: CandlestickPattern
    total_occurrences: int
    successful_trades: int
    failed_trades: int
    success_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    total_return: float
    sharpe_ratio: float
    trades: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['pattern_type'] = self.pattern_type.value
        return data


class PatternDetector:
    """Candlestick pattern detection engine"""

    def __init__(self):
        """Initialize pattern detector"""
        self.detection_methods = {
            CandlestickPattern.DOJI: self._detect_doji,
            CandlestickPattern.HAMMER: self._detect_hammer,
            CandlestickPattern.SHOOTING_STAR: self._detect_shooting_star,
            CandlestickPattern.ENGULFING_BULLISH: self._detect_engulfing_bullish,
            CandlestickPattern.ENGULFING_BEARISH: self._detect_engulfing_bearish,
            CandlestickPattern.MORNING_STAR: self._detect_morning_star,
            CandlestickPattern.EVENING_STAR: self._detect_evening_star,
            CandlestickPattern.THREE_WHITE_SOLDIERS: self._detect_three_white_soldiers,
            CandlestickPattern.THREE_BLACK_CROWS: self._detect_three_black_crows,
            CandlestickPattern.HARAMI_BULLISH: self._detect_harami_bullish,
            CandlestickPattern.HARAMI_BEARISH: self._detect_harami_bearish,
            CandlestickPattern.PIERCING_LINE: self._detect_piercing_line,
            CandlestickPattern.DARK_CLOUD_COVER: self._detect_dark_cloud_cover,
        }

    def detect_all_patterns(self, candles: List[Candle]) -> List[PatternMatch]:
        """
        Detect all patterns in candle list

        Args:
            candles: List of candles

        Returns:
            List of detected patterns
        """
        patterns = []

        for pattern_type, detection_method in self.detection_methods.items():
            matches = detection_method(candles)
            patterns.extend(matches)

        return patterns

    def _detect_doji(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Doji patterns"""
        patterns = []

        for i in range(len(candles)):
            candle = candles[i]

            # Doji: body is very small compared to total range
            if candle.total_range == 0:
                continue

            body_ratio = candle.body / candle.total_range

            if body_ratio < 0.1:  # Body is less than 10% of range
                confidence = 1.0 - (body_ratio / 0.1)  # Higher confidence for smaller body

                pattern_id = self._generate_pattern_id('doji', candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.DOJI,
                    symbol=candle.symbol,
                    timestamp=candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[candle],
                    expected_direction=TrendDirection.SIDEWAYS,
                    metadata={'body_ratio': body_ratio}
                ))

        return patterns

    def _detect_hammer(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Hammer patterns (bullish reversal)"""
        patterns = []

        for i in range(len(candles)):
            candle = candles[i]

            if candle.total_range == 0:
                continue

            # Hammer characteristics:
            # 1. Small body at upper end
            # 2. Long lower shadow (at least 2x body)
            # 3. Little to no upper shadow

            body_ratio = candle.body / candle.total_range
            lower_shadow_ratio = candle.lower_shadow / candle.total_range
            upper_shadow_ratio = candle.upper_shadow / candle.total_range

            is_hammer = (
                body_ratio < 0.3 and
                lower_shadow_ratio > 0.6 and
                upper_shadow_ratio < 0.1
            )

            if is_hammer:
                confidence = min(lower_shadow_ratio * 1.5, 1.0)

                pattern_id = self._generate_pattern_id('hammer', candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.HAMMER,
                    symbol=candle.symbol,
                    timestamp=candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[candle],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={
                        'lower_shadow_ratio': lower_shadow_ratio,
                        'body_ratio': body_ratio
                    }
                ))

        return patterns

    def _detect_shooting_star(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Shooting Star patterns (bearish reversal)"""
        patterns = []

        for i in range(len(candles)):
            candle = candles[i]

            if candle.total_range == 0:
                continue

            # Shooting Star: opposite of hammer
            # 1. Small body at lower end
            # 2. Long upper shadow
            # 3. Little to no lower shadow

            body_ratio = candle.body / candle.total_range
            upper_shadow_ratio = candle.upper_shadow / candle.total_range
            lower_shadow_ratio = candle.lower_shadow / candle.total_range

            is_shooting_star = (
                body_ratio < 0.3 and
                upper_shadow_ratio > 0.6 and
                lower_shadow_ratio < 0.1
            )

            if is_shooting_star:
                confidence = min(upper_shadow_ratio * 1.5, 1.0)

                pattern_id = self._generate_pattern_id('shooting_star', candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.SHOOTING_STAR,
                    symbol=candle.symbol,
                    timestamp=candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[candle],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={
                        'upper_shadow_ratio': upper_shadow_ratio,
                        'body_ratio': body_ratio
                    }
                ))

        return patterns

    def _detect_engulfing_bullish(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Bullish Engulfing patterns"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Bullish Engulfing:
            # 1. Previous candle is bearish
            # 2. Current candle is bullish
            # 3. Current body completely engulfs previous body

            is_engulfing = (
                prev_candle.is_bearish and
                curr_candle.is_bullish and
                curr_candle.open < prev_candle.close and
                curr_candle.close > prev_candle.open
            )

            if is_engulfing:
                # Confidence based on size difference
                engulfing_ratio = curr_candle.body / prev_candle.body if prev_candle.body > 0 else 1.0
                confidence = min(engulfing_ratio / 2.0, 1.0)

                pattern_id = self._generate_pattern_id('engulfing_bullish', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.ENGULFING_BULLISH,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={'engulfing_ratio': engulfing_ratio}
                ))

        return patterns

    def _detect_engulfing_bearish(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Bearish Engulfing patterns"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Bearish Engulfing:
            # 1. Previous candle is bullish
            # 2. Current candle is bearish
            # 3. Current body completely engulfs previous body

            is_engulfing = (
                prev_candle.is_bullish and
                curr_candle.is_bearish and
                curr_candle.open > prev_candle.close and
                curr_candle.close < prev_candle.open
            )

            if is_engulfing:
                engulfing_ratio = curr_candle.body / prev_candle.body if prev_candle.body > 0 else 1.0
                confidence = min(engulfing_ratio / 2.0, 1.0)

                pattern_id = self._generate_pattern_id('engulfing_bearish', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.ENGULFING_BEARISH,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={'engulfing_ratio': engulfing_ratio}
                ))

        return patterns

    def _detect_morning_star(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Morning Star patterns (bullish reversal)"""
        patterns = []

        for i in range(2, len(candles)):
            candle1 = candles[i - 2]  # Bearish
            candle2 = candles[i - 1]  # Small body (star)
            candle3 = candles[i]      # Bullish

            # Morning Star:
            # 1. First candle is bearish with large body
            # 2. Second candle has small body (gap down)
            # 3. Third candle is bullish, closes above midpoint of first

            if (candle1.is_bearish and
                candle2.body < candle1.body * 0.3 and
                candle3.is_bullish and
                candle3.close > (candle1.open + candle1.close) / 2):

                confidence = 0.75 if candle2.close < candle1.close else 0.6

                pattern_id = self._generate_pattern_id('morning_star', candle3)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.MORNING_STAR,
                    symbol=candle3.symbol,
                    timestamp=candle3.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[candle1, candle2, candle3],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={'star_body_ratio': candle2.body / candle1.body}
                ))

        return patterns

    def _detect_evening_star(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Evening Star patterns (bearish reversal)"""
        patterns = []

        for i in range(2, len(candles)):
            candle1 = candles[i - 2]  # Bullish
            candle2 = candles[i - 1]  # Small body (star)
            candle3 = candles[i]      # Bearish

            # Evening Star:
            # 1. First candle is bullish with large body
            # 2. Second candle has small body (gap up)
            # 3. Third candle is bearish, closes below midpoint of first

            if (candle1.is_bullish and
                candle2.body < candle1.body * 0.3 and
                candle3.is_bearish and
                candle3.close < (candle1.open + candle1.close) / 2):

                confidence = 0.75 if candle2.close > candle1.close else 0.6

                pattern_id = self._generate_pattern_id('evening_star', candle3)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.EVENING_STAR,
                    symbol=candle3.symbol,
                    timestamp=candle3.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[candle1, candle2, candle3],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={'star_body_ratio': candle2.body / candle1.body}
                ))

        return patterns

    def _detect_three_white_soldiers(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Three White Soldiers (strong bullish)"""
        patterns = []

        for i in range(2, len(candles)):
            candle1 = candles[i - 2]
            candle2 = candles[i - 1]
            candle3 = candles[i]

            # Three White Soldiers:
            # 1. Three consecutive bullish candles
            # 2. Each opens within previous body
            # 3. Each closes higher than previous

            if (candle1.is_bullish and candle2.is_bullish and candle3.is_bullish and
                candle2.open > candle1.open and candle2.open < candle1.close and
                candle3.open > candle2.open and candle3.open < candle2.close and
                candle2.close > candle1.close and candle3.close > candle2.close):

                confidence = 0.85

                pattern_id = self._generate_pattern_id('three_white_soldiers', candle3)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.THREE_WHITE_SOLDIERS,
                    symbol=candle3.symbol,
                    timestamp=candle3.timestamp,
                    confidence=confidence,
                    strength=PatternStrength.VERY_STRONG,
                    candles=[candle1, candle2, candle3],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={'total_gain': candle3.close - candle1.open}
                ))

        return patterns

    def _detect_three_black_crows(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Three Black Crows (strong bearish)"""
        patterns = []

        for i in range(2, len(candles)):
            candle1 = candles[i - 2]
            candle2 = candles[i - 1]
            candle3 = candles[i]

            # Three Black Crows:
            # 1. Three consecutive bearish candles
            # 2. Each opens within previous body
            # 3. Each closes lower than previous

            if (candle1.is_bearish and candle2.is_bearish and candle3.is_bearish and
                candle2.open < candle1.open and candle2.open > candle1.close and
                candle3.open < candle2.open and candle3.open > candle2.close and
                candle2.close < candle1.close and candle3.close < candle2.close):

                confidence = 0.85

                pattern_id = self._generate_pattern_id('three_black_crows', candle3)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.THREE_BLACK_CROWS,
                    symbol=candle3.symbol,
                    timestamp=candle3.timestamp,
                    confidence=confidence,
                    strength=PatternStrength.VERY_STRONG,
                    candles=[candle1, candle2, candle3],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={'total_loss': candle1.open - candle3.close}
                ))

        return patterns

    def _detect_harami_bullish(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Bullish Harami patterns"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Bullish Harami:
            # 1. Previous candle is bearish with large body
            # 2. Current candle is bullish with small body
            # 3. Current body is within previous body

            if (prev_candle.is_bearish and curr_candle.is_bullish and
                curr_candle.open > prev_candle.close and
                curr_candle.close < prev_candle.open and
                curr_candle.body < prev_candle.body * 0.5):

                confidence = 0.65

                pattern_id = self._generate_pattern_id('harami_bullish', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.HARAMI_BULLISH,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={'body_ratio': curr_candle.body / prev_candle.body}
                ))

        return patterns

    def _detect_harami_bearish(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Bearish Harami patterns"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Bearish Harami:
            # 1. Previous candle is bullish with large body
            # 2. Current candle is bearish with small body
            # 3. Current body is within previous body

            if (prev_candle.is_bullish and curr_candle.is_bearish and
                curr_candle.open < prev_candle.close and
                curr_candle.close > prev_candle.open and
                curr_candle.body < prev_candle.body * 0.5):

                confidence = 0.65

                pattern_id = self._generate_pattern_id('harami_bearish', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.HARAMI_BEARISH,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={'body_ratio': curr_candle.body / prev_candle.body}
                ))

        return patterns

    def _detect_piercing_line(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Piercing Line patterns (bullish reversal)"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Piercing Line:
            # 1. Previous candle is bearish
            # 2. Current candle is bullish
            # 3. Current opens below previous low
            # 4. Current closes above midpoint of previous body

            midpoint = (prev_candle.open + prev_candle.close) / 2

            if (prev_candle.is_bearish and curr_candle.is_bullish and
                curr_candle.open < prev_candle.low and
                curr_candle.close > midpoint and
                curr_candle.close < prev_candle.open):

                confidence = 0.70

                pattern_id = self._generate_pattern_id('piercing_line', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.PIERCING_LINE,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BULLISH,
                    metadata={'penetration': curr_candle.close - midpoint}
                ))

        return patterns

    def _detect_dark_cloud_cover(self, candles: List[Candle]) -> List[PatternMatch]:
        """Detect Dark Cloud Cover patterns (bearish reversal)"""
        patterns = []

        for i in range(1, len(candles)):
            prev_candle = candles[i - 1]
            curr_candle = candles[i]

            # Dark Cloud Cover:
            # 1. Previous candle is bullish
            # 2. Current candle is bearish
            # 3. Current opens above previous high
            # 4. Current closes below midpoint of previous body

            midpoint = (prev_candle.open + prev_candle.close) / 2

            if (prev_candle.is_bullish and curr_candle.is_bearish and
                curr_candle.open > prev_candle.high and
                curr_candle.close < midpoint and
                curr_candle.close > prev_candle.open):

                confidence = 0.70

                pattern_id = self._generate_pattern_id('dark_cloud_cover', curr_candle)

                patterns.append(PatternMatch(
                    pattern_id=pattern_id,
                    pattern_type=CandlestickPattern.DARK_CLOUD_COVER,
                    symbol=curr_candle.symbol,
                    timestamp=curr_candle.timestamp,
                    confidence=confidence,
                    strength=self._calculate_strength(confidence),
                    candles=[prev_candle, curr_candle],
                    expected_direction=TrendDirection.BEARISH,
                    metadata={'penetration': midpoint - curr_candle.close}
                ))

        return patterns

    def _calculate_strength(self, confidence: float) -> PatternStrength:
        """Calculate pattern strength from confidence"""
        if confidence >= 0.8:
            return PatternStrength.VERY_STRONG
        elif confidence >= 0.65:
            return PatternStrength.STRONG
        elif confidence >= 0.5:
            return PatternStrength.MODERATE
        else:
            return PatternStrength.WEAK

    def _generate_pattern_id(self, pattern_name: str, candle: Candle) -> str:
        """Generate unique pattern ID"""
        data = f"{pattern_name}_{candle.symbol}_{candle.timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


class HistoricalPatternTracker:
    """Track historical pattern performance"""

    def __init__(self, storage_file: str = "/tmp/pattern_history.json"):
        """
        Initialize historical tracker

        Args:
            storage_file: File to store pattern history
        """
        self.storage_file = storage_file
        self.pattern_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'avg_profit': 0.0,
            'avg_loss': 0.0
        })
        self.load_history()

    def load_history(self):
        """Load pattern history from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.pattern_stats.update(data)
                logger.info(f"Loaded pattern history: {len(self.pattern_stats)} patterns")
            except Exception as e:
                logger.error(f"Error loading history: {e}")

    def save_history(self):
        """Save pattern history to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(dict(self.pattern_stats), f, indent=2)
            logger.info("Pattern history saved")
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def record_pattern_outcome(
        self,
        pattern_type: CandlestickPattern,
        success: bool,
        profit_loss: float
    ):
        """
        Record pattern outcome

        Args:
            pattern_type: Pattern type
            success: Whether pattern was successful
            profit_loss: Profit or loss amount
        """
        key = pattern_type.value
        stats = self.pattern_stats[key]

        stats['total'] += 1

        if success:
            stats['successful'] += 1
            # Update average profit
            prev_avg = stats['avg_profit']
            stats['avg_profit'] = (
                (prev_avg * (stats['successful'] - 1) + profit_loss) / stats['successful']
            )
        else:
            stats['failed'] += 1
            # Update average loss
            prev_avg = stats['avg_loss']
            stats['avg_loss'] = (
                (prev_avg * (stats['failed'] - 1) + abs(profit_loss)) / stats['failed']
            )

        self.save_history()

    def get_success_rate(self, pattern_type: CandlestickPattern) -> float:
        """Get historical success rate for pattern"""
        stats = self.pattern_stats[pattern_type.value]
        if stats['total'] == 0:
            return 0.5  # Default 50% if no history

        return stats['successful'] / stats['total']

    def get_profit_factor(self, pattern_type: CandlestickPattern) -> float:
        """Get profit factor for pattern"""
        stats = self.pattern_stats[pattern_type.value]
        if stats['avg_loss'] == 0:
            return 0.0

        return stats['avg_profit'] / stats['avg_loss']

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get all pattern statistics"""
        return dict(self.pattern_stats)


class BacktestingEngine:
    """Backtesting framework for pattern strategies"""

    def __init__(self, historical_tracker: HistoricalPatternTracker):
        """
        Initialize backtesting engine

        Args:
            historical_tracker: Historical pattern tracker
        """
        self.tracker = historical_tracker

    async def backtest_pattern(
        self,
        pattern_type: CandlestickPattern,
        candles: List[Candle],
        holding_period: int = 10,
        profit_target: float = 0.02,  # 2%
        stop_loss: float = 0.01  # 1%
    ) -> BacktestResult:
        """
        Backtest a specific pattern

        Args:
            pattern_type: Pattern to backtest
            candles: Historical candle data
            holding_period: Number of candles to hold
            profit_target: Profit target percentage
            stop_loss: Stop loss percentage

        Returns:
            Backtest results
        """
        detector = PatternDetector()
        patterns = detector.detect_all_patterns(candles)

        # Filter for specific pattern type
        patterns = [p for p in patterns if p.pattern_type == pattern_type]

        trades = []
        total_profit = 0.0
        successful = 0
        failed = 0

        for pattern in patterns:
            # Find entry candle index
            entry_index = None
            for i, candle in enumerate(candles):
                if candle.timestamp == pattern.timestamp:
                    entry_index = i
                    break

            if entry_index is None or entry_index + holding_period >= len(candles):
                continue

            entry_price = candles[entry_index].close
            exit_price = None
            exit_reason = None

            # Simulate holding period
            for i in range(entry_index + 1, min(entry_index + holding_period + 1, len(candles))):
                candle = candles[i]

                if pattern.expected_direction == TrendDirection.BULLISH:
                    # Check profit target
                    if candle.high >= entry_price * (1 + profit_target):
                        exit_price = entry_price * (1 + profit_target)
                        exit_reason = 'profit_target'
                        break

                    # Check stop loss
                    if candle.low <= entry_price * (1 - stop_loss):
                        exit_price = entry_price * (1 - stop_loss)
                        exit_reason = 'stop_loss'
                        break

                elif pattern.expected_direction == TrendDirection.BEARISH:
                    # For bearish, we short (profit when price goes down)
                    if candle.low <= entry_price * (1 - profit_target):
                        exit_price = entry_price * (1 - profit_target)
                        exit_reason = 'profit_target'
                        break

                    if candle.high >= entry_price * (1 + stop_loss):
                        exit_price = entry_price * (1 + stop_loss)
                        exit_reason = 'stop_loss'
                        break

            # If no exit, use end of holding period
            if exit_price is None:
                exit_price = candles[min(entry_index + holding_period, len(candles) - 1)].close
                exit_reason = 'holding_period_end'

            # Calculate profit/loss
            if pattern.expected_direction == TrendDirection.BULLISH:
                pnl = (exit_price - entry_price) / entry_price
            else:  # Bearish (short)
                pnl = (entry_price - exit_price) / entry_price

            trade_success = pnl > 0
            if trade_success:
                successful += 1
            else:
                failed += 1

            total_profit += pnl

            trades.append({
                'entry_time': pattern.timestamp.isoformat(),
                'entry_price': entry_price,
                'exit_price': exit_price,
                'exit_reason': exit_reason,
                'pnl': pnl,
                'pnl_percent': pnl * 100,
                'success': trade_success
            })

        # Calculate metrics
        total_occurrences = len(patterns)
        success_rate = successful / total_occurrences if total_occurrences > 0 else 0.0

        winning_trades = [t for t in trades if t['success']]
        losing_trades = [t for t in trades if not t['success']]

        avg_profit = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0.0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 0.0

        profit_factor = avg_profit / avg_loss if avg_loss > 0 else 0.0

        # Calculate max drawdown
        cumulative_returns = np.cumsum([t['pnl'] for t in trades]) if trades else [0]
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = running_max - cumulative_returns
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0.0

        # Calculate Sharpe ratio (simplified)
        returns = [t['pnl'] for t in trades] if trades else [0]
        sharpe_ratio = (
            np.mean(returns) / np.std(returns)
            if len(returns) > 1 and np.std(returns) > 0
            else 0.0
        )

        return BacktestResult(
            pattern_type=pattern_type,
            total_occurrences=total_occurrences,
            successful_trades=successful,
            failed_trades=failed,
            success_rate=success_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            total_return=total_profit,
            sharpe_ratio=sharpe_ratio,
            trades=trades
        )

    async def backtest_all_patterns(
        self,
        candles: List[Candle]
    ) -> Dict[str, BacktestResult]:
        """
        Backtest all patterns

        Args:
            candles: Historical candle data

        Returns:
            Dictionary of backtest results by pattern type
        """
        results = {}

        for pattern_type in CandlestickPattern:
            logger.info(f"Backtesting {pattern_type.value}...")
            result = await self.backtest_pattern(pattern_type, candles)
            results[pattern_type.value] = result

        return results


class RealTimeScanner:
    """Real-time pattern scanning engine"""

    def __init__(self, detector: PatternDetector, tracker: HistoricalPatternTracker):
        """
        Initialize real-time scanner

        Args:
            detector: Pattern detector
            tracker: Historical pattern tracker
        """
        self.detector = detector
        self.tracker = tracker
        self.candle_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.active_patterns: List[PatternMatch] = []

    def add_candle(self, candle: Candle):
        """
        Add new candle to buffer

        Args:
            candle: New candle data
        """
        self.candle_buffer[candle.symbol].append(candle)

    def scan_for_patterns(self, symbol: str, min_confidence: float = 0.6) -> List[PatternMatch]:
        """
        Scan for patterns in symbol

        Args:
            symbol: Trading symbol
            min_confidence: Minimum confidence threshold

        Returns:
            List of detected patterns
        """
        if symbol not in self.candle_buffer:
            return []

        candles = list(self.candle_buffer[symbol])
        if len(candles) < 3:
            return []

        # Detect patterns
        patterns = self.detector.detect_all_patterns(candles)

        # Filter by confidence and add historical success rate
        filtered_patterns = []
        for pattern in patterns:
            if pattern.confidence >= min_confidence:
                # Add historical success rate
                pattern.historical_success_rate = self.tracker.get_success_rate(
                    pattern.pattern_type
                )
                filtered_patterns.append(pattern)

        # Update active patterns
        self.active_patterns = filtered_patterns

        return filtered_patterns


class PatternRecognitionEngine:
    """Main pattern recognition engine"""

    def __init__(self, storage_dir: str = "/tmp/pattern_recognition"):
        """
        Initialize pattern recognition engine

        Args:
            storage_dir: Directory for storing data
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        self.detector = PatternDetector()
        self.tracker = HistoricalPatternTracker(
            os.path.join(storage_dir, "pattern_history.json")
        )
        self.backtester = BacktestingEngine(self.tracker)
        self.scanner = RealTimeScanner(self.detector, self.tracker)

    async def analyze_candles(
        self,
        candles: List[Candle],
        min_confidence: float = 0.6
    ) -> Dict[str, Any]:
        """
        Analyze candles for patterns

        Args:
            candles: List of candles
            min_confidence: Minimum confidence threshold

        Returns:
            Analysis results
        """
        patterns = self.detector.detect_all_patterns(candles)

        # Filter by confidence
        filtered_patterns = [
            p for p in patterns
            if p.confidence >= min_confidence
        ]

        # Add historical data
        for pattern in filtered_patterns:
            pattern.historical_success_rate = self.tracker.get_success_rate(
                pattern.pattern_type
            )

        # Group by type
        by_type = defaultdict(list)
        for pattern in filtered_patterns:
            by_type[pattern.pattern_type.value].append(pattern)

        return {
            'total_patterns': len(filtered_patterns),
            'patterns_by_type': {k: len(v) for k, v in by_type.items()},
            'patterns': [p.to_dict() for p in filtered_patterns],
            'highest_confidence': max([p.confidence for p in filtered_patterns]) if filtered_patterns else 0.0
        }

    async def run_backtest(
        self,
        candles: List[Candle],
        pattern_type: Optional[CandlestickPattern] = None
    ) -> Dict[str, Any]:
        """
        Run backtest

        Args:
            candles: Historical candles
            pattern_type: Specific pattern or None for all

        Returns:
            Backtest results
        """
        if pattern_type:
            result = await self.backtester.backtest_pattern(pattern_type, candles)
            return {pattern_type.value: result.to_dict()}
        else:
            results = await self.backtester.backtest_all_patterns(candles)
            return {k: v.to_dict() for k, v in results.items()}

    def get_pattern_statistics(self) -> Dict[str, Dict]:
        """Get all pattern statistics"""
        return self.tracker.get_all_stats()


# Example usage
async def main():
    """Example usage of Pattern Recognition Engine"""

    # Initialize engine
    engine = PatternRecognitionEngine()

    # Generate sample candles
    print("📊 Generating sample candle data...")
    candles = []
    base_price = 50000.0

    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=100-i)

        # Simulate price movement
        trend = np.sin(i / 10) * 1000
        noise = np.random.randn() * 500

        open_price = base_price + trend + noise
        close_price = open_price + np.random.randn() * 200
        high_price = max(open_price, close_price) + abs(np.random.randn() * 100)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 100)
        volume = abs(np.random.randn() * 10000)

        candles.append(Candle(
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
            symbol='BTCUSDT'
        ))

    # Analyze patterns
    print("\n🔍 Analyzing patterns...")
    analysis = await engine.analyze_candles(candles, min_confidence=0.6)

    print(f"\n✓ Pattern Analysis Complete:")
    print(f"  Total Patterns: {analysis['total_patterns']}")
    print(f"  Patterns by Type:")
    for pattern_type, count in analysis['patterns_by_type'].items():
        print(f"    - {pattern_type}: {count}")
    print(f"  Highest Confidence: {analysis['highest_confidence']:.2%}")

    # Run backtest
    print("\n📈 Running backtest...")
    backtest_results = await engine.run_backtest(candles)

    print(f"\n✓ Backtest Results:")
    for pattern_type, result in backtest_results.items():
        if result['total_occurrences'] > 0:
            print(f"\n  {pattern_type.upper()}:")
            print(f"    Occurrences: {result['total_occurrences']}")
            print(f"    Success Rate: {result['success_rate']:.2%}")
            print(f"    Profit Factor: {result['profit_factor']:.2f}")
            print(f"    Total Return: {result['total_return']:.2%}")

    # Get statistics
    print("\n📊 Pattern Statistics:")
    stats = engine.get_pattern_statistics()
    for pattern_type, stat in stats.items():
        if stat['total'] > 0:
            print(f"\n  {pattern_type.upper()}:")
            print(f"    Total: {stat['total']}")
            print(f"    Success Rate: {stat['successful']/stat['total']:.2%}")
            print(f"    Avg Profit: {stat['avg_profit']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
