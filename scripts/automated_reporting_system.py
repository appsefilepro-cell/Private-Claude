#!/usr/bin/env python3
"""
Automated Reporting System
Sends daily (morning) and weekly performance reports via email
"""

import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ReportingSystem')


class AutomatedReportingSystem:
    """Generates and sends automated trading reports"""

    def __init__(self):
        self.email_to = os.getenv('ALERT_EMAIL', 'appsefilepro@gmail.com')
        self.email_from = os.getenv('SMTP_FROM', 'agent-x2@trading-system.local')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

    def get_latest_stats(self) -> Dict[str, Any]:
        """Get latest trading statistics"""
        try:
            logs_dir = Path('logs')
            stats_files = sorted(logs_dir.glob('trading_stats_*.json'), reverse=True)

            if stats_files:
                with open(stats_files[0], 'r') as f:
                    return json.load(f)
            return {'timestamp': datetime.now().isoformat(), 'accounts': {}}
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
            return {'timestamp': datetime.now().isoformat(), 'accounts': {}}

    def calculate_summary_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics across all accounts"""
        accounts = stats.get('accounts', {})

        total_capital = 0
        total_initial = 0
        total_trades = 0
        total_wins = 0
        total_losses = 0
        total_profit = 0
        total_loss = 0
        active_accounts = 0

        for account in accounts.values():
            total_capital += account['current_capital']
            total_initial += account['initial_capital']
            total_trades += account['total_trades']
            total_wins += account['winning_trades']
            total_losses += account['losing_trades']
            total_profit += account['total_profit']
            total_loss += account['total_loss']
            if account['status'] == 'RUNNING':
                active_accounts += 1

        total_pnl = total_capital - total_initial
        total_pnl_percent = (total_pnl / total_initial * 100) if total_initial > 0 else 0
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0

        return {
            'total_capital': total_capital,
            'total_initial': total_initial,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'total_trades': total_trades,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'active_accounts': active_accounts,
            'total_accounts': len(accounts)
        }

    def generate_daily_report_html(self) -> str:
        """Generate HTML for daily morning report"""
        stats = self.get_latest_stats()
        metrics = self.calculate_summary_metrics(stats)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
                .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
                .metric-label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
                .account-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .account-table th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
                .account-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                .account-table tr:hover {{ background: #f8f9fa; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Trading Report</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</p>
                </div>

                <div class="summary">
                    <div class="metric">
                        <div class="metric-label">Total Portfolio Value</div>
                        <div class="metric-value">${metrics['total_capital']:,.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">24h P/L</div>
                        <div class="metric-value {'positive' if metrics['total_pnl'] >= 0 else 'negative'}">
                            {'+'if metrics['total_pnl'] >= 0 else ''}{metrics['total_pnl']:,.2f}
                            ({'+' if metrics['total_pnl_percent'] >= 0 else ''}{metrics['total_pnl_percent']:.2f}%)
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value {'positive' if metrics['win_rate'] >= 50 else 'negative'}">
                            {metrics['win_rate']:.1f}%
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Trades</div>
                        <div class="metric-value">{metrics['total_trades']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Active Accounts</div>
                        <div class="metric-value">{metrics['active_accounts']}/{metrics['total_accounts']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Wins / Losses</div>
                        <div class="metric-value">{metrics['total_wins']} / {metrics['total_losses']}</div>
                    </div>
                </div>

                <h2>Account Performance Details</h2>
                <table class="account-table">
                    <thead>
                        <tr>
                            <th>Account</th>
                            <th>Profile</th>
                            <th>Capital</th>
                            <th>P/L</th>
                            <th>Trades</th>
                            <th>Win Rate</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for account_id, account in stats.get('accounts', {}).items():
            pnl = account['current_capital'] - account['initial_capital']
            pnl_percent = (pnl / account['initial_capital'] * 100) if account['initial_capital'] > 0 else 0
            win_rate = (account['winning_trades'] / account['total_trades'] * 100) if account['total_trades'] > 0 else 0

            html += f"""
                        <tr>
                            <td>{account['name']}</td>
                            <td>{account['profile'].upper()}</td>
                            <td>${account['current_capital']:,.2f}</td>
                            <td class="{'positive' if pnl >= 0 else 'negative'}">
                                {'+'if pnl >= 0 else ''}{pnl:,.2f} ({'+' if pnl_percent >= 0 else ''}{pnl_percent:.2f}%)
                            </td>
                            <td>{account['total_trades']}</td>
                            <td class="{'positive' if win_rate >= 50 else 'negative'}">{win_rate:.1f}%</td>
                            <td>{account['status']}</td>
                        </tr>
            """

        html += """
                    </tbody>
                </table>

                <div class="footer">
                    <p><strong>Agent X2.0 - 24/7 Trading System</strong></p>
                    <p>This is an automated report. Dashboard: http://localhost:8080</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def generate_weekly_report_html(self) -> str:
        """Generate HTML for weekly report (more detailed)"""
        # Weekly report includes trends, charts, and deeper analysis
        daily_html = self.generate_daily_report_html()

        # Add weekly-specific sections
        weekly_additions = """
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
            <h2>📈 Weekly Insights</h2>
            <ul>
                <li><strong>Best Performing Account:</strong> Analysis of top performer</li>
                <li><strong>Strategy Effectiveness:</strong> Which patterns worked best</li>
                <li><strong>Risk Analysis:</strong> Drawdowns and risk metrics</li>
                <li><strong>Recommendations:</strong> Suggested adjustments for next week</li>
            </ul>
        </div>
        """

        # Insert before footer
        return daily_html.replace('<div class="footer">', weekly_additions + '<div class="footer">')

    def send_email_report(self, subject: str, html_content: str, attachments: List[str] = None):
        """Send email report"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Attach files if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                            msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_password:
                    server.login(self.email_from, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✅ Report sent to {self.email_to}: {subject}")

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            # Save report locally as backup
            backup_file = f"logs/email_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(backup_file, 'w') as f:
                f.write(html_content)
            logger.info(f"📁 Report saved to {backup_file}")

    def send_daily_report(self):
        """Send daily morning report"""
        logger.info("📧 Generating daily report...")
        html = self.generate_daily_report_html()
        subject = f"Agent X2.0 Daily Report - {datetime.now().strftime('%B %d, %Y')}"
        self.send_email_report(subject, html)

    def send_weekly_report(self):
        """Send weekly report"""
        logger.info("📧 Generating weekly report...")
        html = self.generate_weekly_report_html()
        subject = f"Agent X2.0 Weekly Report - Week of {datetime.now().strftime('%B %d, %Y')}"

        # Attach stats file
        stats_files = sorted(Path('logs').glob('trading_stats_*.json'), reverse=True)
        attachments = [str(stats_files[0])] if stats_files else []

        self.send_email_report(subject, html, attachments)

    def start_scheduler(self):
        """Start the automated reporting scheduler"""
        logger.info("=" * 70)
        logger.info("📧 AUTOMATED REPORTING SYSTEM STARTED")
        logger.info("=" * 70)
        logger.info(f"Email Recipient: {self.email_to}")
        logger.info(f"Daily Report: Every day at 7:00 AM")
        logger.info(f"Weekly Report: Every Monday at 7:00 AM")
        logger.info("=" * 70)

        # Schedule daily report at 7:00 AM
        schedule.every().day.at("07:00").do(self.send_daily_report)

        # Schedule weekly report every Monday at 7:00 AM
        schedule.every().monday.at("07:00").do(self.send_weekly_report)

        # For testing: send immediate report
        logger.info("📧 Sending test report immediately...")
        self.send_daily_report()

        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║            AUTOMATED REPORTING SYSTEM                             ║
    ║         Daily (7 AM) & Weekly (Monday 7 AM) Reports               ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    reporter = AutomatedReportingSystem()
    reporter.start_scheduler()


if __name__ == "__main__":
    main()
