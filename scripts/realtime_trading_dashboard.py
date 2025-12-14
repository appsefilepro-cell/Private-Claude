#!/usr/bin/env python3
"""
Real-Time Trading Dashboard
Web-based dashboard to monitor all 21 trading accounts in real-time
Access at: http://localhost:8080
"""

import json
import os
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.generate_dashboard_html().encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(self.get_latest_stats().encode())
        else:
            self.send_response(404)
            self.end_headers()

    def generate_dashboard_html(self) -> str:
        """Generate real-time dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Agent X2.0 - 24/7 Trading Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .stats-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
        }

        .accounts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }

        .account-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }

        .account-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.4);
        }

        .account-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .account-name {
            font-size: 1.2em;
            font-weight: bold;
        }

        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .status-running {
            background: #10b981;
        }

        .status-error {
            background: #ef4444;
        }

        .account-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .detail-item {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
        }

        .detail-label {
            font-size: 0.8em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .detail-value {
            font-size: 1.1em;
            font-weight: bold;
        }

        .positive {
            color: #10b981;
        }

        .negative {
            color: #ef4444;
        }

        .refresh-info {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }

        .profile-beginner {
            border-left: 4px solid #3b82f6;
        }

        .profile-novice {
            border-left: 4px solid #f59e0b;
        }

        .profile-advanced {
            border-left: 4px solid #ef4444;
        }

        .last-update {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Agent X2.0 Trading Dashboard</h1>
        <div class="subtitle">24/7 Live Trading Monitoring - All Accounts</div>
        <div class="subtitle" id="last-update">Loading...</div>
    </div>

    <div class="stats-summary" id="summary">
        <div class="stat-card">
            <h3>Total Portfolio Value</h3>
            <div class="value" id="total-value">$0.00</div>
        </div>
        <div class="stat-card">
            <h3>Total Trades Executed</h3>
            <div class="value" id="total-trades">0</div>
        </div>
        <div class="stat-card">
            <h3>Active Accounts</h3>
            <div class="value" id="active-accounts">0/21</div>
        </div>
        <div class="stat-card">
            <h3>Win Rate</h3>
            <div class="value" id="win-rate">0%</div>
        </div>
    </div>

    <div class="accounts-grid" id="accounts">
        <!-- Account cards will be populated here -->
    </div>

    <div class="refresh-info">
        ⟳ Dashboard auto-refreshes every 10 seconds
    </div>

    <script>
        function fetchStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching stats:', error);
                });
        }

        function updateDashboard(data) {
            // Update last update time
            document.getElementById('last-update').textContent =
                'Last Update: ' + new Date(data.timestamp).toLocaleString();

            // Calculate summary stats
            let totalValue = 0;
            let totalTrades = 0;
            let totalWins = 0;
            let activeAccounts = 0;

            Object.values(data.accounts).forEach(account => {
                totalValue += account.current_capital;
                totalTrades += account.total_trades;
                totalWins += account.winning_trades;
                if (account.status === 'RUNNING') activeAccounts++;
            });

            const winRate = totalTrades > 0 ? (totalWins / totalTrades * 100) : 0;

            // Update summary
            document.getElementById('total-value').textContent =
                '$' + totalValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('total-trades').textContent = totalTrades;
            document.getElementById('active-accounts').textContent = activeAccounts + '/21';
            document.getElementById('win-rate').textContent = winRate.toFixed(1) + '%';

            // Update account cards
            const accountsContainer = document.getElementById('accounts');
            accountsContainer.innerHTML = '';

            Object.entries(data.accounts).forEach(([id, account]) => {
                const profitLoss = account.current_capital - account.initial_capital;
                const profitLossPercent = (profitLoss / account.initial_capital * 100);
                const winRate = account.total_trades > 0
                    ? (account.winning_trades / account.total_trades * 100)
                    : 0;

                const card = document.createElement('div');
                card.className = 'account-card profile-' + account.profile;
                card.innerHTML = `
                    <div class="account-header">
                        <div class="account-name">${account.name}</div>
                        <div class="status-badge status-${account.status.toLowerCase()}">
                            ${account.status}
                        </div>
                    </div>
                    <div class="account-details">
                        <div class="detail-item">
                            <div class="detail-label">Current Capital</div>
                            <div class="detail-value">$${account.current_capital.toLocaleString()}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">P/L</div>
                            <div class="detail-value ${profitLoss >= 0 ? 'positive' : 'negative'}">
                                ${profitLoss >= 0 ? '+' : ''}$${profitLoss.toFixed(2)}
                                (${profitLoss >= 0 ? '+' : ''}${profitLossPercent.toFixed(2)}%)
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Total Trades</div>
                            <div class="detail-value">${account.total_trades}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Win Rate</div>
                            <div class="detail-value ${winRate >= 50 ? 'positive' : 'negative'}">
                                ${winRate.toFixed(1)}%
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Profile</div>
                            <div class="detail-value">${account.profile.toUpperCase()}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Environment</div>
                            <div class="detail-value">${account.environment.toUpperCase()}</div>
                        </div>
                    </div>
                `;
                accountsContainer.appendChild(card);
            });
        }

        // Initial fetch
        fetchStats();

        // Auto-refresh every 10 seconds
        setInterval(fetchStats, 10000);
    </script>
</body>
</html>
        """

    def get_latest_stats(self) -> str:
        """Get latest trading statistics"""
        try:
            # Find most recent stats file
            logs_dir = Path('logs')
            stats_files = sorted(logs_dir.glob('trading_stats_*.json'), reverse=True)

            if stats_files:
                with open(stats_files[0], 'r') as f:
                    return f.read()
            else:
                # Return empty template
                return json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'accounts': {}
                })
        except Exception as e:
            return json.dumps({'error': str(e)})


def start_dashboard_server(port=8080):
    """Start the dashboard web server"""
    print(f"""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║            REAL-TIME TRADING DASHBOARD SERVER                     ║
    ╚═══════════════════════════════════════════════════════════════════╝

    🌐 Dashboard URL: http://localhost:{port}
    📊 Real-time updates every 10 seconds
    💻 Open in your browser to view live trading data

    Press Ctrl+C to stop the server
    ═══════════════════════════════════════════════════════════════════
    """)

    server = HTTPServer(('0.0.0.0', port), DashboardHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down dashboard server...")
        server.shutdown()


if __name__ == "__main__":
    start_dashboard_server()
