"""
24-Hour Backtesting Engine
Tests trading strategies against historical data across beginner, novice, and advanced profiles
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BacktestEngine")


class BacktestingEngine:
    """
    Comprehensive backtesting engine for Agent X2.0 trading strategies
    Supports paper, sandbox, and live environment simulation
    """

    def __init__(self, profile: str = "beginner"):
        """Initialize backtesting engine with specified risk profile"""
        self.profile_name = profile
        self.config = self.load_risk_profile(profile)
        self.trades = []
        self.performance_metrics = {}
        self.initial_capital = 10000
        self.current_capital = self.initial_capital
        logger.info(f"Backtesting Engine initialized - Profile: {profile}")

    def load_risk_profile(self, profile: str) -> Dict[str, Any]:
        """Load risk profile configuration"""
        config_path = (
            Path(__file__).parent.parent / "config" / "trading_risk_profiles.json"
        )

        if not config_path.exists():
            logger.error(f"Risk profile config not found: {config_path}")
            return {}

        with open(config_path, "r") as f:
            all_profiles = json.load(f)

        if profile not in all_profiles["profiles"]:
            logger.error(f"Profile '{profile}' not found")
            return {}

        return all_profiles["profiles"][profile]

    def generate_test_data(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        Generate simulated market data for testing
        In production, this would fetch real historical data from Kraken API
        """
        test_data = []
        base_price = 50000  # Starting BTC price

        # Generate hourly candles for specified days
        for hour in range(days * 24):
            # Simulate price movement
            price_change = (
                hash(str(hour)) % 1000 - 500
            ) / 100  # Random-ish price change
            open_price = base_price
            close_price = base_price + price_change
            high_price = max(open_price, close_price) + abs(price_change) * 0.5
            low_price = min(open_price, close_price) - abs(price_change) * 0.5

            candle = {
                "timestamp": datetime.now() - timedelta(hours=(days * 24 - hour)),
                "pair": "BTC/USD",
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": 100 + (hash(str(hour + 1000)) % 500),
            }

            test_data.append(candle)
            base_price = close_price

        return test_data

    def detect_pattern(self, candles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Simplified pattern detection for backtesting
        In production, uses full candlestick_analyzer.py
        """
        if len(candles) < 3:
            return None

        current = candles[-1]
        prev = candles[-2]

        # Simple hammer pattern detection
        body = abs(current["close"] - current["open"])
        lower_shadow = min(current["open"], current["close"]) - current["low"]
        upper_shadow = current["high"] - max(current["open"], current["close"])

        if lower_shadow >= 2 * body and upper_shadow <= 0.1 * body:
            return {
                "pattern": "HAMMER",
                "confidence": 0.75,
                "signal": "BUY",
                "price": current["close"],
            }

        # Simple shooting star pattern
        if upper_shadow >= 2 * body and lower_shadow <= 0.1 * body:
            return {
                "pattern": "SHOOTING_STAR",
                "confidence": 0.75,
                "signal": "SELL",
                "price": current["close"],
            }

        return None

    def should_execute_trade(self, signal: Dict[str, Any]) -> bool:
        """Check if trade meets profile criteria"""
        if not signal:
            return False

        # Check confidence threshold
        risk_params = self.config.get("risk_parameters", {})
        confidence_threshold = risk_params.get("confidence_threshold", 0.75)

        if signal["confidence"] < confidence_threshold:
            return False

        # Check pattern is enabled
        patterns_enabled = self.config.get("patterns_enabled", [])
        if signal["pattern"] not in patterns_enabled:
            return False

        # Check daily trade limit
        max_trades_per_day = self.config.get("max_trades_per_day", 10)
        today_trades = [
            t for t in self.trades if t["date"].date() == datetime.now().date()
        ]
        if len(today_trades) >= max_trades_per_day:
            return False

        return True

    def execute_trade(
        self, signal: Dict[str, Any], candle: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a simulated trade"""
        risk_params = self.config.get("risk_parameters", {})

        # Calculate position size
        max_position_size = risk_params.get("max_position_size", 0.01)
        position_value = self.current_capital * max_position_size
        price = signal["price"]
        quantity = position_value / price

        # Calculate stop loss and take profit
        stop_loss_pct = self.config.get("stop_loss_percentage", 0.02)
        take_profit_pct = self.config.get("take_profit_percentage", 0.04)

        if signal["signal"] == "BUY":
            stop_loss = price * (1 - stop_loss_pct)
            take_profit = price * (1 + take_profit_pct)
        else:
            stop_loss = price * (1 + stop_loss_pct)
            take_profit = price * (1 - take_profit_pct)

        trade = {
            "id": len(self.trades) + 1,
            "date": candle["timestamp"],
            "pair": candle["pair"],
            "pattern": signal["pattern"],
            "signal": signal["signal"],
            "entry_price": price,
            "quantity": quantity,
            "position_value": position_value,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "OPEN",
            "exit_price": None,
            "profit_loss": 0,
            "profit_loss_pct": 0,
        }

        self.trades.append(trade)
        logger.info(
            f"Trade #{trade['id']}: {signal['signal']} {signal['pattern']} @ ${price:.2f}"
        )

        return trade

    def check_open_trades(self, candle: Dict[str, Any]):
        """Check and close open trades based on stop loss / take profit"""
        for trade in self.trades:
            if trade["status"] != "OPEN":
                continue

            current_price = candle["close"]

            # Check stop loss
            if trade["signal"] == "BUY" and current_price <= trade["stop_loss"]:
                self.close_trade(trade, current_price, "STOP_LOSS")
            elif trade["signal"] == "SELL" and current_price >= trade["stop_loss"]:
                self.close_trade(trade, current_price, "STOP_LOSS")

            # Check take profit
            elif trade["signal"] == "BUY" and current_price >= trade["take_profit"]:
                self.close_trade(trade, current_price, "TAKE_PROFIT")
            elif trade["signal"] == "SELL" and current_price <= trade["take_profit"]:
                self.close_trade(trade, current_price, "TAKE_PROFIT")

    def close_trade(self, trade: Dict[str, Any], exit_price: float, reason: str):
        """Close an open trade"""
        trade["status"] = "CLOSED"
        trade["exit_price"] = exit_price
        trade["close_reason"] = reason

        if trade["signal"] == "BUY":
            profit_loss = (exit_price - trade["entry_price"]) * trade["quantity"]
        else:
            profit_loss = (trade["entry_price"] - exit_price) * trade["quantity"]

        trade["profit_loss"] = profit_loss
        trade["profit_loss_pct"] = (profit_loss / trade["position_value"]) * 100

        self.current_capital += profit_loss

        logger.info(
            f"Trade #{trade['id']} CLOSED - {reason}: P/L ${profit_loss:.2f} ({trade['profit_loss_pct']:.2f}%)"
        )

    def run_backtest(self, days: int = 1) -> Dict[str, Any]:
        """Run complete backtest simulation"""
        logger.info(f"=" * 70)
        logger.info(
            f"STARTING {days}-DAY BACKTEST - Profile: {self.profile_name.upper()}"
        )
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"=" * 70)

        # Generate test data
        market_data = self.generate_test_data(days)
        logger.info(f"Generated {len(market_data)} hourly candles ({days} days)")

        # Process each candle
        for i, candle in enumerate(market_data):
            # Check open trades
            self.check_open_trades(candle)

            # Look for new patterns (need at least 3 candles)
            if i >= 2:
                recent_candles = market_data[max(0, i - 10) : i + 1]
                signal = self.detect_pattern(recent_candles)

                if signal and self.should_execute_trade(signal):
                    self.execute_trade(signal, candle)

        # Close any remaining open trades at final price
        final_candle = market_data[-1]
        for trade in self.trades:
            if trade["status"] == "OPEN":
                self.close_trade(trade, final_candle["close"], "BACKTEST_END")

        # Calculate performance metrics
        self.calculate_performance_metrics()

        return self.performance_metrics

    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            logger.warning("No trades executed during backtest")
            self.performance_metrics = {
                "total_trades": 0,
                "message": "No trades executed",
            }
            return

        winning_trades = [t for t in self.trades if t["profit_loss"] > 0]
        losing_trades = [t for t in self.trades if t["profit_loss"] < 0]

        total_profit = sum(t["profit_loss"] for t in winning_trades)
        total_loss = abs(sum(t["profit_loss"] for t in losing_trades))

        net_profit = self.current_capital - self.initial_capital
        roi = (net_profit / self.initial_capital) * 100

        win_rate = (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0

        avg_win = total_profit / len(winning_trades) if winning_trades else 0
        avg_loss = total_loss / len(losing_trades) if losing_trades else 0

        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        self.performance_metrics = {
            "profile": self.profile_name,
            "total_trades": len(self.trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "total_loss": round(total_loss, 2),
            "net_profit": round(net_profit, 2),
            "roi_percentage": round(roi, 2),
            "initial_capital": self.initial_capital,
            "final_capital": round(self.current_capital, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "largest_win": max((t["profit_loss"] for t in winning_trades), default=0),
            "largest_loss": min((t["profit_loss"] for t in losing_trades), default=0),
        }

        logger.info(f"\n{'='*70}")
        logger.info(f"BACKTEST RESULTS - {self.profile_name.upper()}")
        logger.info(f"{'='*70}")
        logger.info(f"Total Trades: {self.performance_metrics['total_trades']}")
        logger.info(f"Win Rate: {self.performance_metrics['win_rate']}%")
        logger.info(f"Net Profit: ${self.performance_metrics['net_profit']:.2f}")
        logger.info(f"ROI: {self.performance_metrics['roi_percentage']}%")
        logger.info(f"Final Capital: ${self.performance_metrics['final_capital']:,.2f}")
        logger.info(f"Profit Factor: {self.performance_metrics['profit_factor']:.2f}")
        logger.info(f"{'='*70}\n")

    def export_results(self, output_dir: str = "backtest-results"):
        """Export backtest results to JSON and readable report"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export trades
        trades_file = f"{output_dir}/{self.profile_name}_trades_{timestamp}.json"
        with open(trades_file, "w") as f:
            json.dump(self.trades, f, indent=2, default=str)

        # Export metrics
        metrics_file = f"{output_dir}/{self.profile_name}_metrics_{timestamp}.json"
        with open(metrics_file, "w") as f:
            json.dump(self.performance_metrics, f, indent=2)

        logger.info(f"Results exported to {output_dir}/")

        return {"trades_file": trades_file, "metrics_file": metrics_file}


def run_all_profiles_backtest(days: int = 1):
    """Run backtest for all three profiles"""
    profiles = ["beginner", "novice", "advanced"]
    all_results = {}

    print("\n" + "=" * 70)
    print("COMPREHENSIVE BACKTEST - ALL RISK PROFILES")
    print(f"Duration: {days} day(s)")
    print("=" * 70 + "\n")

    for profile in profiles:
        engine = BacktestingEngine(profile)
        results = engine.run_backtest(days)
        engine.export_results()
        all_results[profile] = results

    # Comparative summary
    print("\n" + "=" * 70)
    print("COMPARATIVE PERFORMANCE SUMMARY")
    print("=" * 70)
    print(
        f"{'Profile':<12} {'Trades':<8} {'Win Rate':<10} {'ROI':<10} {'Final Capital':<15}"
    )
    print("-" * 70)

    for profile, results in all_results.items():
        if "total_trades" in results and results["total_trades"] > 0:
            print(
                f"{profile.capitalize():<12} "
                f"{results['total_trades']:<8} "
                f"{results['win_rate']}%{'':<7} "
                f"{results['roi_percentage']}%{'':<7} "
                f"${results['final_capital']:,.2f}"
            )

    print("=" * 70 + "\n")

    return all_results


if __name__ == "__main__":
    # Run 24-hour backtest for all profiles
    results = run_all_profiles_backtest(days=1)
