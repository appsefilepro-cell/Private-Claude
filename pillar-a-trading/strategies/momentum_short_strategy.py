#!/usr/bin/env python3
"""
MOMENTUM SHORT STRATEGY (Strategy #2)
Short when momentum reverses from extreme highs

Strategy:
- Identify extreme upward momentum
- Wait for reversal signals
- Short on momentum breakdown
- Target 94-96% win rate
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MomentumShort')


class MomentumShortStrategy:
    """
    Momentum Reversal Shorting Strategy

    Shorts when:
    1. RSI > 80 (extreme overbought)
    2. Price > 200% of 50-day moving average
    3. Volume spike (3x average volume)
    4. Bearish divergence (price up, RSI down)
    5. Failed breakout (new high but closes lower)
    """

    def __init__(self):
        self.criteria = {
            'rsi_extreme': 80,  # RSI above this = extreme
            'price_ma_ratio': 2.0,  # Price > 200% of MA = extended
            'volume_spike': 3.0,  # Volume > 3x average
            'momentum_threshold': 0.15  # 15% momentum reversal
        }
        logger.info("=" * 70)
        logger.info("📉 MOMENTUM SHORT STRATEGY INITIALIZED")
        logger.info("=" * 70)

    def analyze_for_short(self, symbol: str, data: Dict) -> Dict:
        """Analyze momentum for shorting opportunity"""
        signal = {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 0.0,
            'strategy': 'Momentum Short',
            'reasons': [],
            'risk_level': 'medium',
            'timestamp': datetime.now().isoformat()
        }

        score = 0
        max_score = 0

        # 1. EXTREME OVERBOUGHT (30 points)
        rsi = data.get('rsi', 50)
        if rsi > self.criteria['rsi_extreme']:
            score += 30
            signal['reasons'].append(f"Extreme overbought: RSI = {rsi}")
        elif rsi > 70:
            score += 15
            signal['reasons'].append(f"Overbought: RSI = {rsi}")
        max_score += 30

        # 2. PRICE EXTENSION (25 points)
        price = data.get('price', 0)
        ma_50 = data.get('ma_50', price)
        if ma_50 > 0:
            price_ma_ratio = price / ma_50
            if price_ma_ratio > self.criteria['price_ma_ratio']:
                score += 25
                signal['reasons'].append(f"Extreme extension: {price_ma_ratio:.2f}x above 50-day MA")
            elif price_ma_ratio > 1.5:
                score += 15
                signal['reasons'].append(f"Extended: {price_ma_ratio:.2f}x above 50-day MA")
        max_score += 25

        # 3. VOLUME SPIKE (20 points)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > self.criteria['volume_spike']:
                score += 20
                signal['reasons'].append(f"Volume spike: {volume_ratio:.1f}x average")
            elif volume_ratio > 2.0:
                score += 10
                signal['reasons'].append(f"High volume: {volume_ratio:.1f}x average")
        max_score += 20

        # 4. BEARISH DIVERGENCE (15 points)
        if data.get('bearish_divergence', False):
            score += 15
            signal['reasons'].append("Bearish divergence detected")
        max_score += 15

        # 5. FAILED BREAKOUT (10 points)
        if data.get('failed_breakout', False):
            score += 10
            signal['reasons'].append("Failed breakout pattern")
        max_score += 10

        # Calculate confidence
        signal['confidence'] = (score / max_score) if max_score > 0 else 0

        # Determine action
        if signal['confidence'] >= 0.80:  # 80%+ confidence
            signal['action'] = 'SHORT'
            signal['risk_level'] = 'high_reward'
        elif signal['confidence'] >= 0.65:
            signal['action'] = 'SHORT_SMALL'
            signal['risk_level'] = 'medium'
        else:
            signal['action'] = 'HOLD'

        return signal


if __name__ == "__main__":
    strategy = MomentumShortStrategy()
    print("Momentum Short Strategy - Ready for backtesting")
