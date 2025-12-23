#!/usr/bin/env python3
"""
Email Automation Runner
Scheduled execution to process emails and automate task/reminder creation
Runs every hour to process new unread emails
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

# Import email extractor
from email_data_extractor import EmailDataExtractor, TaskAutomation


class EmailAutomationRunner:
    """Automated email processing and task creation"""

    def __init__(self):
        self.extractor = EmailDataExtractor()
        self.automation = TaskAutomation()
        self.agent_webhook = os.getenv('AGENT_5_WEBHOOK_URL')
        self.log_dir = "/home/user/Private-Claude/data/email_tasks/logs"
        os.makedirs(self.log_dir, exist_ok=True)

    def process_unread_emails(self, limit: int = 10) -> Dict[str, Any]:
        """Process unread emails and extract data"""
        print(f"\n{'='*70}")
        print(f"EMAIL AUTOMATION RUNNER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        start_time = datetime.now()

        # Scan inbox for unread emails
        print("📧 Scanning for unread emails...")
        emails = self.extractor.scan_inbox(limit=limit)

        if not emails:
            print("✅ No unread emails found")
            return {
                'status': 'success',
                'emails_processed': 0,
                'tasks_created': 0,
                'reminders_created': 0,
                'documents_identified': 0,
                'timestamp': datetime.now().isoformat()
            }

        print(f"📬 Found {len(emails)} unread email(s)\n")

        # Process each email
        total_tasks = 0
        total_reminders = 0
        total_docs = 0

        for idx, email_data in enumerate(emails, 1):
            print(f"[{idx}/{len(emails)}] Processing: {email_data['subject']}")

            # Extract and create tasks
            if email_data['tasks']:
                for task in email_data['tasks']:
                    success = self.automation.create_google_task(task)
                    total_tasks += 1
                print(f"   ✅ {len(email_data['tasks'])} task(s) extracted")

            # Extract and create reminders
            if email_data['reminders']:
                for reminder in email_data['reminders']:
                    success = self.automation.create_reminder(reminder)
                    total_reminders += 1
                print(f"   ⏰ {len(email_data['reminders'])} reminder(s) extracted")

            # Track documents
            if email_data['documents_needed']:
                total_docs += len(email_data['documents_needed'])
                self.automation.save_document_request(
                    email_data['documents_needed'],
                    email_data['subject']
                )

            # Save processed email
            self.automation.save_processed_email(email_data)

            # Send to Agent 5.0
            if self.agent_webhook:
                self.send_to_agent(email_data)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Summary
        print(f"\n{'='*70}")
        print("PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"📧 Emails processed: {len(emails)}")
        print(f"✅ Tasks created: {total_tasks}")
        print(f"⏰ Reminders created: {total_reminders}")
        print(f"📄 Documents identified: {total_docs}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"{'='*70}\n")

        # Return summary
        return {
            'status': 'success',
            'emails_processed': len(emails),
            'tasks_created': total_tasks,
            'reminders_created': total_reminders,
            'documents_identified': total_docs,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }

    def send_to_agent(self, email_data: Dict[str, Any]):
        """Send extracted data to Agent 5.0 webhook"""
        try:
            payload = {
                'event': 'email_processed',
                'email': {
                    'subject': email_data['subject'],
                    'from': email_data['from'],
                    'date': email_data['date']
                },
                'extracted': {
                    'tasks_count': len(email_data['tasks']),
                    'reminders_count': len(email_data['reminders']),
                    'documents_count': len(email_data['documents_needed']),
                    'deadlines_count': len(email_data['deadlines'])
                },
                'timestamp': datetime.utcnow().isoformat()
            }

            response = requests.post(
                self.agent_webhook,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print(f"   🤖 Sent to Agent 5.0")
            else:
                print(f"   ⚠️  Agent 5.0 webhook failed: {response.status_code}")

        except Exception as e:
            print(f"   ⚠️  Agent 5.0 webhook error: {e}")

    def log_run(self, summary: Dict[str, Any]):
        """Log automation run to file"""
        log_file = f"{self.log_dir}/automation_runs.json"

        runs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                runs = json.load(f)

        runs.append(summary)

        # Keep only last 1000 runs
        if len(runs) > 1000:
            runs = runs[-1000:]

        with open(log_file, 'w') as f:
            json.dump(runs, f, indent=2)

    def run_once(self, limit: int = 10):
        """Run automation once"""
        try:
            summary = self.process_unread_emails(limit=limit)
            self.log_run(summary)
            return summary
        except Exception as e:
            error_summary = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.log_run(error_summary)
            print(f"\n❌ Error: {e}\n")
            return error_summary

    def run_continuous(self, interval_minutes: int = 60, limit: int = 10):
        """Run automation continuously on schedule"""
        print(f"🔄 Starting continuous email automation (every {interval_minutes} minutes)")
        print(f"📧 Processing up to {limit} emails per run")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        while True:
            try:
                summary = self.process_unread_emails(limit=limit)
                self.log_run(summary)

                # Wait for next run
                next_run = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"⏱️  Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"💤 Sleeping for {interval_minutes} minutes...\n")

                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n\n🛑 Automation stopped by user")
                break
            except Exception as e:
                error_summary = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.log_run(error_summary)
                print(f"\n❌ Error: {e}")
                print(f"⏱️  Retrying in {interval_minutes} minutes...\n")
                time.sleep(interval_minutes * 60)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Email Automation Runner')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=60, help='Minutes between runs (default: 60)')
    parser.add_argument('--limit', type=int, default=10, help='Max emails to process per run (default: 10)')

    args = parser.parse_args()

    runner = EmailAutomationRunner()

    if args.continuous:
        runner.run_continuous(interval_minutes=args.interval, limit=args.limit)
    else:
        # Default: run once
        summary = runner.run_once(limit=args.limit)

        # Exit with appropriate code
        if summary['status'] == 'success':
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
