#!/usr/bin/env python3
"""
LIVE TRADING DASHBOARD
Real-time monitoring and visualization of all trading operations

Features:
- Streamlit dashboard with real-time data
- Show all active trades across all bots
- Display P&L charts and performance metrics
- Show strategy performance comparison
- Bot status monitoring
- Mobile-responsive design
- Auto-refresh data
- Historical performance analysis
- Risk management visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
import time
from typing import Dict, List, Optional
import sys

# Add parent directory to path
sys.path.append('/home/user/Private-Claude/pillar-a-trading')

# Page configuration
st.set_page_config(
    page_title="Trading Dashboard - Live",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stMetric > div {
        margin: 0;
    }
    @media (max-width: 768px) {
        .main {
            padding: 0rem 0.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


class TradingDashboard:
    """Live Trading Dashboard"""

    def __init__(self, data_dir: str = "/home/user/Private-Claude/pillar-a-trading/data"):
        """Initialize dashboard"""
        self.data_dir = Path(data_dir)

        # Database paths
        self.bot_manager_db = self.data_dir / "bot_manager.db"
        self.mt5_db = self.data_dir / "mt5_accounts.db"
        self.okx_db = self.data_dir / "okx_paper_trading.db"
        self.trades_db = self.data_dir / "trades.json"

    # ============================================================
    # DATA RETRIEVAL
    # ============================================================

    def get_bot_status(self) -> pd.DataFrame:
        """Get status of all trading bots"""
        if not self.bot_manager_db.exists():
            return pd.DataFrame()

        conn = sqlite3.connect(self.bot_manager_db)
        query = "SELECT * FROM bots ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def get_system_metrics(self, hours: int = 24) -> pd.DataFrame:
        """Get system metrics for the last N hours"""
        if not self.bot_manager_db.exists():
            return pd.DataFrame()

        conn = sqlite3.connect(self.bot_manager_db)
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        query = f"""
            SELECT * FROM system_metrics
            WHERE timestamp > '{cutoff}'
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    def get_all_trades(self, limit: int = 100) -> pd.DataFrame:
        """Get recent trades from all sources"""
        all_trades = []

        # MT5 trades
        if self.mt5_db.exists():
            conn = sqlite3.connect(self.mt5_db)
            query = f"SELECT * FROM demo_trades ORDER BY open_time DESC LIMIT {limit}"
            mt5_trades = pd.read_sql_query(query, conn)
            conn.close()

            if not mt5_trades.empty:
                mt5_trades['source'] = 'MT5'
                all_trades.append(mt5_trades)

        # OKX trades
        if self.okx_db.exists():
            conn = sqlite3.connect(self.okx_db)
            query = f"SELECT * FROM trades ORDER BY open_time DESC LIMIT {limit}"
            okx_trades = pd.read_sql_query(query, conn)
            conn.close()

            if not okx_trades.empty:
                okx_trades['source'] = 'OKX'
                all_trades.append(okx_trades)

        # Combine all trades
        if all_trades:
            df = pd.concat(all_trades, ignore_index=True)
            df['open_time'] = pd.to_datetime(df['open_time'])
            return df.sort_values('open_time', ascending=False)

        return pd.DataFrame()

    def get_portfolio_summary(self) -> Dict:
        """Get overall portfolio summary"""
        summary = {
            'total_balance': 0.0,
            'total_equity': 0.0,
            'total_profit': 0.0,
            'total_trades': 0,
            'active_positions': 0,
            'bots_running': 0
        }

        # Get from system metrics
        metrics = self.get_system_metrics(hours=1)
        if not metrics.empty:
            latest = metrics.iloc[-1]
            summary['total_balance'] = latest['total_balance']
            summary['total_profit'] = latest['total_profit']
            summary['total_trades'] = latest['total_trades']
            summary['bots_running'] = latest['active_bots']

        return summary

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        trades = self.get_all_trades()

        if trades.empty:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }

        # Calculate metrics
        closed_trades = trades[trades['status'] == 'closed']

        if closed_trades.empty:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0
            }

        wins = closed_trades[closed_trades['profit_loss'] > 0]
        losses = closed_trades[closed_trades['profit_loss'] < 0]

        win_rate = (len(wins) / len(closed_trades)) * 100 if len(closed_trades) > 0 else 0

        total_wins = wins['profit_loss'].sum() if not wins.empty else 0
        total_losses = abs(losses['profit_loss'].sum()) if not losses.empty else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        avg_win = wins['profit_loss'].mean() if not wins.empty else 0
        avg_loss = losses['profit_loss'].mean() if not losses.empty else 0

        # Simplified Sharpe ratio
        returns = closed_trades['profit_loss'] / closed_trades['total_value']
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown': 0.0,  # TODO: Calculate
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }

    # ============================================================
    # VISUALIZATIONS
    # ============================================================

    def create_profit_chart(self) -> go.Figure:
        """Create profit over time chart"""
        metrics = self.get_system_metrics(hours=168)  # 7 days

        if metrics.empty:
            # Empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        fig = go.Figure()

        # Profit line
        fig.add_trace(go.Scatter(
            x=metrics['timestamp'],
            y=metrics['total_profit'],
            mode='lines+markers',
            name='Profit',
            line=dict(color='#00D4AA', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 170, 0.1)'
        ))

        fig.update_layout(
            title='Profit Over Time',
            xaxis_title='Time',
            yaxis_title='Profit (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    def create_balance_chart(self) -> go.Figure:
        """Create balance evolution chart"""
        metrics = self.get_system_metrics(hours=168)

        if metrics.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Balance
        fig.add_trace(
            go.Scatter(
                x=metrics['timestamp'],
                y=metrics['total_balance'],
                mode='lines',
                name='Balance',
                line=dict(color='#1f77b4', width=2)
            ),
            secondary_y=False
        )

        # Trades count
        fig.add_trace(
            go.Scatter(
                x=metrics['timestamp'],
                y=metrics['total_trades'],
                mode='lines',
                name='Total Trades',
                line=dict(color='#ff7f0e', width=2)
            ),
            secondary_y=True
        )

        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Balance (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Trades Count", secondary_y=True)

        fig.update_layout(
            title='Balance & Trades Evolution',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    def create_bot_performance_chart(self) -> go.Figure:
        """Create bot performance comparison chart"""
        trades = self.get_all_trades()

        if trades.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No trades available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Group by source (bot)
        bot_perf = trades.groupby('source').agg({
            'profit_loss': 'sum',
            'symbol': 'count'
        }).reset_index()

        bot_perf.columns = ['Bot', 'Total P&L', 'Trade Count']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=bot_perf['Bot'],
            y=bot_perf['Total P&L'],
            marker_color=['#00D4AA' if x > 0 else '#FF4B4B' for x in bot_perf['Total P&L']],
            text=bot_perf['Total P&L'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
        ))

        fig.update_layout(
            title='Bot Performance Comparison',
            xaxis_title='Trading Bot',
            yaxis_title='Profit/Loss (USD)',
            template='plotly_white',
            height=400
        )

        return fig

    def create_trades_distribution(self) -> go.Figure:
        """Create trades distribution chart"""
        trades = self.get_all_trades()

        if trades.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No trades available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        closed = trades[trades['status'] == 'closed']

        if closed.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No closed trades",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        wins = closed[closed['profit_loss'] > 0]
        losses = closed[closed['profit_loss'] <= 0]

        fig = go.Figure(data=[
            go.Pie(
                labels=['Wins', 'Losses'],
                values=[len(wins), len(losses)],
                marker=dict(colors=['#00D4AA', '#FF4B4B']),
                hole=0.4,
                textinfo='label+percent+value',
                hovertemplate='%{label}<br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
            )
        ])

        fig.update_layout(
            title='Win/Loss Distribution',
            template='plotly_white',
            height=400
        )

        return fig

    # ============================================================
    # DASHBOARD LAYOUT
    # ============================================================

    def render(self):
        """Render the dashboard"""
        # Header
        st.title("📈 Live Trading Dashboard")
        st.markdown("Real-time monitoring of all trading operations")

        # Auto-refresh
        refresh_interval = st.sidebar.number_input(
            "Auto-refresh (seconds)",
            min_value=5,
            max_value=300,
            value=30
        )

        if st.sidebar.button("🔄 Refresh Now"):
            st.rerun()

        # Portfolio summary
        st.header("📊 Portfolio Overview")

        summary = self.get_portfolio_summary()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Balance",
                f"${summary['total_balance']:.2f}",
                delta=f"${summary['total_profit']:.2f}"
            )

        with col2:
            st.metric(
                "Total Trades",
                summary['total_trades']
            )

        with col3:
            st.metric(
                "Active Bots",
                summary['bots_running']
            )

        with col4:
            st.metric(
                "Open Positions",
                summary['active_positions']
            )

        # Performance Metrics
        st.header("📈 Performance Metrics")

        metrics = self.get_performance_metrics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")

        with col2:
            st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")

        with col3:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")

        with col4:
            avg_win = metrics['avg_win']
            st.metric("Avg Win", f"${avg_win:.2f}")

        # Charts
        st.header("📉 Charts")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Profit Over Time",
            "Balance & Trades",
            "Bot Performance",
            "Win/Loss Distribution"
        ])

        with tab1:
            st.plotly_chart(
                self.create_profit_chart(),
                use_container_width=True
            )

        with tab2:
            st.plotly_chart(
                self.create_balance_chart(),
                use_container_width=True
            )

        with tab3:
            st.plotly_chart(
                self.create_bot_performance_chart(),
                use_container_width=True
            )

        with tab4:
            st.plotly_chart(
                self.create_trades_distribution(),
                use_container_width=True
            )

        # Bot Status
        st.header("🤖 Bot Status")

        bot_status = self.get_bot_status()

        if not bot_status.empty:
            st.dataframe(
                bot_status[['name', 'type', 'status', 'last_started']],
                use_container_width=True
            )
        else:
            st.info("No bots registered yet")

        # Recent Trades
        st.header("💹 Recent Trades")

        trades = self.get_all_trades(limit=50)

        if not trades.empty:
            # Format for display
            display_trades = trades[[
                'source', 'symbol', 'side', 'quantity',
                'price', 'profit_loss', 'status', 'open_time'
            ]].copy()

            display_trades['open_time'] = pd.to_datetime(display_trades['open_time']).dt.strftime('%Y-%m-%d %H:%M')

            # Apply color coding
            st.dataframe(
                display_trades,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No trades recorded yet")

        # System Information
        with st.sidebar:
            st.header("ℹ️ System Info")

            st.metric("Dashboard Status", "🟢 Live")

            st.markdown(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

            # Links
            st.markdown("---")
            st.markdown("### 📚 Resources")
            st.markdown("- [MT5 Setup](/mt5_demo_setup)")
            st.markdown("- [OKX Paper Trading](/okx_paper)")
            st.markdown("- [Bot Manager](/bot_manager)")

        # Auto-refresh
        time.sleep(refresh_interval)
        st.rerun()


def main():
    """Main entry point"""
    dashboard = TradingDashboard()
    dashboard.render()


if __name__ == "__main__":
    main()
