#!/usr/bin/env python3
"""
THE BIG SHORT STRATEGY
Main trading strategy focused on shorting overvalued assets

Inspired by: The Big Short (2008 Financial Crisis)
Strategy: Find overvalued, overleveraged, bubble assets and SHORT them

Targets:
- Overvalued stocks (P/E > 50, P/B > 10)
- Bubble sectors (tech, crypto during euphoria)
- Overleveraged companies (Debt/Equity > 3)
- Fraud indicators (unusual accounting)
- Market euphoria peaks (VIX < 12, extreme greed)
"""

import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BigShort')


class BigShortStrategy:
    """
    The Big Short - Professional Shorting Strategy

    Identifies and shorts:
    1. Overvalued stocks (fundamentals)
    2. Technical overbought (RSI > 70, MACD bearish)
    3. Market euphoria peaks (sentiment extreme)
    4. Fraud/accounting red flags
    5. Sector bubbles
    """

    def __init__(self):
        self.watchlist = []
        self.active_shorts = []
        self.criteria = {
            'pe_ratio_max': 50,  # P/E above this = overvalued
            'pb_ratio_max': 10,   # P/B above this = overvalued
            'debt_equity_min': 3,  # D/E above this = overleveraged
            'rsi_overbought': 70,  # RSI above this = overbought
            'vix_euphoria': 12    # VIX below this = market euphoria
        }
        logger.info("=" * 70)
        logger.info("📉 BIG SHORT STRATEGY INITIALIZED")
        logger.info("   Finding overvalued assets to SHORT...")
        logger.info("=" * 70)

    def analyze_for_short(self, symbol: str, data: Dict) -> Dict:
        """
        Analyze if symbol is a good SHORT candidate

        Returns signal with confidence 0-100%
        """
        signal = {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 0.0,
            'strategy': 'Big Short',
            'reasons': [],
            'risk_level': 'medium',
            'timestamp': datetime.now().isoformat()
        }

        score = 0
        max_score = 0

        # 1. FUNDAMENTAL OVERVALUATION (40 points)
        pe_ratio = data.get('pe_ratio', 20)
        pb_ratio = data.get('pb_ratio', 3)
        debt_equity = data.get('debt_equity', 1)

        # Handle 'N/A' or string values
        try:
            pe_ratio = float(pe_ratio) if pe_ratio not in ['N/A', None] else 999  # Assume very high if N/A
        except (ValueError, TypeError):
            pe_ratio = 999

        try:
            pb_ratio = float(pb_ratio) if pb_ratio not in ['N/A', None] else 0
        except (ValueError, TypeError):
            pb_ratio = 0

        try:
            debt_equity = float(debt_equity) if debt_equity not in ['N/A', None, 'Unknown (fraud)'] else 0
        except (ValueError, TypeError):
            debt_equity = 0

        if pe_ratio > self.criteria['pe_ratio_max']:
            score += 15
            signal['reasons'].append(f"Extremely high P/E: {pe_ratio if pe_ratio < 999 else 'N/A (no earnings)'} (overvalued)")

        if pb_ratio > self.criteria['pb_ratio_max']:
            score += 10
            signal['reasons'].append(f"High P/B ratio: {pb_ratio} (bubble territory)")

        if debt_equity > self.criteria['debt_equity_min']:
            score += 15
            signal['reasons'].append(f"Overleveraged: D/E = {debt_equity}")

        max_score += 40

        # 2. TECHNICAL OVERBOUGHT (30 points)
        rsi = data.get('rsi', 50)
        macd = data.get('macd', 'neutral')

        if rsi > self.criteria['rsi_overbought']:
            score += 15
            signal['reasons'].append(f"Overbought: RSI = {rsi}")

        if macd == 'bearish' or data.get('macd_signal') == 'sell':
            score += 15
            signal['reasons'].append("MACD bearish divergence")

        max_score += 30

        # 3. MARKET SENTIMENT (20 points)
        vix = data.get('vix', 20)
        news_sentiment = data.get('news_sentiment', 'neutral')
        social_sentiment = data.get('social_sentiment', 'neutral')

        if vix < self.criteria['vix_euphoria']:
            score += 10
            signal['reasons'].append(f"Market euphoria: VIX = {vix} (too low)")

        if news_sentiment == 'extremely_bullish' or social_sentiment == 'euphoric':
            score += 10
            signal['reasons'].append("Extreme bullish sentiment (contrarian indicator)")

        max_score += 20

        # 4. ACCOUNTING RED FLAGS (10 points)
        revenue_growth = data.get('revenue_growth', 0)
        earnings_quality = data.get('earnings_quality', 'normal')

        if revenue_growth < 0 and pe_ratio > 30:
            score += 5
            signal['reasons'].append("Declining revenue but high valuation")

        if earnings_quality == 'suspicious' or data.get('accounting_irregularities', False):
            score += 5
            signal['reasons'].append("Accounting red flags detected")

        max_score += 10

        # Calculate final confidence
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

        logger.info(f"📉 SHORT Analysis for {symbol}:")
        logger.info(f"   Action: {signal['action']}")
        logger.info(f"   Confidence: {signal['confidence']:.2%}")
        logger.info(f"   Score: {score}/{max_score}")

        return signal

    def find_short_opportunities(self, market_data: List[Dict]) -> List[Dict]:
        """
        Scan entire market for SHORT opportunities

        Input: List of stocks with fundamental and technical data
        Output: Ranked list of best shorts
        """
        logger.info("🔍 Scanning market for SHORT opportunities...")

        opportunities = []

        for stock_data in market_data:
            symbol = stock_data.get('symbol', 'UNKNOWN')
            signal = self.analyze_for_short(symbol, stock_data)

            if signal['action'] in ['SHORT', 'SHORT_SMALL']:
                opportunities.append(signal)

        # Sort by confidence (highest first)
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        logger.info(f"✅ Found {len(opportunities)} SHORT opportunities")

        return opportunities

    def calculate_position_size(self, account_balance: float, confidence: float, risk_per_trade: float = 0.02) -> Dict:
        """
        Calculate optimal position size for SHORT

        Conservative sizing:
        - High confidence (>90%): 2% of account
        - Medium confidence (75-90%): 1% of account
        - Low confidence (<75%): 0.5% of account
        """
        if confidence >= 0.90:
            position_size = account_balance * risk_per_trade
            leverage = 1  # No leverage for shorts
        elif confidence >= 0.75:
            position_size = account_balance * (risk_per_trade * 0.5)
            leverage = 1
        else:
            position_size = account_balance * (risk_per_trade * 0.25)
            leverage = 1

        return {
            'position_size': position_size,
            'leverage': leverage,
            'max_loss': position_size * 0.1,  # 10% stop loss
            'shares_to_short': 0  # Calculate based on stock price
        }


