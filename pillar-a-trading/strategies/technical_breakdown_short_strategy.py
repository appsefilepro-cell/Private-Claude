#!/usr/bin/env python3
"""
TECHNICAL BREAKDOWN SHORT STRATEGY (Strategy #3)
Short when key technical levels break down

Strategy:
- Major support breaks
- Death cross (50-day MA crosses below 200-day MA)
- Head & shoulders pattern completion
- Descending triangle breakdowns
- Target 94-96% win rate
"""

import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TechnicalBreakdown')


class TechnicalBreakdownShortStrategy:
    """
    Technical Breakdown Shorting Strategy

    Shorts when:
    1. Support level breaks (confirmed)
    2. Death cross occurs (50-day < 200-day MA)
    3. Head & shoulders or double top completes
    4. Descending triangle breaks down
    5. Volume confirms breakdown
    """

    def __init__(self):
        self.criteria = {
            'support_break_confirm': 0.02,  # 2% below support = confirmed
            'volume_confirm': 1.5,  # Volume > 1.5x average
            'ma_death_cross_buffer': 0.01  # 1% buffer for death cross
        }
        logger.info("=" * 70)
        logger.info("📉 TECHNICAL BREAKDOWN SHORT STRATEGY INITIALIZED")
        logger.info("=" * 70)

    def analyze_for_short(self, symbol: str, data: Dict) -> Dict:
        """Analyze technical breakdown for shorting"""
        signal = {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 0.0,
            'strategy': 'Technical Breakdown Short',
            'reasons': [],
            'risk_level': 'medium',
            'timestamp': datetime.now().isoformat()
        }

        score = 0
        max_score = 0

        # 1. SUPPORT BREAK (35 points)
        price = data.get('price', 0)
        support_level = data.get('support_level', 0)

        if support_level > 0 and price < support_level:
            break_pct = ((support_level - price) / support_level)

            if break_pct > self.criteria['support_break_confirm']:
                score += 35
                signal['reasons'].append(f"Support broken: {break_pct * 100:.1f}% below support")
            elif break_pct > 0:
                score += 20
                signal['reasons'].append(f"Testing support: {break_pct * 100:.1f}% below")

        max_score += 35

        # 2. DEATH CROSS (30 points)
        ma_50 = data.get('ma_50', 0)
        ma_200 = data.get('ma_200', 0)

        if ma_50 > 0 and ma_200 > 0:
            ma_ratio = ma_50 / ma_200

            if ma_ratio < (1 - self.criteria['ma_death_cross_buffer']):
                score += 30
                signal['reasons'].append(f"Death cross: 50-day MA < 200-day MA")
            elif ma_ratio < 1.0:
                score += 15
                signal['reasons'].append("50-day MA approaching 200-day MA")

        max_score += 30

        # 3. BEARISH PATTERN (20 points)
        pattern = data.get('pattern', None)

        if pattern in ['head_and_shoulders', 'double_top', 'descending_triangle']:
            score += 20
            signal['reasons'].append(f"Bearish pattern: {pattern}")
        elif pattern in ['rising_wedge', 'bear_flag']:
            score += 10
            signal['reasons'].append(f"Continuation pattern: {pattern}")

        max_score += 20

        # 4. VOLUME CONFIRMATION (10 points)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)

        if avg_volume > 0:
            volume_ratio = volume / avg_volume

            if volume_ratio > self.criteria['volume_confirm']:
                score += 10
                signal['reasons'].append(f"Volume confirms breakdown: {volume_ratio:.1f}x")
            elif volume_ratio > 1.0:
                score += 5
                signal['reasons'].append("Volume increasing")

        max_score += 10

        # 5. MACD BEARISH (5 points)
        macd = data.get('macd', 'neutral')

        if macd == 'bearish' or data.get('macd_signal') == 'sell':
            score += 5
            signal['reasons'].append("MACD bearish")

        max_score += 5

        # Calculate confidence
        signal['confidence'] = (score / max_score) if max_score > 0 else 0

        # Determine action
        if signal['confidence'] >= 0.75:  # 75%+ confidence
            signal['action'] = 'SHORT'
            signal['risk_level'] = 'high_reward'
        elif signal['confidence'] >= 0.60:
            signal['action'] = 'SHORT_SMALL'
            signal['risk_level'] = 'medium'
        else:
            signal['action'] = 'HOLD'

        return signal


if __name__ == "__main__":
    strategy = TechnicalBreakdownShortStrategy()
    print("Technical Breakdown Short Strategy - Ready for backtesting")
