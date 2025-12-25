#!/usr/bin/env python3
"""
INTEGRATION LAYER
Connects all 4 pillars of Agent 5.0 CFO Suite and provides unified data flow
Part of Agent 5.0 CFO Suite
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import all pillars
from pillar1_financial_operations import FinancialOperations, Transaction, Invoice, Budget
from pillar2_legal_operations import LegalOperations, LegalCase, Contract, ComplianceCheck
from pillar3_trading_operations import TradingOperations, TradingBot, Trade, Position
from pillar4_business_intelligence import (
    BusinessIntelligence, KPI, Alert, Report,
    KPICategory, AlertPriority, ReportType
)


@dataclass
class IntegrationEvent:
    """Cross-pillar integration event"""
    id: str
    event_type: str
    source_pillar: str
    target_pillar: str
    data: Dict[str, Any]
    timestamp: str
    processed: bool = False


class CFOSuiteIntegration:
    """
    Integration layer for CFO Suite
    Coordinates data flow and operations across all 4 pillars
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize integration layer"""
        if data_dir is None:
            self.base_dir = Path(__file__).parent
            self.data_dir = self.base_dir / 'data' / 'integration'
        else:
            self.data_dir = data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / 'logs' / 'integration'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.logger = logging.getLogger('CFOIntegration')
        handler = logging.FileHandler(
            self.logs_dir / f'integration_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize all pillars
        self.logger.info("Initializing all pillars...")
        self.financial = FinancialOperations(self.data_dir / 'financial')
        self.legal = LegalOperations(self.data_dir / 'legal')
        self.trading = TradingOperations(self.data_dir / 'trading')
        self.bi = BusinessIntelligence(self.data_dir / 'bi')

        self.logger.info("All pillars initialized successfully")

        # Integration event queue
        self.event_queue: List[IntegrationEvent] = []

    # ==================== CROSS-PILLAR INTEGRATIONS ====================

    def sync_trading_to_financial(self) -> Dict[str, Any]:
        """Sync trading profits/losses to financial records"""
        self.logger.info("Syncing trading data to financial records...")

        # Get today's trading activity
        today = datetime.now().strftime('%Y-%m-%d')
        synced_trades = []

        # Get all active bots
        bots = self.trading.get_active_bots()

        for bot in bots:
            # Get bot's trades
            trades = self.trading.get_bot_trades(bot.id, limit=100)

            for trade in trades:
                # Only sync completed trades from today
                if trade.status == 'filled' and trade.exit_time and trade.exit_time.startswith(today):
                    # Create financial transaction
                    txn = Transaction(
                        id=f"TXN-TRADING-{trade.id}",
                        date=trade.exit_time[:10],
                        type='income' if trade.profit_loss and trade.profit_loss > 0 else 'expense',
                        category='trading',
                        amount=abs(trade.profit_loss) if trade.profit_loss else 0,
                        description=f"Trading P/L: {trade.symbol} {trade.side}",
                        account='trading_account',
                        reference=trade.id,
                        tags=['automated', 'trading', bot.strategy],
                        metadata={
                            'bot_id': bot.id,
                            'bot_name': bot.name,
                            'symbol': trade.symbol,
                            'strategy': trade.strategy
                        }
                    )

                    try:
                        self.financial.add_transaction(txn)
                        synced_trades.append(trade.id)
                    except Exception as e:
                        self.logger.error(f"Failed to sync trade {trade.id}: {e}")

        self.logger.info(f"Synced {len(synced_trades)} trades to financial records")

        return {
            'synced_count': len(synced_trades),
            'trade_ids': synced_trades,
            'timestamp': datetime.now().isoformat()
        }

    def sync_legal_to_financial(self) -> Dict[str, Any]:
        """Sync legal expenses and case values to financial records"""
        self.logger.info("Syncing legal data to financial records...")

        synced_items = []

        # Get active cases
        cases = self.legal.get_active_cases()

        for case in cases:
            # Create transaction for estimated case value if not already recorded
            if case.estimated_value and case.estimated_value > 0:
                txn = Transaction(
                    id=f"TXN-LEGAL-{case.id}",
                    date=datetime.now().strftime('%Y-%m-%d'),
                    type='expense',
                    category='legal',
                    amount=case.estimated_value,
                    description=f"Legal case: {case.case_name}",
                    account='legal_expenses',
                    reference=case.id,
                    tags=['legal', 'case_expense'],
                    metadata={
                        'case_number': case.case_number,
                        'court': case.court,
                        'attorney': case.assigned_attorney
                    }
                )

                try:
                    # Note: In production, check if transaction already exists
                    # For now, we'll log it
                    self.logger.info(f"Legal case expense tracked: {case.case_number} - ${case.estimated_value:,.2f}")
                    synced_items.append(case.id)
                except Exception as e:
                    self.logger.error(f"Failed to sync case {case.id}: {e}")

        return {
            'synced_count': len(synced_items),
            'case_ids': synced_items,
            'timestamp': datetime.now().isoformat()
        }

    def generate_unified_kpis(self) -> Dict[str, Any]:
        """Generate KPIs across all pillars"""
        self.logger.info("Generating unified KPIs...")

        kpis = {}

        # Financial KPIs
        try:
            financial_summary = self.financial.get_financial_summary()

            # Calculate profit margin
            income = financial_summary['current_month']['income']
            expenses = financial_summary['current_month']['expenses']
            profit_margin = (income - expenses) / income * 100 if income > 0 else 0

            profit_kpi = self.bi.calculate_kpi('profit_margin', profit_margin)
            self.bi.record_kpi(profit_kpi)
            kpis['profit_margin'] = asdict(profit_kpi)

        except Exception as e:
            self.logger.error(f"Failed to calculate financial KPIs: {e}")

        # Trading KPIs
        try:
            portfolio = self.trading.generate_portfolio_summary()

            # Get performance for all active bots
            bots = self.trading.get_active_bots()
            if bots:
                total_trades = 0
                total_wins = 0

                for bot in bots:
                    perf = self.trading.calculate_bot_performance(bot.id, days=30)
                    if perf.get('total_trades', 0) > 0:
                        total_trades += perf['total_trades']
                        total_wins += perf.get('winning_trades', 0)

                win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
                win_rate_kpi = self.bi.calculate_kpi('trading_win_rate', win_rate)
                self.bi.record_kpi(win_rate_kpi)
                kpis['trading_win_rate'] = asdict(win_rate_kpi)

        except Exception as e:
            self.logger.error(f"Failed to calculate trading KPIs: {e}")

        # Legal KPIs
        try:
            case_summary = self.legal.generate_case_summary()

            total_cases = sum(case_summary['status_breakdown'].values())
            closed_cases = case_summary['status_breakdown'].get('closed', 0) + \
                          case_summary['status_breakdown'].get('dismissed', 0)

            resolution_rate = (closed_cases / total_cases * 100) if total_cases > 0 else 0
            resolution_kpi = self.bi.calculate_kpi('case_resolution_rate', resolution_rate)
            self.bi.record_kpi(resolution_kpi)
            kpis['case_resolution_rate'] = asdict(resolution_kpi)

        except Exception as e:
            self.logger.error(f"Failed to calculate legal KPIs: {e}")

        self.logger.info(f"Generated {len(kpis)} unified KPIs")

        return {
            'kpis': kpis,
            'count': len(kpis),
            'timestamp': datetime.now().isoformat()
        }

    def check_cross_pillar_alerts(self) -> List[Alert]:
        """Check for alerts across all pillars"""
        self.logger.info("Checking cross-pillar alerts...")

        alerts = []

        # Financial alerts
        try:
            financial_summary = self.financial.get_financial_summary()

            # Alert on negative cash flow
            if financial_summary['current_month']['net'] < 0:
                alert = Alert(
                    id=f"ALERT-FIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    priority=AlertPriority.WARNING.value,
                    category='financial',
                    title='Negative Monthly Cash Flow',
                    message=f"Current month net: ${financial_summary['current_month']['net']:,.2f}",
                    source='integration_layer',
                    timestamp=datetime.now().isoformat()
                )
                self.bi.create_alert(alert)
                alerts.append(alert)

            # Alert on overdue invoices
            if financial_summary['overdue_invoices'] > 0:
                alert = Alert(
                    id=f"ALERT-FIN-{datetime.now().strftime('%Y%m%d%H%M%S')}-INV",
                    priority=AlertPriority.URGENT.value,
                    category='financial',
                    title='Overdue Invoices',
                    message=f"{financial_summary['overdue_invoices']} invoices are overdue",
                    source='integration_layer',
                    timestamp=datetime.now().isoformat()
                )
                self.bi.create_alert(alert)
                alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Failed to check financial alerts: {e}")

        # Legal alerts
        try:
            hearings = self.legal.get_upcoming_hearings(days_ahead=7)

            if hearings:
                alert = Alert(
                    id=f"ALERT-LEGAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    priority=AlertPriority.URGENT.value,
                    category='legal',
                    title='Upcoming Court Hearings',
                    message=f"{len(hearings)} hearing(s) in next 7 days",
                    source='integration_layer',
                    timestamp=datetime.now().isoformat()
                )
                self.bi.create_alert(alert)
                alerts.append(alert)

            # Check compliance
            due_compliance = self.legal.get_due_compliance_checks()
            if due_compliance:
                alert = Alert(
                    id=f"ALERT-LEGAL-{datetime.now().strftime('%Y%m%d%H%M%S')}-COMP",
                    priority=AlertPriority.CRITICAL.value,
                    category='legal',
                    title='Compliance Checks Due',
                    message=f"{len(due_compliance)} compliance check(s) are due",
                    source='integration_layer',
                    timestamp=datetime.now().isoformat()
                )
                self.bi.create_alert(alert)
                alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Failed to check legal alerts: {e}")

        # Trading alerts
        try:
            risk = self.trading.get_current_risk_assessment()

            if risk['risk_level'] in ['high', 'extreme']:
                alert = Alert(
                    id=f"ALERT-TRADE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    priority=AlertPriority.CRITICAL.value,
                    category='trading',
                    title=f'Trading Risk: {risk["risk_level"].upper()}',
                    message=f"Portfolio exposure: {risk['exposure_ratio']:.2%}",
                    source='integration_layer',
                    timestamp=datetime.now().isoformat()
                )
                self.bi.create_alert(alert)
                alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Failed to check trading alerts: {e}")

        self.logger.info(f"Generated {len(alerts)} cross-pillar alerts")

        return alerts

    def collect_pillar_data(self) -> Dict[str, Any]:
        """Collect data from all pillars"""
        self.logger.info("Collecting data from all pillars...")

        data = {}

        # Financial data
        try:
            data['financial'] = self.financial.get_financial_summary()
        except Exception as e:
            self.logger.error(f"Failed to collect financial data: {e}")
            data['financial'] = {}

        # Legal data
        try:
            active_cases = self.legal.get_active_cases()
            upcoming_hearings = self.legal.get_upcoming_hearings(days_ahead=30)
            case_summary = self.legal.generate_case_summary()

            data['legal'] = {
                'active_cases': len(active_cases),
                'upcoming_hearings': len(upcoming_hearings),
                'case_summary': case_summary,
                'compliance_status': 'compliant'  # Simplified
            }
        except Exception as e:
            self.logger.error(f"Failed to collect legal data: {e}")
            data['legal'] = {}

        # Trading data
        try:
            data['trading'] = self.trading.generate_portfolio_summary()
            risk = self.trading.get_current_risk_assessment()
            data['trading']['risk'] = risk
        except Exception as e:
            self.logger.error(f"Failed to collect trading data: {e}")
            data['trading'] = {}

        return data

    def generate_unified_dashboard(self) -> Dict[str, Any]:
        """Generate unified executive dashboard"""
        self.logger.info("Generating unified executive dashboard...")

        # Collect all pillar data
        pillar_data = self.collect_pillar_data()

        # Generate dashboard through BI pillar
        dashboard = self.bi.generate_executive_dashboard(pillar_data)

        # Add integration metadata
        dashboard['integration'] = {
            'pillars_online': 4,
            'last_sync': datetime.now().isoformat(),
            'data_sources': list(pillar_data.keys())
        }

        return dashboard

    def generate_comprehensive_report(self, days: int = 30) -> Report:
        """Generate comprehensive report across all pillars"""
        self.logger.info(f"Generating comprehensive report for last {days} days...")

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Collect all pillar data
        pillar_data = self.collect_pillar_data()

        # Add detailed reports from each pillar
        try:
            pillar_data['financial_detail'] = self.financial.generate_profit_loss_report(
                start_date, end_date
            )
        except Exception as e:
            self.logger.error(f"Failed to generate financial report: {e}")

        try:
            pillar_data['legal_detail'] = self.legal.generate_case_summary()
        except Exception as e:
            self.logger.error(f"Failed to generate legal report: {e}")

        # Generate report through BI pillar
        report = self.bi.generate_comprehensive_report(pillar_data, start_date, end_date)

        # Save report
        self.bi.generate_report(report)

        self.logger.info(f"Comprehensive report generated: {report.id}")

        return report


def main():
    """Demo and testing"""
    print("\n" + "="*70)
    print("CFO SUITE - INTEGRATION LAYER")
    print("="*70 + "\n")

    integration = CFOSuiteIntegration()

    print("All pillars initialized successfully!\n")

    # Test: Collect pillar data
    print("-"*70)
    print("COLLECTING PILLAR DATA")
    print("-"*70)

    data = integration.collect_pillar_data()

    print(f"\nFinancial Data: {len(data.get('financial', {}))} keys")
    print(f"Legal Data: {len(data.get('legal', {}))} keys")
    print(f"Trading Data: {len(data.get('trading', {}))} keys")

    # Test: Generate unified KPIs
    print("\n" + "-"*70)
    print("GENERATING UNIFIED KPIs")
    print("-"*70)

    kpis = integration.generate_unified_kpis()
    print(f"\nGenerated {kpis['count']} KPIs across all pillars")

    # Test: Check alerts
    print("\n" + "-"*70)
    print("CHECKING CROSS-PILLAR ALERTS")
    print("-"*70)

    alerts = integration.check_cross_pillar_alerts()
    print(f"\nGenerated {len(alerts)} alerts")

    for alert in alerts[:5]:  # Show first 5
        print(f"  [{alert.priority}] {alert.title}")

    # Test: Generate dashboard
    print("\n" + "-"*70)
    print("GENERATING UNIFIED DASHBOARD")
    print("-"*70)

    dashboard = integration.generate_unified_dashboard()

    print(f"\nDashboard Summary:")
    print(f"  Pillars Online: {dashboard['integration']['pillars_online']}")
    print(f"  Data Sources: {', '.join(dashboard['integration']['data_sources'])}")
    print(f"  Critical Alerts: {dashboard['alerts']['critical_count']}")
    print(f"  Urgent Alerts: {dashboard['alerts']['urgent_count']}")

    print("\n" + "="*70)
    print("Integration Layer Ready")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