def main():
    """Demo of Big Short Strategy"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                  THE BIG SHORT STRATEGY                           ║
    ║         Professional Shorting of Overvalued Assets                ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    strategy = BigShortStrategy()

    # Example: Analyze potentially overvalued stock
    test_data = {
        'symbol': 'OVERVALUED_STOCK',
        'pe_ratio': 85,  # Very high!
        'pb_ratio': 12,   # Bubble territory
        'debt_equity': 4.5,  # Overleveraged
        'rsi': 78,  # Overbought
        'macd': 'bearish',
        'vix': 11,  # Market euphoria
        'news_sentiment': 'extremely_bullish',
        'revenue_growth': -5,  # Declining!
        'accounting_irregularities': True
    }

    print("\n📊 Analyzing Test Stock:")
    print("=" * 70)
    signal = strategy.analyze_for_short('OVERVALUED_STOCK', test_data)

    print(f"\nAction: {signal['action']}")
    print(f"Confidence: {signal['confidence']:.2%}")
    print(f"Risk Level: {signal['risk_level']}")
    print(f"\nReasons to SHORT:")
    for reason in signal['reasons']:
        print(f"  • {reason}")

    # Calculate position size
    account_balance = 10000
    position_info = strategy.calculate_position_size(account_balance, signal['confidence'])

    print(f"\n💰 Position Sizing (${account_balance:,} account):")
    print(f"   Position Size: ${position_info['position_size']:,.2f}")
    print(f"   Max Loss: ${position_info['max_loss']:,.2f}")


if __name__ == "__main__":
    main()
