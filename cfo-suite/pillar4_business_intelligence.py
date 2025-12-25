#!/usr/bin/env python3
"""
PILLAR 4: BUSINESS INTELLIGENCE
Complete analytics and reporting including executive dashboards, KPIs, and business insights
Part of Agent 5.0 CFO Suite
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3
from collections import defaultdict


class ReportType(Enum):
    """Report types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL_DETAIL = "financial_detail"
    LEGAL_SUMMARY = "legal_summary"
    TRADING_PERFORMANCE = "trading_performance"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class KPICategory(Enum):
    """KPI categories"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    TRADING = "trading"
    OPERATIONAL = "operational"


class AlertPriority(Enum):
    """Alert priority levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    URGENT = "urgent"


@dataclass
class KPI:
    """Key Performance Indicator"""
    id: str
    name: str
    category: str
    value: float
    target: float
    unit: str
    trend: str  # up, down, stable
    variance_percent: float
    status: str  # on_target, below_target, above_target
    timestamp: str


@dataclass
class Alert:
    """System alert"""
    id: str
    priority: str
    category: str
    title: str
    message: str
    source: str
    timestamp: str
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class Report:
    """Business report"""
    id: str
    report_type: str
    title: str
    period_start: str
    period_end: str
    generated_at: str
    data: Dict[str, Any]
    summary: str
    file_path: Optional[str] = None


