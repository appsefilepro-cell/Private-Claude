// AgentX5 React Dashboard
// Complete trading + legal + financial monitoring system

import React, { useState, useEffect } from 'react';
import './App.css';

// ============================================================================
// TYPES
// ============================================================================

interface TradingMetrics {
  winRate: number;
  totalTrades: number;
  activeTrades: number;
  todayProfit: number;
  accountBalance: number;
}

interface Trade {
  id: string;
  pair: string;
  pattern: string;
  entryPrice: number;
  status: 'active' | 'won' | 'lost';
  profit?: number;
  timestamp: string;
}

interface SystemStatus {
  trading: 'operational' | 'warning' | 'offline';
  legal: 'operational' | 'warning' | 'offline';
  crm: 'operational' | 'warning' | 'offline';
  api: 'operational' | 'warning' | 'offline';
}

// ============================================================================
// MAIN APP
// ============================================================================

function App() {
  const [metrics, setMetrics] = useState<TradingMetrics>({
    winRate: 92.6,
    totalTrades: 500,
    activeTrades: 5,
    todayProfit: 1250.50,
    accountBalance: 12500.00
  });

  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    trading: 'operational',
    legal: 'operational',
    crm: 'operational',
    api: 'operational'
  });

  // Fetch data from API
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // In production, fetch from API
      // const response = await fetch('http://localhost:8000/api/v1/trading/status');
      // const data = await response.json();
      // setMetrics(data);

      // Simulate live data for demo
      setMetrics(prev => ({
        ...prev,
        todayProfit: prev.todayProfit + (Math.random() * 10 - 5)
      }));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  return (
    <div className="App">
      <Header />

      <main className="dashboard-container">
        {/* System Status Banner */}
        <SystemStatusBanner status={systemStatus} />

        {/* Trading Metrics Cards */}
        <MetricsGrid metrics={metrics} />

        {/* Active Trades */}
        <section className="section">
          <h2>Active Trades</h2>
          <TradesTable trades={recentTrades} />
        </section>

        {/* Trading Signals */}
        <section className="section">
          <h2>Live Trading Signals</h2>
          <SignalsPanel />
        </section>

        {/* Performance Chart */}
        <section className="section">
          <h2>Performance Chart</h2>
          <PerformanceChart />
        </section>
      </main>
    </div>
  );
}

// ============================================================================
// COMPONENTS
// ============================================================================

const Header: React.FC = () => {
  return (
    <header className="app-header">
      <div className="header-content">
        <h1>🚀 AgentX5 Dashboard</h1>
        <p>Trading + Legal + Financial Automation</p>
      </div>
      <div className="header-actions">
        <span className="status-badge operational">● LIVE</span>
        <button className="btn-primary">Deploy to Railway</button>
      </div>
    </header>
  );
};

interface SystemStatusBannerProps {
  status: SystemStatus;
}

const SystemStatusBanner: React.FC<SystemStatusBannerProps> = ({ status }) => {
  const allOperational = Object.values(status).every(s => s === 'operational');

  return (
    <div className={`status-banner ${allOperational ? 'operational' : 'warning'}`}>
      <h3>System Status</h3>
      <div className="status-grid">
        <StatusItem label="Trading" status={status.trading} />
        <StatusItem label="Legal" status={status.legal} />
        <StatusItem label="CRM" status={status.crm} />
        <StatusItem label="API" status={status.api} />
      </div>
    </div>
  );
};

interface StatusItemProps {
  label: string;
  status: 'operational' | 'warning' | 'offline';
}

const StatusItem: React.FC<StatusItemProps> = ({ label, status }) => {
  const icon = status === 'operational' ? '✅' : status === 'warning' ? '⚠️' : '❌';
  return (
    <div className="status-item">
      <span className="status-icon">{icon}</span>
      <span className="status-label">{label}</span>
    </div>
  );
};

interface MetricsGridProps {
  metrics: TradingMetrics;
}

