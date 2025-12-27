#!/usr/bin/env python3
"""
GitHub Copilot Usage Tracker

Tracks GitHub Copilot suggestion acceptance rate, calculates usage percentage,
generates weekly reports, and sends email notifications when usage drops below 90%.

Author: AgentX5
Date: 2024-12-27
Target: Increase Copilot usage from 2.3% to 95%
"""

import os
import json
import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import requests


@dataclass
class CopilotMetrics:
    """Data class for Copilot usage metrics"""
    date: str
    suggestions_shown: int
    suggestions_accepted: int
    suggestions_rejected: int
    acceptance_rate: float
    lines_generated: int
    files_modified: int
    usage_percentage: float
    week_number: int
    target_percentage: float


@dataclass
class WeeklyGoal:
    """Data class for weekly Copilot goals"""
    week_number: int
    target_percentage: float
    tasks_count: int
    lines_target: int
    focus_area: str


class CopilotUsageTracker:
    """
    Main class for tracking GitHub Copilot usage and generating reports.
    """

    def __init__(self, db_path: str = "copilot_usage.db"):
        """
        Initialize the tracker with database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
        self.weekly_goals = self._load_weekly_goals()

    def initialize_database(self) -> None:
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create metrics table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS copilot_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                suggestions_shown INTEGER DEFAULT 0,
                suggestions_accepted INTEGER DEFAULT 0,
                suggestions_rejected INTEGER DEFAULT 0,
                acceptance_rate REAL DEFAULT 0.0,
                lines_generated INTEGER DEFAULT 0,
                files_modified INTEGER DEFAULT 0,
                usage_percentage REAL DEFAULT 0.0,
                week_number INTEGER DEFAULT 0,
                target_percentage REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create weekly reports table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                week_start_date TEXT NOT NULL,
                week_end_date TEXT NOT NULL,
                total_suggestions INTEGER DEFAULT 0,
                total_accepted INTEGER DEFAULT 0,
                avg_acceptance_rate REAL DEFAULT 0.0,
                total_lines_generated INTEGER DEFAULT 0,
                total_files_modified INTEGER DEFAULT 0,
                avg_usage_percentage REAL DEFAULT 0.0,
                target_met BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create email notifications log
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sent_date TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                usage_percentage REAL DEFAULT 0.0,
                sent_successfully BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def _load_weekly_goals(self) -> Dict[int, WeeklyGoal]:
        """
        Load weekly goals from the 2-month plan.

        Returns:
            Dictionary mapping week number to WeeklyGoal
        """
        goals = {
            1: WeeklyGoal(1, 20.0, 15, 2000, "Trading System Completion"),
            2: WeeklyGoal(2, 35.0, 20, 3500, "Legal Automation + Tests"),
            3: WeeklyGoal(3, 50.0, 25, 4000, "API Expansion + Frontend"),
            4: WeeklyGoal(4, 65.0, 25, 4500, "Credit Repair + Tax Filing"),
            5: WeeklyGoal(5, 75.0, 20, 3500, "Mobile App Development"),
            6: WeeklyGoal(6, 85.0, 20, 3500, "AI Orchestration + ML Models"),
            7: WeeklyGoal(7, 92.0, 15, 2500, "Integration Testing"),
            8: WeeklyGoal(8, 95.0, 10, 1500, "Performance Optimization"),
        }
        return goals

    def get_current_week_number(self) -> int:
        """
        Calculate current week number based on project start date.

        Returns:
            Current week number (1-8)
        """
        # Project starts Week of December 23, 2024
        start_date = datetime(2024, 12, 23)
        current_date = datetime.now()
        weeks_elapsed = (current_date - start_date).days // 7
        return min(max(weeks_elapsed + 1, 1), 8)

    def get_current_target(self) -> Tuple[float, str]:
        """
        Get current week's usage target and focus area.

        Returns:
            Tuple of (target_percentage, focus_area)
        """
        week = self.get_current_week_number()
        goal = self.weekly_goals.get(week, WeeklyGoal(8, 95.0, 10, 1500, "Maintenance"))
        return goal.target_percentage, goal.focus_area

    def fetch_copilot_stats_from_github(self) -> Optional[Dict]:
        """
        Fetch Copilot usage statistics from GitHub API.

        Note: This requires GitHub Enterprise or special API access.
        For now, this is a placeholder that returns mock data.

        Returns:
            Dictionary with Copilot statistics
        """
        # In production, this would use GitHub API:
        # GET /enterprises/{enterprise}/copilot/usage
        # Requires authentication and appropriate permissions

        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("⚠️  No GITHUB_TOKEN found. Using manual tracking.")
            return None

        # Placeholder for GitHub API integration
        # TODO: Implement actual GitHub API call when available
        return None

    def calculate_usage_from_git_stats(self) -> Dict:
        """
        Calculate Copilot usage from git commit statistics.

        Returns:
            Dictionary with calculated metrics
        """
        try:
            # Get commits from last 7 days
            result = subprocess.run(
                ['git', 'log', '--since=7.days.ago', '--pretty=format:%H', '--numstat'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            if result.returncode != 0:
                print(f"⚠️  Git command failed: {result.stderr}")
                return self._get_default_metrics()

            # Parse git output
            lines_added = 0
            files_modified = set()

            for line in result.stdout.split('\n'):
                parts = line.split('\t')
                if len(parts) == 3:
                    added, deleted, filename = parts
                    if added.isdigit():
                        lines_added += int(added)
                        files_modified.add(filename)

            # Estimate Copilot contribution
            # Assuming Copilot-generated commits have specific patterns
            copilot_commits = subprocess.run(
                ['git', 'log', '--since=7.days.ago', '--grep=Copilot', '--oneline'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            copilot_commit_count = len(copilot_commits.stdout.split('\n')) if copilot_commits.returncode == 0 else 0

            return {
                'lines_generated': lines_added,
                'files_modified': len(files_modified),
                'copilot_commits': copilot_commit_count,
                'total_commits': len(result.stdout.split('\n')) // 2 if result.stdout else 0
            }

        except Exception as e:
            print(f"❌ Error calculating git stats: {e}")
            return self._get_default_metrics()

    def _get_default_metrics(self) -> Dict:
        """Get default metrics when git stats unavailable"""
        return {
            'lines_generated': 0,
            'files_modified': 0,
            'copilot_commits': 0,
            'total_commits': 0
        }

    def record_daily_metrics(
        self,
        suggestions_shown: int,
        suggestions_accepted: int,
        suggestions_rejected: int,
        lines_generated: Optional[int] = None,
        files_modified: Optional[int] = None
    ) -> CopilotMetrics:
        """
        Record daily Copilot usage metrics.

        Args:
            suggestions_shown: Number of suggestions shown
            suggestions_accepted: Number of suggestions accepted
            suggestions_rejected: Number of suggestions rejected
            lines_generated: Lines of code generated (optional)
            files_modified: Number of files modified (optional)

        Returns:
            CopilotMetrics object with calculated values
        """
        today = datetime.now().strftime('%Y-%m-%d')
        week_number = self.get_current_week_number()
        target_percentage, _ = self.get_current_target()

        # Calculate acceptance rate
        acceptance_rate = (
            (suggestions_accepted / suggestions_shown * 100)
            if suggestions_shown > 0 else 0.0
        )

        # Get git stats if not provided
        if lines_generated is None or files_modified is None:
            git_stats = self.calculate_usage_from_git_stats()
            lines_generated = git_stats['lines_generated']
            files_modified = git_stats['files_modified']

        # Calculate usage percentage (acceptance rate is a proxy)
        usage_percentage = acceptance_rate

        metrics = CopilotMetrics(
            date=today,
            suggestions_shown=suggestions_shown,
            suggestions_accepted=suggestions_accepted,
            suggestions_rejected=suggestions_rejected,
            acceptance_rate=acceptance_rate,
            lines_generated=lines_generated,
            files_modified=files_modified,
            usage_percentage=usage_percentage,
            week_number=week_number,
            target_percentage=target_percentage
        )

        # Insert into database
        self.cursor.execute("""
            INSERT INTO copilot_metrics (
                date, suggestions_shown, suggestions_accepted, suggestions_rejected,
                acceptance_rate, lines_generated, files_modified, usage_percentage,
                week_number, target_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.date, metrics.suggestions_shown, metrics.suggestions_accepted,
            metrics.suggestions_rejected, metrics.acceptance_rate, metrics.lines_generated,
            metrics.files_modified, metrics.usage_percentage, metrics.week_number,
            metrics.target_percentage
        ))
        self.conn.commit()

        return metrics

    def generate_weekly_report(self, week_number: Optional[int] = None) -> Dict:
        """
        Generate weekly usage report.

        Args:
            week_number: Week number to generate report for (default: current week)

        Returns:
            Dictionary with weekly statistics
        """
        if week_number is None:
            week_number = self.get_current_week_number()

        # Get all metrics for the week
        self.cursor.execute("""
            SELECT
                SUM(suggestions_shown) as total_suggestions,
                SUM(suggestions_accepted) as total_accepted,
                AVG(acceptance_rate) as avg_acceptance_rate,
                SUM(lines_generated) as total_lines,
                SUM(files_modified) as total_files,
                AVG(usage_percentage) as avg_usage_percentage,
                MIN(date) as week_start,
                MAX(date) as week_end
            FROM copilot_metrics
            WHERE week_number = ?
        """, (week_number,))

        result = self.cursor.fetchone()

        if result and result[0]:
            total_suggestions, total_accepted, avg_acceptance_rate, total_lines, \
                total_files, avg_usage_percentage, week_start, week_end = result

            goal = self.weekly_goals.get(week_number)
            target_met = avg_usage_percentage >= goal.target_percentage if goal else False

            report = {
                'week_number': week_number,
                'week_start': week_start,
                'week_end': week_end,
                'total_suggestions': total_suggestions or 0,
                'total_accepted': total_accepted or 0,
                'avg_acceptance_rate': avg_acceptance_rate or 0.0,
                'total_lines_generated': total_lines or 0,
                'total_files_modified': total_files or 0,
                'avg_usage_percentage': avg_usage_percentage or 0.0,
                'target_percentage': goal.target_percentage if goal else 95.0,
                'target_met': target_met,
                'focus_area': goal.focus_area if goal else 'General Development'
            }

            # Save to database
            self.cursor.execute("""
                INSERT INTO weekly_reports (
                    week_number, week_start_date, week_end_date, total_suggestions,
                    total_accepted, avg_acceptance_rate, total_lines_generated,
                    total_files_modified, avg_usage_percentage, target_met
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                week_number, week_start, week_end, report['total_suggestions'],
                report['total_accepted'], report['avg_acceptance_rate'],
                report['total_lines_generated'], report['total_files_modified'],
                report['avg_usage_percentage'], target_met
            ))
            self.conn.commit()

            return report
        else:
            return {
                'week_number': week_number,
                'error': 'No data available for this week'
            }

    def send_email_notification(
        self,
        recipient: str,
        current_usage: float,
        target_usage: float,
        subject: Optional[str] = None
    ) -> bool:
        """
        Send email notification when usage drops below threshold.

        Args:
            recipient: Email address to send to
            current_usage: Current usage percentage
            target_usage: Target usage percentage
            subject: Email subject (optional)

        Returns:
            True if email sent successfully
        """
        if subject is None:
            subject = f"⚠️ GitHub Copilot Usage Alert: {current_usage:.1f}% (Target: {target_usage:.1f}%)"

        # Email configuration (use environment variables for security)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')

        if not smtp_username or not smtp_password:
            print("⚠️  SMTP credentials not configured. Skipping email notification.")
            return False

        # Create email content
        week_number = self.get_current_week_number()
        _, focus_area = self.get_current_target()

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0366d6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f6f8fa; }}
                .metrics {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #0366d6; }}
                .warning {{ background-color: #fff3cd; border-left-color: #ffc107; }}
                .success {{ background-color: #d4edda; border-left-color: #28a745; }}
                .footer {{ text-align: center; padding: 20px; color: #586069; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GitHub Copilot Usage Report</h1>
                </div>
                <div class="content">
                    <div class="metrics {'warning' if current_usage < 90 else 'success'}">
                        <h2>Current Usage: {current_usage:.1f}%</h2>
                        <p><strong>Target:</strong> {target_usage:.1f}%</p>
                        <p><strong>Week:</strong> {week_number} - {focus_area}</p>
                        <p><strong>Status:</strong> {'⚠️ BELOW TARGET' if current_usage < target_usage else '✅ MEETING TARGET'}</p>
                    </div>

                    <h3>Action Items:</h3>
                    <ul>
                        <li>Open VS Code with Copilot enabled</li>
                        <li>Review tasks in .github/copilot-tasks.md</li>
                        <li>Accept 50+ Copilot suggestions today</li>
                        <li>Write clear TODO comments for Copilot</li>
                        <li>Let Copilot write your tests</li>
                    </ul>

                    <h3>Tips to Increase Usage:</h3>
                    <ul>
                        <li>Press Tab to accept suggestions</li>
                        <li>Use Alt+] to cycle through alternatives</li>
                        <li>Write descriptive function names</li>
                        <li>Add TODO comments before writing code</li>
                        <li>Use Copilot Chat for complex logic</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Check your usage: <a href="https://github.com/settings/copilot">GitHub Copilot Settings</a></p>
                    <p>Generated by Copilot Usage Tracker</p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_username
            msg['To'] = recipient
            msg['Subject'] = subject

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            # Log notification
            today = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute("""
                INSERT INTO email_notifications (sent_date, recipient, subject, usage_percentage, sent_successfully)
                VALUES (?, ?, ?, ?, 1)
            """, (today, recipient, subject, current_usage))
            self.conn.commit()

            print(f"✅ Email notification sent to {recipient}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")

            # Log failed notification
            today = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute("""
                INSERT INTO email_notifications (sent_date, recipient, subject, usage_percentage, sent_successfully)
                VALUES (?, ?, ?, ?, 0)
            """, (today, recipient, subject, current_usage))
            self.conn.commit()

            return False

    def print_usage_summary(self) -> None:
        """Print current Copilot usage summary to console"""
        week_number = self.get_current_week_number()
        target_percentage, focus_area = self.get_current_target()

        # Get latest metrics
        self.cursor.execute("""
            SELECT * FROM copilot_metrics
            ORDER BY date DESC
            LIMIT 1
        """)

        result = self.cursor.fetchone()

        print("\n" + "="*80)
        print("📊 GITHUB COPILOT USAGE SUMMARY")
        print("="*80)
        print(f"\n📅 Week {week_number}: {focus_area}")
        print(f"🎯 Target: {target_percentage}%")
        print(f"💼 Investment: $39/month")

        if result:
            metrics = result[8]  # usage_percentage column
            print(f"📈 Current Usage: {metrics:.1f}%")

            if metrics >= target_percentage:
                print("✅ MEETING TARGET!")
            elif metrics >= 90:
                print("⚠️  Close to target, keep pushing!")
            else:
                print("❌ BELOW TARGET - ACTION REQUIRED")

            print(f"\n📊 Last 7 Days Statistics:")
            print(f"  • Lines Generated: {result[6]}")
            print(f"  • Files Modified: {result[7]}")
            print(f"  • Suggestions Accepted: {result[3]}")
            print(f"  • Acceptance Rate: {result[5]:.1f}%")
        else:
            print("⚠️  No usage data available yet")

        print("\n" + "="*80 + "\n")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main function to run the tracker"""
    tracker = CopilotUsageTracker()

    try:
        # Print current usage summary
        tracker.print_usage_summary()

        # Check if we should send email notification
        week_number = tracker.get_current_week_number()
        target_percentage, _ = tracker.get_current_target()

        # Get latest usage
        tracker.cursor.execute("""
            SELECT usage_percentage FROM copilot_metrics
            ORDER BY date DESC
            LIMIT 1
        """)

        result = tracker.cursor.fetchone()

        if result:
            current_usage = result[0]

            # Send email if usage < 90%
            if current_usage < 90:
                recipient_email = os.environ.get('NOTIFICATION_EMAIL', 'user@example.com')
                tracker.send_email_notification(
                    recipient=recipient_email,
                    current_usage=current_usage,
                    target_usage=target_percentage
                )

        # Generate weekly report (if it's the end of the week)
        if datetime.now().weekday() == 6:  # Sunday
            report = tracker.generate_weekly_report()
            print("\n📊 Weekly Report Generated:")
            print(json.dumps(report, indent=2))

    finally:
        tracker.close()


if __name__ == "__main__":
    main()
