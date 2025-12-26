"""
Trading Bot Performance Tracker
Comprehensive performance tracking, metrics calculation, and reporting
Tracks trades, calculates win/loss ratios, ROI, risk metrics, and generates reports
"""

import os
import json
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PerformanceTracker')


class PerformanceTracker:
    """
    Comprehensive performance tracking for trading bot
    Tracks all trades, calculates metrics, and generates reports
    """

    def __init__(self, mode: str = "paper", profile: str = "beginner"):
        """
        Initialize performance tracker

        Args:
            mode: Trading mode (paper/demo/live)
            profile: Risk profile (beginner/novice/advanced)
        """
        self.mode = mode
        self.profile = profile
        self.trades: List[Dict[str, Any]] = []
        self.session_start = datetime.now()

        # Performance metrics
        self.initial_capital = 10000.0
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.metrics_cache = {}
        self.last_metrics_update = None

        # Create output directories
        self.output_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'performance'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Performance Tracker initialized - Mode: {mode}, Profile: {profile}")

    def record_trade(self, trade: Dict[str, Any]):
        """Record a new trade"""
        try:
            # Add timestamp if not present
            if 'entry_time' not in trade:
                trade['entry_time'] = datetime.now()

            self.trades.append(trade)
            logger.debug(f"Trade recorded: {trade.get('type')} {trade.get('pair')} @ ${trade.get('entry_price', 0):.2f}")

            # Invalidate metrics cache
            self.last_metrics_update = None

        except Exception as e:
            logger.error(f"Error recording trade: {e}")

    def update_trade(self, trade: Dict[str, Any]):
        """Update an existing trade (e.g., when closed)"""
        try:
            # Find and update the trade
            for i, t in enumerate(self.trades):
                if t.get('id') == trade.get('id'):
                    self.trades[i] = trade

                    # Update capital tracking
                    if trade.get('status') == 'CLOSED':
                        profit_loss = trade.get('profit_loss', 0)
                        self.current_capital += profit_loss

                        # Update peak capital for drawdown calculation
                        if self.current_capital > self.peak_capital:
                            self.peak_capital = self.current_capital

                    # Invalidate metrics cache
                    self.last_metrics_update = None

                    logger.debug(f"Trade updated: #{trade.get('id')} - {trade.get('status')}")
                    return

            logger.warning(f"Trade not found for update: #{trade.get('id')}")

        except Exception as e:
            logger.error(f"Error updating trade: {e}")

    def get_closed_trades(self) -> List[Dict[str, Any]]:
        """Get all closed trades"""
        return [t for t in self.trades if t.get('status') == 'CLOSED']

    def get_open_trades(self) -> List[Dict[str, Any]]:
        """Get all open trades"""
        return [t for t in self.trades if t.get('status') == 'OPEN']

    def get_winning_trades(self) -> List[Dict[str, Any]]:
        """Get all winning trades"""
        return [t for t in self.get_closed_trades() if t.get('profit_loss', 0) > 0]

    def get_losing_trades(self) -> List[Dict[str, Any]]:
        """Get all losing trades"""
        return [t for t in self.get_closed_trades() if t.get('profit_loss', 0) < 0]

    def calculate_win_loss_ratio(self) -> Dict[str, Any]:
        """Calculate win/loss ratio and related metrics"""
        closed_trades = self.get_closed_trades()
        if not closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "win_loss_ratio": 0.0
            }

        winning_trades = self.get_winning_trades()
        losing_trades = self.get_losing_trades()

        total = len(closed_trades)
        wins = len(winning_trades)
        losses = len(losing_trades)

        win_rate = (wins / total * 100) if total > 0 else 0
        loss_rate = (losses / total * 100) if total > 0 else 0
        win_loss_ratio = (wins / losses) if losses > 0 else float('inf') if wins > 0 else 0

        return {
            "total_trades": total,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "win_loss_ratio": round(win_loss_ratio, 2) if win_loss_ratio != float('inf') else "∞"
        }

    def calculate_roi(self) -> Dict[str, Any]:
        """Calculate return on investment metrics"""
        net_profit = self.current_capital - self.initial_capital
        roi_percentage = (net_profit / self.initial_capital * 100) if self.initial_capital > 0 else 0

        # Calculate time-based ROI
        session_duration = datetime.now() - self.session_start
        days_running = max(session_duration.total_seconds() / 86400, 1)  # Minimum 1 day

        daily_roi = roi_percentage / days_running
        monthly_roi = daily_roi * 30
        yearly_roi = daily_roi * 365

        return {
            "initial_capital": self.initial_capital,
            "current_capital": round(self.current_capital, 2),
            "net_profit": round(net_profit, 2),
            "roi_percentage": round(roi_percentage, 2),
            "daily_roi": round(daily_roi, 2),
            "monthly_roi": round(monthly_roi, 2),
            "yearly_roi": round(yearly_roi, 2),
            "days_running": round(days_running, 2)
        }

    def calculate_profit_metrics(self) -> Dict[str, Any]:
        """Calculate profit and loss metrics"""
        winning_trades = self.get_winning_trades()
        losing_trades = self.get_losing_trades()

        total_profit = sum(t.get('profit_loss', 0) for t in winning_trades)
        total_loss = abs(sum(t.get('profit_loss', 0) for t in losing_trades))

        avg_win = total_profit / len(winning_trades) if winning_trades else 0
        avg_loss = total_loss / len(losing_trades) if losing_trades else 0

        largest_win = max((t.get('profit_loss', 0) for t in winning_trades), default=0)
        largest_loss = min((t.get('profit_loss', 0) for t in losing_trades), default=0)

        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf') if total_profit > 0 else 0

        # Average profit per trade
        closed_trades = self.get_closed_trades()
        avg_profit_per_trade = sum(t.get('profit_loss', 0) for t in closed_trades) / len(closed_trades) if closed_trades else 0

        return {
            "total_profit": round(total_profit, 2),
            "total_loss": round(total_loss, 2),
            "net_profit": round(total_profit - total_loss, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "largest_win": round(largest_win, 2),
            "largest_loss": round(largest_loss, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
            "avg_profit_per_trade": round(avg_profit_per_trade, 2)
        }

    def calculate_max_drawdown(self) -> Dict[str, Any]:
        """Calculate maximum drawdown"""
        if not self.trades:
            return {
                "max_drawdown": 0.0,
                "max_drawdown_pct": 0.0,
                "current_drawdown": 0.0,
                "current_drawdown_pct": 0.0
            }

        # Calculate drawdown
        current_drawdown = self.peak_capital - self.current_capital
        current_drawdown_pct = (current_drawdown / self.peak_capital * 100) if self.peak_capital > 0 else 0

        # For max drawdown, we'd need to track capital over time
        # For now, use current drawdown as approximation
        max_drawdown = current_drawdown
        max_drawdown_pct = current_drawdown_pct

        return {
            "peak_capital": round(self.peak_capital, 2),
            "current_capital": round(self.current_capital, 2),
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "current_drawdown": round(current_drawdown, 2),
            "current_drawdown_pct": round(current_drawdown_pct, 2)
        }

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        closed_trades = self.get_closed_trades()
        if len(closed_trades) < 2:
            return 0.0

        # Calculate returns for each trade
        returns = [t.get('profit_loss_pct', 0) / 100 for t in closed_trades]

        if not returns:
            return 0.0

        # Calculate average return and standard deviation
        avg_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0

        if std_dev == 0:
            return 0.0

        # Convert annual risk-free rate to per-trade rate
        # Assuming average holding period
        sharpe_ratio = (avg_return - risk_free_rate / 252) / std_dev  # 252 trading days

        return round(sharpe_ratio, 4)

    def calculate_trade_duration_metrics(self) -> Dict[str, Any]:
        """Calculate metrics related to trade duration"""
        closed_trades = self.get_closed_trades()
        if not closed_trades:
            return {
                "avg_trade_duration": "N/A",
                "shortest_trade": "N/A",
                "longest_trade": "N/A"
            }

        durations = []
        for trade in closed_trades:
            if 'entry_time' in trade and 'exit_time' in trade:
                entry = trade['entry_time']
                exit = trade['exit_time']

                # Convert to datetime if string
                if isinstance(entry, str):
                    entry = datetime.fromisoformat(entry.replace('Z', '+00:00'))
                if isinstance(exit, str):
                    exit = datetime.fromisoformat(exit.replace('Z', '+00:00'))

                duration = exit - entry
                durations.append(duration)

        if not durations:
            return {
                "avg_trade_duration": "N/A",
                "shortest_trade": "N/A",
                "longest_trade": "N/A"
            }

        avg_duration = sum(durations, timedelta()) / len(durations)
        shortest = min(durations)
        longest = max(durations)

        def format_duration(td):
            seconds = td.total_seconds()
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"

        return {
            "avg_trade_duration": format_duration(avg_duration),
            "shortest_trade": format_duration(shortest),
            "longest_trade": format_duration(longest)
        }

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics (cached for performance)"""
        # Return cached metrics if recent (within 1 minute)
        if self.last_metrics_update:
            time_since_update = datetime.now() - self.last_metrics_update
            if time_since_update.total_seconds() < 60:
                return self.metrics_cache

        # Calculate fresh metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "profile": self.profile,
            "session_start": self.session_start.isoformat(),
            "total_trades": len(self.trades),
            "open_trades": len(self.get_open_trades()),
            "closed_trades": len(self.get_closed_trades()),
        }

        # Add all metric categories
        metrics.update(self.calculate_win_loss_ratio())
        metrics.update(self.calculate_roi())
        metrics.update(self.calculate_profit_metrics())
        metrics.update(self.calculate_max_drawdown())
        metrics["sharpe_ratio"] = self.calculate_sharpe_ratio()
        metrics.update(self.calculate_trade_duration_metrics())

        # Cache metrics
        self.metrics_cache = metrics
        self.last_metrics_update = datetime.now()

        return metrics

    def get_hourly_metrics(self) -> Dict[str, Any]:
        """Get metrics for the last hour"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # Filter trades from last hour
        recent_trades = [
            t for t in self.get_closed_trades()
            if 'exit_time' in t and (
                (isinstance(t['exit_time'], datetime) and t['exit_time'] > one_hour_ago) or
                (isinstance(t['exit_time'], str) and datetime.fromisoformat(t['exit_time'].replace('Z', '+00:00')) > one_hour_ago)
            )
        ]

        hourly_profit_loss = sum(t.get('profit_loss', 0) for t in recent_trades)

        return {
            "trades_last_hour": len(recent_trades),
            "hourly_profit_loss": round(hourly_profit_loss, 2),
            **self.get_current_metrics()
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return self.get_current_metrics()

    def get_trade_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get trade history

        Args:
            limit: Maximum number of trades to return (None for all)
        """
        trades = sorted(self.trades, key=lambda t: t.get('entry_time', datetime.min), reverse=True)
        if limit:
            trades = trades[:limit]
        return trades

    def export_json(self, filename: Optional[str] = None) -> str:
        """
        Export performance metrics and trade history to JSON

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_{self.mode}_{self.profile}_{timestamp}.json"

        filepath = self.output_dir / filename

        data = {
            "metadata": {
                "mode": self.mode,
                "profile": self.profile,
                "session_start": self.session_start.isoformat(),
                "export_time": datetime.now().isoformat()
            },
            "metrics": self.get_current_metrics(),
            "trades": self.trades
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Performance data exported to {filepath}")
        return str(filepath)

    def export_csv(self, filename: Optional[str] = None) -> str:
        """
        Export trade history to CSV

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trades_{self.mode}_{self.profile}_{timestamp}.csv"

        filepath = self.output_dir / filename

        if not self.trades:
            logger.warning("No trades to export")
            return ""

        # Get all possible fields from trades
        fieldnames = set()
        for trade in self.trades:
            fieldnames.update(trade.keys())

        fieldnames = sorted(fieldnames)

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for trade in self.trades:
                # Convert datetime objects to strings
                row = {}
                for key, value in trade.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
                    else:
                        row[key] = value
                writer.writerow(row)

        logger.info(f"Trade history exported to {filepath}")
        return str(filepath)

    def generate_performance_report(self, filename: Optional[str] = None) -> str:
        """
        Generate comprehensive performance report

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{self.mode}_{self.profile}_{timestamp}.txt"

        filepath = self.output_dir / filename

        metrics = self.get_current_metrics()

        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write("TRADING BOT PERFORMANCE REPORT\n")
            f.write("="*80 + "\n\n")

            # Session Info
            f.write("SESSION INFORMATION\n")
            f.write("-"*80 + "\n")
            f.write(f"Mode:           {self.mode.upper()}\n")
            f.write(f"Profile:        {self.profile.capitalize()}\n")
            f.write(f"Session Start:  {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Report Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Runtime:        {metrics.get('days_running', 0):.2f} days\n")
            f.write("\n")

            # Capital & ROI
            f.write("CAPITAL & RETURNS\n")
            f.write("-"*80 + "\n")
            f.write(f"Initial Capital:    ${metrics.get('initial_capital', 0):,.2f}\n")
            f.write(f"Current Capital:    ${metrics.get('current_capital', 0):,.2f}\n")
            f.write(f"Peak Capital:       ${metrics.get('peak_capital', 0):,.2f}\n")
            f.write(f"Net Profit:         ${metrics.get('net_profit', 0):,.2f}\n")
            f.write(f"ROI:                {metrics.get('roi_percentage', 0):.2f}%\n")
            f.write(f"Daily ROI:          {metrics.get('daily_roi', 0):.2f}%\n")
            f.write(f"Monthly ROI (est):  {metrics.get('monthly_roi', 0):.2f}%\n")
            f.write(f"Yearly ROI (est):   {metrics.get('yearly_roi', 0):.2f}%\n")
            f.write("\n")

            # Trade Statistics
            f.write("TRADE STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Trades:       {metrics.get('total_trades', 0)}\n")
            f.write(f"Open Trades:        {metrics.get('open_trades', 0)}\n")
            f.write(f"Closed Trades:      {metrics.get('closed_trades', 0)}\n")
            f.write(f"Winning Trades:     {metrics.get('winning_trades', 0)}\n")
            f.write(f"Losing Trades:      {metrics.get('losing_trades', 0)}\n")
            f.write(f"Win Rate:           {metrics.get('win_rate', 0):.2f}%\n")
            f.write(f"Win/Loss Ratio:     {metrics.get('win_loss_ratio', 0)}\n")
            f.write("\n")

            # Profit Metrics
            f.write("PROFIT METRICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Profit:       ${metrics.get('total_profit', 0):,.2f}\n")
            f.write(f"Total Loss:         ${metrics.get('total_loss', 0):,.2f}\n")
            f.write(f"Average Win:        ${metrics.get('avg_win', 0):,.2f}\n")
            f.write(f"Average Loss:       ${metrics.get('avg_loss', 0):,.2f}\n")
            f.write(f"Largest Win:        ${metrics.get('largest_win', 0):,.2f}\n")
            f.write(f"Largest Loss:       ${metrics.get('largest_loss', 0):,.2f}\n")
            f.write(f"Profit Factor:      {metrics.get('profit_factor', 0)}\n")
            f.write(f"Avg Profit/Trade:   ${metrics.get('avg_profit_per_trade', 0):,.2f}\n")
            f.write("\n")

            # Risk Metrics
            f.write("RISK METRICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Max Drawdown:       ${metrics.get('max_drawdown', 0):,.2f} ({metrics.get('max_drawdown_pct', 0):.2f}%)\n")
            f.write(f"Current Drawdown:   ${metrics.get('current_drawdown', 0):,.2f} ({metrics.get('current_drawdown_pct', 0):.2f}%)\n")
            f.write(f"Sharpe Ratio:       {metrics.get('sharpe_ratio', 0):.4f}\n")
            f.write("\n")

            # Trade Duration
            f.write("TRADE DURATION\n")
            f.write("-"*80 + "\n")
            f.write(f"Average Duration:   {metrics.get('avg_trade_duration', 'N/A')}\n")
            f.write(f"Shortest Trade:     {metrics.get('shortest_trade', 'N/A')}\n")
            f.write(f"Longest Trade:      {metrics.get('longest_trade', 'N/A')}\n")
            f.write("\n")

            # Recent Trades
            f.write("RECENT TRADES (Last 10)\n")
            f.write("-"*80 + "\n")
            recent_trades = self.get_trade_history(limit=10)
            if recent_trades:
                f.write(f"{'ID':<5} {'Pair':<10} {'Type':<6} {'Entry':<10} {'Exit':<10} {'P/L':<12} {'Status':<8}\n")
                f.write("-"*80 + "\n")
                for trade in recent_trades:
                    trade_id = trade.get('id', 'N/A')
                    pair = trade.get('pair', 'N/A')
                    trade_type = trade.get('type', 'N/A')
                    entry = f"${trade.get('entry_price', 0):.2f}"
                    exit = f"${trade.get('exit_price', 0):.2f}" if trade.get('exit_price') else "N/A"
                    pl = f"${trade.get('profit_loss', 0):,.2f}" if 'profit_loss' in trade else "N/A"
                    status = trade.get('status', 'N/A')

                    f.write(f"{trade_id:<5} {pair:<10} {trade_type:<6} {entry:<10} {exit:<10} {pl:<12} {status:<8}\n")
            else:
                f.write("No trades recorded\n")

            f.write("\n")
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")

        logger.info(f"Performance report generated: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    # Test the performance tracker
    tracker = PerformanceTracker(mode="paper", profile="beginner")

    # Simulate some trades
    test_trade_1 = {
        "id": 1,
        "pair": "BTC/USD",
        "type": "BUY",
        "entry_price": 50000,
        "quantity": 0.02,
        "position_value": 1000,
        "entry_time": datetime.now() - timedelta(hours=2),
        "status": "OPEN"
    }

    test_trade_2 = {
        "id": 2,
        "pair": "ETH/USD",
        "type": "BUY",
        "entry_price": 3000,
        "quantity": 0.33,
        "position_value": 1000,
        "entry_time": datetime.now() - timedelta(hours=1),
        "status": "OPEN"
    }

    tracker.record_trade(test_trade_1)
    tracker.record_trade(test_trade_2)

    # Close first trade with profit
    test_trade_1['exit_price'] = 51000
    test_trade_1['exit_time'] = datetime.now()
    test_trade_1['status'] = 'CLOSED'
    test_trade_1['profit_loss'] = (51000 - 50000) * 0.02
    test_trade_1['profit_loss_pct'] = ((51000 - 50000) / 50000) * 100
    test_trade_1['close_reason'] = 'TAKE_PROFIT'

    tracker.update_trade(test_trade_1)

    # Get metrics
    metrics = tracker.get_current_metrics()
    print(json.dumps(metrics, indent=2, default=str))

    # Generate reports
    tracker.export_json()
    tracker.export_csv()
    tracker.generate_performance_report()
