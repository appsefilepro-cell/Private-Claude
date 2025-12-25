#!/usr/bin/env python3
"""
Microsoft 365 Migration Scheduler
Automated backup scheduling with incremental support

For research, development, and educational purposes only.
"""

import os
import sys
import json
import logging
import argparse
import schedule
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import subprocess
from dotenv import load_dotenv


class MigrationScheduler:
    """Scheduler for automated Microsoft 365 migrations"""

    def __init__(self, config_file: str = 'config.json'):
        """Initialize scheduler"""
        self.config_file = config_file
        self.config = self._load_config()
        self.schedule_config = self.config.get('scheduling', {})
        self.running = False
        self.pid_file = Path('/tmp/migration_scheduler.pid')
        self.log_file = Path('/home/user/Private-Claude/logs/system-integration/scheduler.log')

        # Setup logging
        self.logger = self._setup_logging()

        # Last run tracking
        self.state_file = Path('scheduler_state.json')
        self.state = self._load_state()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            print(f"Warning: Config file not found: {self.config_file}")
            return {}

        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger('MigrationScheduler')
        logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_run': None,
            'last_success': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0
        }

    def _save_state(self):
        """Save scheduler state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def _check_if_running(self) -> bool:
        """Check if scheduler is already running"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())

                # Check if process is running
                os.kill(pid, 0)
                return True
            except (OSError, ValueError):
                # Process not running, remove stale PID file
                self.pid_file.unlink()
                return False
        return False

    def _create_pid_file(self):
        """Create PID file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def _remove_pid_file(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def run_migration(self):
        """Execute migration"""
        self.logger.info("="*60)
        self.logger.info("SCHEDULED MIGRATION STARTING")
        self.logger.info(f"Time: {datetime.now().isoformat()}")
        self.logger.info("="*60)

        self.state['last_run'] = datetime.now().isoformat()
        self.state['total_runs'] += 1
        self._save_state()

        try:
            # Determine if incremental backup
            incremental = self.schedule_config.get('incremental_backup', True)

            # Build command
            cmd = [
                sys.executable,
                'enhanced_migration.py',
                '--config', self.config_file,
                '--batch'
            ]

            if incremental:
                cmd.append('--resume')

            # Run migration
            self.logger.info(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=3600 * 4  # 4 hour timeout
            )

            if result.returncode == 0:
                self.logger.info("✅ Migration completed successfully")
                self.state['last_success'] = datetime.now().isoformat()
                self.state['successful_runs'] += 1
                self._send_notification(
                    "Migration Successful",
                    f"Scheduled migration completed successfully at {datetime.now()}"
                )
            else:
                self.logger.error(f"❌ Migration failed with code {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
                self.state['failed_runs'] += 1
                self._send_notification(
                    "Migration Failed",
                    f"Scheduled migration failed at {datetime.now()}\nError: {result.stderr[:500]}"
                )

            # Log output
            self.logger.info(f"STDOUT: {result.stdout}")

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Migration timed out")
            self.state['failed_runs'] += 1
            self._send_notification(
                "Migration Timeout",
                f"Scheduled migration timed out at {datetime.now()}"
            )

        except Exception as e:
            self.logger.error(f"❌ Migration error: {e}")
            self.state['failed_runs'] += 1
            self._send_notification(
                "Migration Error",
                f"Scheduled migration error at {datetime.now()}\nError: {str(e)}"
            )

        finally:
            self._save_state()
            self.logger.info("="*60)
            self.logger.info("SCHEDULED MIGRATION COMPLETE")
            self.logger.info("="*60 + "\n")

    def _send_notification(self, subject: str, message: str):
        """Send notification"""
        notifications = self.config.get('notifications', {})

        # Email notification
        if notifications.get('enabled') and notifications.get('email', {}).get('enabled'):
            try:
                self._send_email_notification(subject, message)
            except Exception as e:
                self.logger.error(f"Failed to send email notification: {e}")

        # Webhook notification
        if notifications.get('webhook', {}).get('enabled'):
            try:
                self._send_webhook_notification(subject, message)
            except Exception as e:
                self.logger.error(f"Failed to send webhook notification: {e}")

    def _send_email_notification(self, subject: str, message: str):
        """Send email notification"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        email_config = self.config['notifications']['email']

        msg = MIMEMultipart()
        msg['From'] = email_config['smtp_user']
        msg['To'] = email_config['recipient']
        msg['Subject'] = f"Microsoft 365 Migration: {subject}"

        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            if email_config.get('use_tls', True):
                server.starttls()
            server.login(email_config['smtp_user'], email_config['smtp_password'])
            server.send_message(msg)

        self.logger.info("📧 Email notification sent")

    def _send_webhook_notification(self, subject: str, message: str):
        """Send webhook notification"""
        import requests

        webhook_config = self.config['notifications']['webhook']

        payload = {
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'scheduler_state': self.state
        }

        response = requests.request(
            method=webhook_config.get('method', 'POST'),
            url=webhook_config['url'],
            json=payload,
            headers=webhook_config.get('headers', {}),
            timeout=30
        )

        response.raise_for_status()
        self.logger.info("🔔 Webhook notification sent")

    def setup_schedule(self):
        """Setup scheduled jobs"""
        schedule_type = self.schedule_config.get('schedule_type', 'daily')
        schedule_time = self.schedule_config.get('schedule_time', '02:00')

        if schedule_type == 'daily':
            schedule.every().day.at(schedule_time).do(self.run_migration)
            self.logger.info(f"📅 Scheduled daily migration at {schedule_time}")

        elif schedule_type == 'weekly':
            days_of_week = self.schedule_config.get('days_of_week', [1])  # Monday by default
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

            for day_num in days_of_week:
                if 0 <= day_num < 7:
                    day_name = day_names[day_num]
                    getattr(schedule.every(), day_name).at(schedule_time).do(self.run_migration)
                    self.logger.info(f"📅 Scheduled migration on {day_name.capitalize()} at {schedule_time}")

        elif schedule_type == 'hourly':
            schedule.every().hour.do(self.run_migration)
            self.logger.info("📅 Scheduled hourly migration")

        elif schedule_type == 'interval':
            interval_hours = self.schedule_config.get('interval_hours', 6)
            schedule.every(interval_hours).hours.do(self.run_migration)
            self.logger.info(f"📅 Scheduled migration every {interval_hours} hours")

        else:
            self.logger.error(f"Unknown schedule type: {schedule_type}")
            return False

        return True

    def start(self):
        """Start the scheduler"""
        if not self.schedule_config.get('enabled', False):
            self.logger.error("Scheduling is not enabled in configuration")
            return

        if self._check_if_running():
            self.logger.error("Scheduler is already running")
            return

        self._create_pid_file()

        self.logger.info("="*60)
        self.logger.info("MIGRATION SCHEDULER STARTING")
        self.logger.info("="*60)
        self.logger.info(f"PID: {os.getpid()}")
        self.logger.info(f"Config: {self.config_file}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"State file: {self.state_file}")
        self.logger.info("="*60 + "\n")

        # Setup schedule
        if not self.setup_schedule():
            self._remove_pid_file()
            return

        self.running = True

        # Show next run time
        next_run = schedule.next_run()
        if next_run:
            self.logger.info(f"⏰ Next scheduled run: {next_run}")

        # Run immediately if requested
        if self.schedule_config.get('run_on_startup', False):
            self.logger.info("Running migration immediately (run_on_startup=true)")
            self.run_migration()

        # Main loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")

        finally:
            self.stop()

    def stop(self):
        """Stop the scheduler"""
        self.logger.info("Stopping scheduler...")
        self.running = False
        self._remove_pid_file()
        self.logger.info("Scheduler stopped")

    def status(self):
        """Show scheduler status"""
        print("\n" + "="*60)
        print("MIGRATION SCHEDULER STATUS")
        print("="*60)

        # Check if running
        if self._check_if_running():
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            print(f"✅ Status: RUNNING (PID: {pid})")
        else:
            print("❌ Status: STOPPED")

        # Show configuration
        print(f"\nConfiguration:")
        print(f"  Schedule Type: {self.schedule_config.get('schedule_type', 'N/A')}")
        print(f"  Schedule Time: {self.schedule_config.get('schedule_time', 'N/A')}")
        print(f"  Incremental: {self.schedule_config.get('incremental_backup', True)}")

        # Show statistics
        print(f"\nStatistics:")
        print(f"  Total Runs: {self.state['total_runs']}")
        print(f"  Successful: {self.state['successful_runs']}")
        print(f"  Failed: {self.state['failed_runs']}")

        if self.state['last_run']:
            print(f"  Last Run: {self.state['last_run']}")
        if self.state['last_success']:
            print(f"  Last Success: {self.state['last_success']}")

        # Next scheduled run
        if self._check_if_running():
            next_run = schedule.next_run()
            if next_run:
                print(f"\n⏰ Next Scheduled Run: {next_run}")

        print("="*60 + "\n")


def main():
    """Main execution"""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Microsoft 365 Migration Scheduler'
    )
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'status', 'run-now'],
        help='Action to perform'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (background process)'
    )

    args = parser.parse_args()

    scheduler = MigrationScheduler(config_file=args.config)

    if args.action == 'start':
        if args.daemon:
            # Fork to background
            if os.fork() > 0:
                print("✅ Scheduler started in background")
                sys.exit(0)
            os.setsid()
            if os.fork() > 0:
                sys.exit(0)

        scheduler.start()

    elif args.action == 'stop':
        if scheduler._check_if_running():
            with open(scheduler.pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print("✅ Scheduler stopped")
            except OSError as e:
                print(f"❌ Failed to stop scheduler: {e}")
        else:
            print("Scheduler is not running")

    elif args.action == 'status':
        scheduler.status()

    elif args.action == 'run-now':
        print("Running migration now...")
        scheduler.run_migration()
        print("✅ Migration complete")


if __name__ == "__main__":
    main()