class BusinessIntelligence:
    """
    Complete business intelligence system
    Handles dashboards, KPIs, reporting, analytics, and alerts
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize business intelligence"""
        if data_dir is None:
            self.base_dir = Path(__file__).parent
            self.data_dir = self.base_dir / 'data' / 'bi'
        else:
            self.data_dir = data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / 'logs' / 'bi'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.data_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.logger = logging.getLogger('BusinessIntelligence')
        handler = logging.FileHandler(
            self.logs_dir / f'bi_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize database
        self.db_path = self.data_dir / 'bi.db'
        self.init_database()

        # KPI definitions
        self.kpi_definitions = {
            'revenue_growth': {
                'category': KPICategory.FINANCIAL,
                'target': 10.0,
                'unit': '%'
            },
            'profit_margin': {
                'category': KPICategory.FINANCIAL,
                'target': 20.0,
                'unit': '%'
            },
            'case_resolution_rate': {
                'category': KPICategory.LEGAL,
                'target': 80.0,
                'unit': '%'
            },
            'trading_win_rate': {
                'category': KPICategory.TRADING,
                'target': 55.0,
                'unit': '%'
            },
            'roi': {
                'category': KPICategory.FINANCIAL,
                'target': 15.0,
                'unit': '%'
            }
        }

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # KPIs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpis (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                value REAL NOT NULL,
                target REAL NOT NULL,
                unit TEXT NOT NULL,
                trend TEXT NOT NULL,
                variance_percent REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                acknowledged INTEGER DEFAULT 0,
                resolved INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                title TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                data TEXT NOT NULL,
                summary TEXT NOT NULL,
                file_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Analytics snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_snapshots (
                id TEXT PRIMARY KEY,
                snapshot_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metrics TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        self.logger.info("Business Intelligence database initialized successfully")

    # ==================== KPI MANAGEMENT ====================

    def record_kpi(self, kpi: KPI) -> str:
        """Record a KPI measurement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO kpis
            (id, name, category, value, target, unit, trend, variance_percent, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kpi.id,
            kpi.name,
            kpi.category,
            kpi.value,
            kpi.target,
            kpi.unit,
            kpi.trend,
            kpi.variance_percent,
            kpi.status,
            kpi.timestamp
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"KPI recorded: {kpi.name} = {kpi.value}{kpi.unit} (target: {kpi.target}{kpi.unit})")
        return kpi.id

    def calculate_kpi(self, name: str, current_value: float, previous_value: Optional[float] = None) -> KPI:
        """Calculate KPI with status and trend"""
        definition = self.kpi_definitions.get(name, {
            'category': KPICategory.OPERATIONAL,
            'target': current_value,
            'unit': 'units'
        })

        variance = ((current_value - definition['target']) / definition['target'] * 100) if definition['target'] != 0 else 0

        if abs(variance) <= 5:
            status = 'on_target'
        elif variance > 0:
            status = 'above_target'
        else:
            status = 'below_target'

        if previous_value is not None:
            if current_value > previous_value * 1.05:
                trend = 'up'
            elif current_value < previous_value * 0.95:
                trend = 'down'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        return KPI(
            id=f"KPI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{name}",
            name=name,
            category=definition['category'].value if isinstance(definition['category'], KPICategory) else definition['category'],
            value=current_value,
            target=definition['target'],
            unit=definition['unit'],
            trend=trend,
            variance_percent=variance,
            status=status,
            timestamp=datetime.now().isoformat()
        )

    def get_kpis_by_category(self, category: KPICategory, limit: int = 10) -> List[KPI]:
        """Get recent KPIs by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM kpis WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
            (category.value, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        kpis = []
        for row in rows:
            kpis.append(KPI(
                id=row[0],
                name=row[1],
                category=row[2],
                value=row[3],
                target=row[4],
                unit=row[5],
                trend=row[6],
                variance_percent=row[7],
                status=row[8],
                timestamp=row[9]
            ))

        return kpis

    # ==================== ALERT MANAGEMENT ====================

    def create_alert(self, alert: Alert) -> str:
        """Create a new alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts
            (id, priority, category, title, message, source, timestamp, acknowledged, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.id,
            alert.priority,
            alert.category,
            alert.title,
            alert.message,
            alert.source,
            alert.timestamp,
            1 if alert.acknowledged else 0,
            1 if alert.resolved else 0
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Alert created: [{alert.priority}] {alert.title}")
        return alert.id

    def get_unresolved_alerts(self, priority: Optional[AlertPriority] = None) -> List[Alert]:
        """Get unresolved alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if priority:
            cursor.execute(
                "SELECT * FROM alerts WHERE resolved = 0 AND priority = ? ORDER BY timestamp DESC",
                (priority.value,)
            )
        else:
            cursor.execute("SELECT * FROM alerts WHERE resolved = 0 ORDER BY timestamp DESC")

        rows = cursor.fetchall()
        conn.close()

        alerts = []
        for row in rows:
            alerts.append(Alert(
                id=row[0],
                priority=row[1],
                category=row[2],
                title=row[3],
                message=row[4],
                source=row[5],
                timestamp=row[6],
                acknowledged=bool(row[7]),
                resolved=bool(row[8])
            ))

        return alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Alert acknowledged: {alert_id}")

        return updated

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE alerts SET resolved = 1, acknowledged = 1 WHERE id = ?", (alert_id,))

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Alert resolved: {alert_id}")

        return updated

    # ==================== REPORTING ====================

    def generate_executive_dashboard(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive dashboard with data from all pillars"""
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'kpis': {},
            'alerts': {},
            'trends': {}
        }

        # Financial summary
        if 'financial' in pillar_data:
            fin = pillar_data['financial']
            dashboard['summary']['financial'] = {
                'monthly_revenue': fin.get('current_month', {}).get('income', 0),
                'monthly_expenses': fin.get('current_month', {}).get('expenses', 0),
                'net_profit': fin.get('current_month', {}).get('net', 0),
                'accounts_receivable': fin.get('accounts_receivable', 0)
            }

        # Legal summary
        if 'legal' in pillar_data:
            legal = pillar_data['legal']
            dashboard['summary']['legal'] = {
                'active_cases': legal.get('active_cases', 0),
                'upcoming_hearings': legal.get('upcoming_hearings', 0),
                'compliance_status': legal.get('compliance_status', 'unknown')
            }

        # Trading summary
        if 'trading' in pillar_data:
            trading = pillar_data['trading']
            dashboard['summary']['trading'] = {
                'active_bots': trading.get('active_bots', 0),
                'open_positions': trading.get('open_positions', 0),
                'total_pl': trading.get('total_unrealized_pl', 0),
                'today_trades': trading.get('today_trades', 0)
            }

        # Get recent KPIs
        for category in KPICategory:
            kpis = self.get_kpis_by_category(category, limit=5)
            dashboard['kpis'][category.value] = [asdict(kpi) for kpi in kpis]

        # Get unresolved alerts
        critical_alerts = self.get_unresolved_alerts(AlertPriority.CRITICAL)
        urgent_alerts = self.get_unresolved_alerts(AlertPriority.URGENT)

        dashboard['alerts'] = {
            'critical_count': len(critical_alerts),
            'urgent_count': len(urgent_alerts),
            'critical': [asdict(a) for a in critical_alerts[:5]],
            'urgent': [asdict(a) for a in urgent_alerts[:5]]
        }

        return dashboard

    def generate_report(self, report: Report) -> str:
        """Generate and save a report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reports
            (id, report_type, title, period_start, period_end, generated_at, data, summary, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.id,
            report.report_type,
            report.title,
            report.period_start,
            report.period_end,
            report.generated_at,
            json.dumps(report.data),
            report.summary,
            report.file_path
        ))

        conn.commit()
        conn.close()

        # Save report to file
        if not report.file_path:
            report_filename = f"{report.id}_{report.report_type}.json"
            report.file_path = str(self.reports_dir / report_filename)

        with open(report.file_path, 'w') as f:
            json.dump({
                'id': report.id,
                'type': report.report_type,
                'title': report.title,
                'period': {'start': report.period_start, 'end': report.period_end},
                'generated_at': report.generated_at,
                'summary': report.summary,
                'data': report.data
            }, f, indent=2)

        self.logger.info(f"Report generated: {report.title} ({report.id})")
        return report.id

    def generate_comprehensive_report(self, pillar_data: Dict[str, Any],
                                     period_start: str, period_end: str) -> Report:
        """Generate comprehensive report across all pillars"""
        report_data = {
            'financial': pillar_data.get('financial', {}),
            'legal': pillar_data.get('legal', {}),
            'trading': pillar_data.get('trading', {}),
            'kpis': {},
            'alerts': {}
        }

        # Add KPIs
        for category in KPICategory:
            kpis = self.get_kpis_by_category(category, limit=10)
            report_data['kpis'][category.value] = [asdict(kpi) for kpi in kpis]

        # Add alerts
        all_alerts = self.get_unresolved_alerts()
        report_data['alerts'] = {
            'total': len(all_alerts),
            'by_priority': {
                priority.value: len([a for a in all_alerts if a.priority == priority.value])
                for priority in AlertPriority
            }
        }

        # Generate summary
        summary_parts = []
        if 'financial' in pillar_data:
            fin = pillar_data['financial']
            net = fin.get('current_month', {}).get('net', 0)
            summary_parts.append(f"Financial: Net profit ${net:,.2f}")

        if 'trading' in pillar_data:
            trading = pillar_data['trading']
            pl = trading.get('total_unrealized_pl', 0)
            summary_parts.append(f"Trading: P/L ${pl:,.2f}")

        if 'legal' in pillar_data:
            legal = pillar_data['legal']
            cases = legal.get('active_cases', 0)
            summary_parts.append(f"Legal: {cases} active cases")

        summary = ". ".join(summary_parts) if summary_parts else "No data available"

        return Report(
            id=f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            report_type=ReportType.COMPREHENSIVE.value,
            title="CFO Suite Comprehensive Report",
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.now().isoformat(),
            data=report_data,
            summary=summary
        )

    # ==================== ANALYTICS ====================

    def create_analytics_snapshot(self, snapshot_type: str, metrics: Dict[str, Any]) -> str:
        """Create an analytics snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        snapshot_id = f"SNAP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cursor.execute('''
            INSERT INTO analytics_snapshots
            (id, snapshot_type, timestamp, metrics)
            VALUES (?, ?, ?, ?)
        ''', (
            snapshot_id,
            snapshot_type,
            datetime.now().isoformat(),
            json.dumps(metrics)
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Analytics snapshot created: {snapshot_type}")
        return snapshot_id

    def get_trend_analysis(self, metric_name: str, days: int = 30) -> Dict[str, Any]:
        """Analyze trends for a specific metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute('''
            SELECT timestamp, value FROM kpis
            WHERE name = ? AND timestamp >= ?
            ORDER BY timestamp
        ''', (metric_name, start_date))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                'metric': metric_name,
                'message': 'No data available for trend analysis'
            }

        values = [row[1] for row in rows]
        timestamps = [row[0] for row in rows]

        # Simple trend calculation
        if len(values) > 1:
            trend_direction = 'up' if values[-1] > values[0] else 'down' if values[-1] < values[0] else 'stable'
            change_percent = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        else:
            trend_direction = 'stable'
            change_percent = 0

        return {
            'metric': metric_name,
            'period_days': days,
            'data_points': len(values),
            'current_value': values[-1] if values else 0,
            'starting_value': values[0] if values else 0,
            'min_value': min(values) if values else 0,
            'max_value': max(values) if values else 0,
            'average_value': sum(values) / len(values) if values else 0,
            'trend_direction': trend_direction,
            'change_percent': change_percent,
            'timestamps': timestamps[-10:],  # Last 10 timestamps
            'values': values[-10:]  # Last 10 values
        }


def main():
    """Demo and testing"""
    print("\n" + "="*70)
    print("PILLAR 4: BUSINESS INTELLIGENCE")
    print("="*70 + "\n")

    bi = BusinessIntelligence()

    # Demo: Record sample KPIs
    profit_margin_kpi = bi.calculate_kpi('profit_margin', 22.5, 20.0)
    kpi_id = bi.record_kpi(profit_margin_kpi)
    print(f"Sample KPI recorded: {profit_margin_kpi.name} = {profit_margin_kpi.value}{profit_margin_kpi.unit}")

    # Demo: Create sample alert
    sample_alert = Alert(
        id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        priority=AlertPriority.WARNING.value,
        category="financial",
        title="Budget threshold exceeded",
        message="Marketing budget has exceeded 80% threshold",
        source="financial_operations",
        timestamp=datetime.now().isoformat()
    )
    alert_id = bi.create_alert(sample_alert)
    print(f"Sample alert created: [{sample_alert.priority}] {sample_alert.title}")

    # Demo: Generate executive dashboard
    sample_data = {
        'financial': {
            'current_month': {'income': 50000, 'expenses': 35000, 'net': 15000},
            'accounts_receivable': 25000
        },
        'legal': {
            'active_cases': 5,
            'upcoming_hearings': 2,
            'compliance_status': 'compliant'
        },
        'trading': {
            'active_bots': 3,
            'open_positions': 7,
            'total_unrealized_pl': 1250,
            'today_trades': 15
        }
    }

    dashboard = bi.generate_executive_dashboard(sample_data)

    print("\n" + "-"*70)
    print("EXECUTIVE DASHBOARD")
    print("-"*70)
    print(f"\nFinancial Summary:")
    if 'financial' in dashboard['summary']:
        fin = dashboard['summary']['financial']
        print(f"  Monthly Revenue: ${fin['monthly_revenue']:,.2f}")
        print(f"  Monthly Expenses: ${fin['monthly_expenses']:,.2f}")
        print(f"  Net Profit: ${fin['net_profit']:,.2f}")

    print(f"\nLegal Summary:")
    if 'legal' in dashboard['summary']:
        legal = dashboard['summary']['legal']
        print(f"  Active Cases: {legal['active_cases']}")
        print(f"  Upcoming Hearings: {legal['upcoming_hearings']}")

    print(f"\nTrading Summary:")
    if 'trading' in dashboard['summary']:
        trading = dashboard['summary']['trading']
        print(f"  Active Bots: {trading['active_bots']}")
        print(f"  Open Positions: {trading['open_positions']}")
        print(f"  Total P/L: ${trading['total_pl']:,.2f}")

    print(f"\nAlerts:")
    print(f"  Critical: {dashboard['alerts']['critical_count']}")
    print(f"  Urgent: {dashboard['alerts']['urgent_count']}")

    print("\n" + "="*70)
    print("Business Intelligence Module Ready")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
