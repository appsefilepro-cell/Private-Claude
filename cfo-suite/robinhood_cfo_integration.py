#!/usr/bin/env python3
"""
Robinhood Crypto CFO Suite Integration
Integrates Robinhood crypto analysis with Agent 5.0 CFO Suite

This module:
1. Processes Robinhood CSV exports
2. Calculates gains/losses
3. Generates tax reports
4. Assesses investment damages
5. Sends data to Zapier for Google Sheets storage
6. Triggers Slack notifications
7. Creates injury lawyer referrals for losses > $10k

Integration Points:
- Google Sheets via Zapier (automated data storage)
- Slack notifications (automated alerts)
- Legal Division (injury lawyer referrals)
- Tax Division (IRS Form 8949 automation)

Usage:
    python robinhood_cfo_integration.py --csv path/to/robinhood_export.csv --zapier-webhook <url>
"""

import os
import sys
import json
import logging
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import the existing Robinhood analyzers
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from robinhood_crypto_gains_analyzer import (
    loadTrades,
    assessInvestmentDamages,
    generateTaxReport,
    exportToGoogleSheets
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RobinhoodCFOIntegration:
    """Integrates Robinhood crypto analysis with CFO Suite automation"""

    def __init__(self, zapier_webhook: Optional[str] = None, slack_webhook: Optional[str] = None):
        """
        Initialize the CFO Suite integration.

        Args:
            zapier_webhook: Zapier webhook URL for data storage
            slack_webhook: Slack webhook URL for notifications
        """
        self.zapier_webhook = zapier_webhook or os.environ.get('ZAPIER_WEBHOOK_URL')
        self.slack_webhook = slack_webhook or os.environ.get('SLACK_WEBHOOK')

    def process_robinhood_export(self, csv_path: str) -> Dict:
        """
        Process Robinhood CSV export and generate comprehensive analysis.

        Args:
            csv_path: Path to Robinhood CSV export

        Returns:
            Dictionary with complete analysis results
        """
        logger.info(f"Processing Robinhood export: {csv_path}")

        # Load and analyze trades
        df = loadTrades(csv_path)
        logger.info(f"Loaded {len(df)} trades")

        # Generate damage assessment
        damage_assessment = assessInvestmentDamages(df)
        logger.info(f"Damage assessment: Net ${damage_assessment['net_gain_loss']:,.2f}")

        # Generate tax report
        tax_report = generateTaxReport(df)
        logger.info(f"Tax report generated for {len(tax_report['by_year'])} years")

        # Compile complete report
        complete_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_trades': len(df),
            'damage_assessment': damage_assessment,
            'tax_report': tax_report,
            'summary': {
                'total_gain_loss': float(df['gain_or_loss'].sum()),
                'total_cost_basis': float(df['cost_basis'].sum()),
                'total_proceeds': float(df['proceeds'].sum()),
                'short_term_gain': float(df[~df['is_long_term']]['gain_or_loss'].sum()),
                'long_term_gain': float(df[df['is_long_term']]['gain_or_loss'].sum()),
            },
            'assets_analyzed': df['asset_name'].nunique(),
            'years_covered': len(tax_report['by_year'])
        }

        return complete_report

    def send_to_zapier(self, report: Dict) -> bool:
        """
        Send analysis report to Zapier for automated storage in Google Sheets.

        Args:
            report: Complete analysis report

        Returns:
            True if successful, False otherwise
        """
        if not self.zapier_webhook:
            logger.warning("Zapier webhook not configured - skipping integration")
            return False

        try:
            payload = {
                'event': 'robinhood_crypto_analysis',
                'timestamp': datetime.now().isoformat(),
                'report': report
            }

            response = requests.post(
                self.zapier_webhook,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("✅ Data sent to Zapier successfully")
                return True
            else:
                logger.error(f"❌ Zapier webhook failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending to Zapier: {str(e)}")
            return False

    def send_slack_notification(self, report: Dict) -> bool:
        """
        Send Slack notification with analysis summary.

        Args:
            report: Complete analysis report

        Returns:
            True if successful, False otherwise
        """
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured - skipping notification")
            return False

        try:
            # Determine status emoji
            net_gain_loss = report['damage_assessment']['net_gain_loss']
            emoji = "📈" if net_gain_loss >= 0 else "📉"
            status_color = "good" if net_gain_loss >= 0 else "warning" if net_gain_loss > -10000 else "danger"

            # Build Slack message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Robinhood Crypto Analysis Complete"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Trades:*\n{report['total_trades']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Assets Analyzed:*\n{report['assets_analyzed']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Net Gain/Loss:*\n${net_gain_loss:,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Years Covered:*\n{report['years_covered']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Tax Breakdown:*\n• Short-term: ${report['summary']['short_term_gain']:,.2f}\n• Long-term: ${report['summary']['long_term_gain']:,.2f}"
                    }
                }
            ]

            # Add legal referral alert if needed
            if report['damage_assessment']['injury_lawyer_referral']:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *Legal Action Recommended*\n{report['damage_assessment']['recommendation']}"
                    }
                })

            payload = {
                "text": f"Robinhood Crypto Analysis: {net_gain_loss:+,.2f} USD",
                "blocks": blocks,
                "attachments": [{
                    "color": status_color,
                    "text": report['damage_assessment']['recommendation']
                }]
            }

            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✅ Slack notification sent successfully")
                return True
            else:
                logger.error(f"❌ Slack notification failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending Slack notification: {str(e)}")
            return False

    def trigger_legal_referral(self, damage_assessment: Dict) -> bool:
        """
        Trigger legal division referral for significant losses.

        Args:
            damage_assessment: Investment damage assessment

        Returns:
            True if referral triggered, False otherwise
        """
        if not damage_assessment['injury_lawyer_referral']:
            logger.info("No legal referral needed (losses below threshold)")
            return False

        logger.warning(f"⚠️ LEGAL REFERRAL TRIGGERED: Loss of ${abs(damage_assessment['net_gain_loss']):,.2f}")

        # Send to Zapier with legal referral flag
        if self.zapier_webhook:
            try:
                payload = {
                    'event': 'legal_referral_investment_damage',
                    'timestamp': datetime.now().isoformat(),
                    'severity': 'HIGH' if damage_assessment['severe_damages'] else 'MEDIUM',
                    'total_loss': damage_assessment['net_gain_loss'],
                    'recommendation': damage_assessment['recommendation'],
                    'client_data': {
                        'loss_amount': abs(damage_assessment['net_gain_loss']),
                        'asset_breakdown': damage_assessment['asset_breakdown']
                    }
                }

                response = requests.post(
                    self.zapier_webhook,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    logger.info("✅ Legal referral sent to Agent 5.0 Legal Division")
                    return True
                else:
                    logger.error(f"❌ Legal referral failed: HTTP {response.status_code}")
                    return False

            except Exception as e:
                logger.error(f"❌ Error triggering legal referral: {str(e)}")
                return False

        return False

    def run_complete_analysis(self, csv_path: str, export_csv: Optional[Path] = None) -> Dict:
        """
        Run complete analysis and all integrations.

        Args:
            csv_path: Path to Robinhood CSV export
            export_csv: Optional path to export cleaned data

        Returns:
            Complete analysis report
        """
        logger.info("="*60)
        logger.info("ROBINHOOD CRYPTO CFO SUITE INTEGRATION")
        logger.info("="*60)

        # Process the export
        report = self.process_robinhood_export(csv_path)

        # Export to CSV if requested
        if export_csv:
            df = loadTrades(csv_path)
            exportToGoogleSheets(df, export_csv)

        # Send to Zapier (Google Sheets automation)
        zapier_success = self.send_to_zapier(report)

        # Send Slack notification
        slack_success = self.send_slack_notification(report)

        # Trigger legal referral if needed
        legal_referral = self.trigger_legal_referral(report['damage_assessment'])

        # Add integration status to report
        report['integrations'] = {
            'zapier': zapier_success,
            'slack': slack_success,
            'legal_referral': legal_referral
        }

        # Print summary
        self.print_summary(report)

        logger.info("="*60)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*60)

        return report

    def print_summary(self, report: Dict):
        """Print analysis summary to console."""
        print("\n" + "="*60)
        print("ROBINHOOD CRYPTO ANALYSIS SUMMARY")
        print("="*60)

        summary = report['summary']
        damage = report['damage_assessment']

        print(f"\n💰 FINANCIAL SUMMARY:")
        print(f"   Total Gain/Loss: ${summary['total_gain_loss']:,.2f}")
        print(f"   Cost Basis:      ${summary['total_cost_basis']:,.2f}")
        print(f"   Proceeds:        ${summary['total_proceeds']:,.2f}")

        print(f"\n📊 TAX BREAKDOWN:")
        print(f"   Short-term: ${summary['short_term_gain']:,.2f}")
        print(f"   Long-term:  ${summary['long_term_gain']:,.2f}")

        print(f"\n📈 ANALYSIS:")
        print(f"   Trades:  {report['total_trades']}")
        print(f"   Assets:  {report['assets_analyzed']}")
        print(f"   Years:   {report['years_covered']}")

        print(f"\n⚖️ DAMAGE ASSESSMENT:")
        print(f"   {damage['recommendation']}")

        print(f"\n🔗 INTEGRATIONS:")
        integrations = report['integrations']
        print(f"   Zapier (Google Sheets): {'✅' if integrations['zapier'] else '❌'}")
        print(f"   Slack Notifications:    {'✅' if integrations['slack'] else '❌'}")
        print(f"   Legal Referral:         {'✅' if integrations['legal_referral'] else '➖'}")

        print("="*60 + "\n")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Robinhood Crypto CFO Suite Integration - Agent 5.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python robinhood_cfo_integration.py --csv robinhood_export.csv

  # With Zapier integration
  python robinhood_cfo_integration.py --csv robinhood_export.csv --zapier-webhook <url>

  # With full automation (Zapier + Slack)
  python robinhood_cfo_integration.py \\
    --csv robinhood_export.csv \\
    --zapier-webhook <zapier_url> \\
    --slack-webhook <slack_url> \\
    --export cleaned_data.csv

  # Using environment variables
  export ZAPIER_WEBHOOK_URL=<url>
  export SLACK_WEBHOOK=<url>
  python robinhood_cfo_integration.py --csv robinhood_export.csv
        """
    )

    parser.add_argument(
        'csv',
        help='Path to Robinhood CSV export file'
    )

    parser.add_argument(
        '--zapier-webhook',
        help='Zapier webhook URL (or set ZAPIER_WEBHOOK_URL env var)',
        default=None
    )

    parser.add_argument(
        '--slack-webhook',
        help='Slack webhook URL (or set SLACK_WEBHOOK env var)',
        default=None
    )

    parser.add_argument(
        '--export',
        help='Export cleaned data to CSV for Google Sheets',
        type=Path,
        default=None
    )

    parser.add_argument(
        '--json-output',
        help='Save full report as JSON',
        type=Path,
        default=None
    )

    args = parser.parse_args()

    # Validate CSV file
    if not Path(args.csv).exists():
        logger.error(f"CSV file not found: {args.csv}")
        sys.exit(1)

    # Initialize integration
    integration = RobinhoodCFOIntegration(
        zapier_webhook=args.zapier_webhook,
        slack_webhook=args.slack_webhook
    )

    # Run complete analysis
    report = integration.run_complete_analysis(
        csv_path=args.csv,
        export_csv=args.export
    )

    # Save JSON report if requested
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"✅ Full report saved to: {args.json_output}")

    # Exit with appropriate code
    if report['damage_assessment']['severe_damages']:
        sys.exit(2)  # Severe damages - requires immediate attention
    elif report['damage_assessment']['injury_lawyer_referral']:
        sys.exit(1)  # Legal consultation recommended
    else:
        sys.exit(0)  # Normal operation


if __name__ == '__main__':
    main()
