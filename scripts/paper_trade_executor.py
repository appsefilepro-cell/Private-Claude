#!/usr/bin/env python3
"""
Paper trading executor used by launch_9am_dual_strategy.
Simulates fills and P/L with simple probabilistic outcomes.
"""
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class PaperPosition:
    symbol: str
    side: str
    size: float
    confidence: float
    opened_at: str
    strategy: str
    reasons: List[str] = field(default_factory=list)


class PaperTradeExecutor:
    """Lightweight paper-trade simulator for short strategies."""

    def __init__(self, balance: float, risk_per_trade: float = 0.02):
        self.start_balance = balance
        self.balance = balance
        self.risk_per_trade = risk_per_trade
        self.positions: List[PaperPosition] = []
        self.realized_pnl = 0.0
        self.wins = 0
        self.losses = 0
        self.total_trades = 0

    def _position_size(self) -> float:
        return self.balance * self.risk_per_trade

    def open_short(self, signal: Dict[str, Any]) -> PaperPosition:
        size = self._position_size()
        pos = PaperPosition(
            symbol=signal.get("symbol", "UNKNOWN"),
            side=signal.get("action", "SHORT"),
            size=size,
            confidence=signal.get("confidence", 0.0),
            opened_at=datetime.now().isoformat(),
            strategy=signal.get("strategy", "unknown"),
            reasons=signal.get("reasons", [])[:5],
        )
        self.positions.append(pos)
        self.total_trades += 1
        return pos

    def close_position(self, position: PaperPosition) -> Dict[str, Any]:
        # Bias wins to the confidence score (clamped between 0 and 98%)
        win_prob = min(0.98, max(0.0, position.confidence))
        is_win = random.random() < win_prob

        # Profit/loss magnitudes are modest to reflect short-term trades
        if is_win:
            pct = random.uniform(0.015, 0.035)  # 1.5% to 3.5%
            pnl = position.size * pct
            self.wins += 1
        else:
            pct = random.uniform(0.005, 0.015)  # 0.5% to 1.5%
            pnl = -position.size * pct
            self.losses += 1

        self.balance += pnl
        self.realized_pnl += pnl
        self.positions.remove(position)

        return {
            "symbol": position.symbol,
            "strategy": position.strategy,
            "win": is_win,
            "pnl": pnl,
            "pnl_pct": pnl / max(position.size, 1e-9),
            "balance": self.balance,
        }

    def stats(self) -> Dict[str, Any]:
        total = self.total_trades
        win_rate = (self.wins / total * 100.0) if total else 0.0
        return {
            "balance": self.balance,
            "start_balance": self.start_balance,
            "realized_pnl": self.realized_pnl,
            "total_trades": total,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": win_rate,
            "open_positions": len(self.positions),
        }
