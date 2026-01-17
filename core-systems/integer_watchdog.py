#!/usr/bin/env python3
"""
Integer Watchdog - Financial Monitoring System
Part 2 Implementation - Pillar A Integration

Real-time cashflow spike detection and alert system for restitution tracking.
Monitors financial data from multiple sources including Robinhood integration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntegerWatchdog:
    """
    Financial monitoring system that tracks cashflow spikes and anomalies.
    
    Key Features:
    - Real-time cashflow spike detection
    - Multi-source financial data aggregation
    - Alert generation for restitution tracking
    - Integration with CFO Master AI Suite
    """
    
    def __init__(self, alert_threshold: float = 10000.0):
        """
        Initialize Integer Watchdog.
        
        Args:
            alert_threshold: Minimum amount to trigger alert (default $10,000)
        """
        self.alert_threshold = alert_threshold
        self.monitored_accounts = []
        self.cashflow_events = []
        self.alerts = []
        self.is_monitoring = False
        
    def add_monitored_account(self, account_info: Dict) -> None:
        """
        Add a financial account to monitoring.
        
        Args:
            account_info: Dictionary with account details
                - account_id: Unique identifier
                - account_name: Human-readable name
                - account_type: Type (trading, banking, etc.)
                - source: Data source (robinhood, etc.)
        """
        self.monitored_accounts.append({
            **account_info,
            'added_date': datetime.now().isoformat(),
            'status': 'active'
        })
        logger.info(f"Added monitored account: {account_info.get('account_name')}")
    
    def ingest_financial_data(self, data_file: str) -> Dict:
        """
        Ingest financial data from JSON file (e.g., from Robinhood parser).
        
        Args:
            data_file: Path to JSON data file
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process cashflow spikes
            spikes = data.get('cashflow_spikes', [])
            for spike in spikes:
                self._process_spike(spike, data.get('source', 'unknown'))
            
            # Process transactions
            transactions = data.get('transactions', [])
            self._analyze_transactions(transactions)
            
            result = {
                'success': True,
                'source': data.get('source'),
                'transactions_processed': len(transactions),
                'spikes_detected': len(spikes),
                'alerts_generated': len([a for a in self.alerts if a.get('recent', False)]),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Ingested data from {result['source']}: "
                       f"{result['transactions_processed']} transactions, "
                       f"{result['spikes_detected']} spikes")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ingesting data: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_spike(self, spike_data: Dict, source: str) -> None:
        """Process a detected cashflow spike and generate alert if needed."""
        # Check if spike exceeds threshold
        net_flow = spike_data.get('net_flow', 0)
        inflow = spike_data.get('inflow', 0)
        
        if abs(net_flow) >= self.alert_threshold or inflow >= self.alert_threshold:
            alert = {
                'alert_id': f"ALERT_{len(self.alerts) + 1}",
                'alert_type': 'CASHFLOW_SPIKE',
                'severity': self._calculate_severity(net_flow, inflow),
                'source': source,
                'month': spike_data.get('month'),
                'inflow': inflow,
                'outflow': spike_data.get('outflow', 0),
                'net_flow': net_flow,
                'threshold': self.alert_threshold,
                'flagged_for_restitution': True,
                'status': 'PENDING_REVIEW',
                'detected_date': datetime.now().isoformat(),
                'recent': True
            }
            
            self.alerts.append(alert)
            logger.warning(f"ALERT GENERATED: {alert['alert_type']} - "
                          f"{alert['month']} - Net Flow: ${net_flow:,.2f}")
    
    def _calculate_severity(self, net_flow: float, inflow: float) -> str:
        """Calculate alert severity based on amounts."""
        max_amount = max(abs(net_flow), inflow)
        
        if max_amount >= 50000:
            return 'CRITICAL'
        elif max_amount >= 25000:
            return 'HIGH'
        elif max_amount >= 10000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _analyze_transactions(self, transactions: List[Dict]) -> None:
        """Analyze transactions for patterns and anomalies."""
        # Group by type
        by_type = {}
        total_volume = 0
        
        for txn in transactions:
            txn_type = txn.get('transaction_type', 'OTHER')
            amount = abs(txn.get('amount', 0))
            
            if txn_type not in by_type:
                by_type[txn_type] = {'count': 0, 'volume': 0}
            
            by_type[txn_type]['count'] += 1
            by_type[txn_type]['volume'] += amount
            total_volume += amount
        
        # Store event for analysis
        event = {
            'event_type': 'TRANSACTION_BATCH',
            'transaction_count': len(transactions),
            'total_volume': total_volume,
            'breakdown_by_type': by_type,
            'analyzed_date': datetime.now().isoformat()
        }
        
        self.cashflow_events.append(event)
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get all alerts pending review."""
        return [a for a in self.alerts if a.get('status') == 'PENDING_REVIEW']
    
    def get_critical_alerts(self) -> List[Dict]:
        """Get all critical severity alerts."""
        return [a for a in self.alerts if a.get('severity') == 'CRITICAL']
    
    def mark_alert_reviewed(self, alert_id: str, notes: str = "") -> bool:
        """
        Mark an alert as reviewed.
        
        Args:
            alert_id: Alert identifier
            notes: Optional review notes
            
        Returns:
            True if successful
        """
        for alert in self.alerts:
            if alert.get('alert_id') == alert_id:
                alert['status'] = 'REVIEWED'
                alert['reviewed_date'] = datetime.now().isoformat()
                alert['review_notes'] = notes
                alert['recent'] = False
                logger.info(f"Alert {alert_id} marked as reviewed")
                return True
        
        return False
    
    def generate_restitution_report(self, output_path: str) -> bool:
        """
        Generate a report for restitution inclusion.
        
        Args:
            output_path: Path to save report
            
        Returns:
            True if successful
        """
        try:
            report = {
                'report_type': 'RESTITUTION_TRACKING',
                'generated_date': datetime.now().isoformat(),
                'monitoring_threshold': self.alert_threshold,
                'total_alerts': len(self.alerts),
                'pending_alerts': len(self.get_pending_alerts()),
                'critical_alerts': len(self.get_critical_alerts()),
                'alerts_detail': self.alerts,
                'monitored_accounts': self.monitored_accounts,
                'cashflow_events': self.cashflow_events,
                'summary': self._generate_summary()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Restitution report generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        total_flagged_amount = sum(
            abs(a.get('net_flow', 0)) for a in self.alerts 
            if a.get('flagged_for_restitution', False)
        )
        
        return {
            'total_flagged_for_restitution': f"${total_flagged_amount:,.2f}",
            'alerts_by_severity': {
                'CRITICAL': len([a for a in self.alerts if a.get('severity') == 'CRITICAL']),
                'HIGH': len([a for a in self.alerts if a.get('severity') == 'HIGH']),
                'MEDIUM': len([a for a in self.alerts if a.get('severity') == 'MEDIUM']),
                'LOW': len([a for a in self.alerts if a.get('severity') == 'LOW'])
            },
            'accounts_monitored': len(self.monitored_accounts)
        }
    
    async def start_monitoring(self, interval_seconds: int = 300) -> None:
        """
        Start continuous monitoring (async).
        
        Args:
            interval_seconds: Check interval in seconds (default 5 minutes)
        """
        self.is_monitoring = True
        logger.info(f"Integer Watchdog monitoring started (interval: {interval_seconds}s)")
        
        while self.is_monitoring:
            # Check for new data files to ingest
            await asyncio.sleep(interval_seconds)
            
            # In production, this would scan for new data files
            # or poll APIs for updates
            logger.info("Monitoring cycle completed - checking for new data...")
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self.is_monitoring = False
        logger.info("Integer Watchdog monitoring stopped")
    
    def print_status_report(self) -> None:
        """Print a status report to console."""
        print("\n" + "=" * 70)
        print("INTEGER WATCHDOG - STATUS REPORT")
        print("=" * 70)
        print(f"\nMonitoring Threshold: ${self.alert_threshold:,.2f}")
        print(f"Monitored Accounts: {len(self.monitored_accounts)}")
        print(f"Total Alerts Generated: {len(self.alerts)}")
        print(f"Pending Review: {len(self.get_pending_alerts())}")
        print(f"Critical Alerts: {len(self.get_critical_alerts())}")
        
        if self.alerts:
            print("\nRECENT ALERTS:")
            for alert in self.alerts[-5:]:  # Show last 5
                print(f"  • [{alert['severity']}] {alert['month']} - "
                      f"Net: ${alert['net_flow']:,.2f} - "
                      f"Status: {alert['status']}")
        
        print("\n" + "=" * 70 + "\n")


async def main():
    """Example usage of Integer Watchdog."""
    watchdog = IntegerWatchdog(alert_threshold=10000.0)
    
    print("Integer Watchdog - Part 2 Implementation")
    print("Financial monitoring system for cashflow spike detection\n")
    
    # Example: Add monitored account
    watchdog.add_monitored_account({
        'account_id': 'RH_001',
        'account_name': 'Robinhood Trading Account',
        'account_type': 'TRADING',
        'source': 'robinhood'
    })
    
    # Example: Ingest data (would use actual file path)
    print("\nExample integration with Robinhood parser:")
    print("  1. Parse Robinhood data: parser.parse_transaction_csv('transactions.csv')")
    print("  2. Export for watchdog: parser.export_to_integer_watchdog('data.json')")
    print("  3. Ingest into watchdog: watchdog.ingest_financial_data('data.json')")
    print("  4. Generate report: watchdog.generate_restitution_report('report.json')")
    
    watchdog.print_status_report()


if __name__ == "__main__":
    asyncio.run(main())