const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  return (
    <div className="metrics-grid">
      <MetricCard
        title="Win Rate"
        value={`${metrics.winRate}%`}
        subtitle="500 trades"
        trend="up"
        color="green"
      />
      <MetricCard
        title="Today's Profit"
        value={`$${metrics.todayProfit.toFixed(2)}`}
        subtitle={`${metrics.activeTrades} active trades`}
        trend="up"
        color="blue"
      />
      <MetricCard
        title="Account Balance"
        value={`$${metrics.accountBalance.toLocaleString()}`}
        subtitle="All accounts"
        trend="up"
        color="purple"
      />
      <MetricCard
        title="Total Trades"
        value={metrics.totalTrades.toString()}
        subtitle="Last 30 days"
        trend="up"
        color="orange"
      />
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  trend: 'up' | 'down' | 'neutral';
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, trend, color }) => {
  return (
    <div className={`metric-card ${color}`}>
      <h3>{title}</h3>
      <p className="metric-value">{value}</p>
      <p className="metric-subtitle">
        <span className={`trend-${trend}`}>
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
        </span>
        {subtitle}
      </p>
    </div>
  );
};

interface TradesTableProps {
  trades: Trade[];
}

const TradesTable: React.FC<TradesTableProps> = ({ trades }) => {
  // Demo data if empty
  const demoTrades: Trade[] = [
    {
      id: 'TRADE_001',
      pair: 'GBPJPY',
      pattern: 'Inverse H&S',
      entryPrice: 185.432,
      status: 'active',
      timestamp: new Date().toISOString()
    },
    {
      id: 'TRADE_002',
      pair: 'BTC/USDT',
      pattern: 'Morning Star',
      entryPrice: 43250.00,
      status: 'won',
      profit: 125.50,
      timestamp: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: 'TRADE_003',
      pair: 'EURUSD',
      pattern: 'Bull Flag',
      entryPrice: 1.0875,
      status: 'active',
      timestamp: new Date(Date.now() - 7200000).toISOString()
    }
  ];

  const displayTrades = trades.length > 0 ? trades : demoTrades;

  return (
    <div className="trades-table">
      <table>
        <thead>
          <tr>
            <th>Pair</th>
            <th>Pattern</th>
            <th>Entry</th>
            <th>Status</th>
            <th>P/L</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {displayTrades.map(trade => (
            <tr key={trade.id}>
              <td><strong>{trade.pair}</strong></td>
              <td>{trade.pattern}</td>
              <td>${trade.entryPrice.toFixed(2)}</td>
              <td>
                <span className={`status-badge ${trade.status}`}>
                  {trade.status.toUpperCase()}
                </span>
              </td>
              <td className={trade.profit && trade.profit > 0 ? 'profit-positive' : 'profit-negative'}>
                {trade.profit ? `$${trade.profit.toFixed(2)}` : '-'}
              </td>
              <td>{new Date(trade.timestamp).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const SignalsPanel: React.FC = () => {
  return (
    <div className="signals-panel">
      <div className="signal-card">
        <div className="signal-header">
          <h4>GBPJPY</h4>
          <span className="signal-badge buy">BUY</span>
        </div>
        <p className="signal-pattern">Pattern: Inverse H&S (94% accuracy)</p>
        <p className="signal-price">Entry: 185.432 | TP: 186.132</p>
      </div>

      <div className="signal-card">
        <div className="signal-header">
          <h4>BTC/USDT</h4>
          <span className="signal-badge buy">BUY</span>
        </div>
        <p className="signal-pattern">Pattern: Morning Star (93% accuracy)</p>
        <p className="signal-price">Entry: 43,250 | TP: 44,300</p>
      </div>

      <div className="signal-card">
        <div className="signal-header">
          <h4>EURUSD</h4>
          <span className="signal-badge neutral">NEUTRAL</span>
        </div>
        <p className="signal-pattern">No high-probability pattern detected</p>
        <p className="signal-price">Waiting for signal...</p>
      </div>
    </div>
  );
};

const PerformanceChart: React.FC = () => {
  return (
    <div className="performance-chart">
      <div className="chart-placeholder">
        <p>📊 Performance Chart</p>
        <p className="chart-note">
          Install Chart.js: <code>npm install chart.js react-chartjs-2</code>
        </p>
        <p className="chart-note">
          GitHub Copilot will generate chart implementation when you start coding
        </p>
      </div>
    </div>
  );
};

export default App;
