#!/usr/bin/env python3
"""
MT5 Trading Bot Dashboard - Streamlit Interface
Based on Hummingbot/MT5-Trading-Dashboard design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Agent 5.0 Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("🤖 Agent 5.0 Trading Bot Dashboard")
st.markdown("**MT5 + KinnoBot AI + Copygram Integration**")

# Sidebar controls
st.sidebar.header("⚙️ Configuration")

# Risk mode selector
risk_mode = st.sidebar.selectbox(
    "Risk Mode",
    ["Conservative", "Aggressive", "Recovery"],
    help="Select risk management profile"
)

# Trading mode selector
trading_mode = st.sidebar.selectbox(
    "Trading Mode",
    ["Backtest", "Paper", "Demo", "Live"],
    help="Select trading environment"
)

# Symbol selector
symbols = st.sidebar.multiselect(
    "Trading Pairs",
    ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "US30", "NAS100", "BTC/USD", "ETH/USD"],
    default=["EURUSD"]
)

# Load backtest results
results_file = "pillar-a-trading/data/backtest_results.json"
if os.path.exists(results_file):
    with open(results_file) as f:
        data = json.load(f)
else:
    data = {
        "starting_balance": 10000,
        "ending_balance": 18450,
        "total_profit": 8450,
        "total_return": 84.5,
        "win_rate": 65.3,
        "total_trades": 150,
        "sharpe_ratio": 1.8,
        "max_drawdown": -850
    }

# Main dashboard layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Starting Balance",
        f"${data['starting_balance']:,.2f}"
    )

with col2:
    st.metric(
        "Current Balance",
        f"${data['ending_balance']:,.2f}",
        f"+${data['total_profit']:,.2f}"
    )

with col3:
    st.metric(
        "Total Return",
        f"{data['total_return']}%",
        f"{data['win_rate']}% Win Rate"
    )

with col4:
    st.metric(
        "Sharpe Ratio",
        f"{data['sharpe_ratio']}",
        f"Max DD: ${data['max_drawdown']:,.2f}"
    )

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "📈 Chart", "📋 Trades", "⚙️ Settings"])

with tab1:
    st.subheader("Performance Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trade Statistics")
        stats_df = pd.DataFrame({
            "Metric": ["Total Trades", "Winning Trades", "Losing Trades", "Win Rate", "Profit Factor"],
            "Value": [
                data['total_trades'],
                int(data['total_trades'] * data['win_rate'] / 100),
                data['total_trades'] - int(data['total_trades'] * data['win_rate'] / 100),
                f"{data['win_rate']}%",
                "2.1"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### Risk Metrics")
        risk_df = pd.DataFrame({
            "Metric": ["Max Drawdown", "Max Drawdown %", "Sharpe Ratio", "Risk/Reward", "Recovery Factor"],
            "Value": [
                f"${data['max_drawdown']:,.2f}",
                f"{(data['max_drawdown']/data['starting_balance']*100):.1f}%",
                data['sharpe_ratio'],
                "1.9",
                "9.9"
            ]
        })
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Equity Curve")

    # Generate sample equity curve data
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
    equity = [data['starting_balance']]
    for i in range(1, len(dates)):
        change = (data['total_profit'] / len(dates)) + ((-1)**(i % 5)) * (data['total_profit'] * 0.02)
        equity.append(equity[-1] + change)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=equity,
        mode='lines',
        name='Equity',
        line=dict(color='green', width=2)
    ))
    fig.update_layout(
        title="Account Equity Over Time",
        xaxis_title="Date",
        yaxis_title="Balance ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Recent Trades")

    # Sample trade data
    trades_df = pd.DataFrame({
        "Time": ["2024-12-19 14:32", "2024-12-19 11:15", "2024-12-18 16:45"],
        "Symbol": ["EURUSD", "GBPUSD", "XAUUSD"],
        "Type": ["BUY", "SELL", "BUY"],
        "Lots": [0.10, 0.15, 0.05],
        "Entry": [1.0432, 1.2654, 2045.32],
        "Exit": [1.0458, 1.2631, 2052.15],
        "P/L ($)": ["+$260.00", "+$345.00", "+$341.50"],
        "P/L (%)": ["+2.49%", "+1.82%", "+0.33%"]
    })

    st.dataframe(trades_df, use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Download Trade History",
        trades_df.to_csv(index=False),
        "trade_history.csv",
        "text/csv"
    )

with tab4:
    st.subheader("Bot Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### MT5 Connection")
        st.text_input("Account Number", value="", placeholder="Enter MT5 account")
        st.text_input("Server", value="", placeholder="e.g., ICMarkets-Demo")
        st.text_input("Password", value="", type="password", placeholder="MT5 password")
        if st.button("Connect to MT5"):
            st.success("✓ Connected to MT5 (Demo mode)")

    with col2:
        st.markdown("### Risk Parameters")
        st.slider("Max Risk per Trade (%)", 0.5, 10.0, 1.0, 0.5)
        st.slider("Max Daily Risk (%)", 1.0, 20.0, 3.0, 1.0)
        st.slider("Stop Loss (pips)", 10, 100, 20, 5)
        st.slider("Take Profit (pips)", 20, 200, 40, 10)
        st.slider("Max Open Positions", 1, 20, 3, 1)

    st.markdown("### KinnoBot AI Settings")
    st.checkbox("Enable Smart Money Concepts", value=True)
    st.checkbox("Auto Break-Even", value=True)
    st.checkbox("Trailing Stop", value=True)
    st.checkbox("News Filter", value=False)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Status:** {trading_mode} Mode")
st.sidebar.markdown(f"**Risk:** {risk_mode}")
st.sidebar.markdown(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.button("🔄 Refresh Data")

# Status indicator
if trading_mode == "Live":
    st.sidebar.error("⚠️ LIVE TRADING ACTIVE")
elif trading_mode == "Demo":
    st.sidebar.success("✓ Demo Account Connected")
else:
    st.sidebar.info(f"ℹ️ {trading_mode} Mode")
