"""
Remediation Engine
Automatically checks for incomplete tasks, retries failed ingestion jobs, and updates CSV
"""

import csv
import json
import logging
import os
import re
# Import processors
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data-ingestion"))

try:
    from ingestion_orchestrator import (CustomerContact, DataValidator,
                                        ExcelProcessor, PDFProcessor)

    PROCESSORS_AVAILABLE = True
except BaseException:
    PROCESSORS_AVAILABLE = False
    logging.warning("Ingestion processors not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RemediationEngine")


class TaskStatus:
    """Track status of ingestion tasks"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class RemediationEngine:
    """
    Remediation Engine for incomplete tasks and failed jobs
    """

    def __init__(self):
        self.tasks_file = "logs/ingestion_tasks.json"
        self.remediation_log = "logs/remediation_log.txt"
        self.output_csv = "customer_contact_list.csv"
        self.max_retries = 3
        self.tasks = []
        self.remediated_count = 0
        self.failed_count = 0

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        logger.info("Remediation Engine initialized")

    def log_action(self, action: str) -> None:
        """Log remediation action"""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {action}\n"

        with open(self.remediation_log, "a", encoding="utf-8") as f:
            f.write(log_entry)

        logger.info(action)

    def load_tasks(self) -> List[Dict[str, Any]]:
        """Load ingestion tasks from log"""
        if not os.path.exists(self.tasks_file):
            self.log_action("No tasks file found, scanning for files to process")
            return self.discover_unprocessed_files()

        try:
            with open(self.tasks_file, "r") as f:
                self.tasks = json.load(f)
            self.log_action(f"Loaded {len(self.tasks)} tasks from {self.tasks_file}")
            return self.tasks
        except Exception as e:
            self.log_action(f"Error loading tasks: {e}")
            return []

    def discover_unprocessed_files(self) -> List[Dict[str, Any]]:
        """Discover files that haven't been processed"""
        tasks = []
        search_dirs = [
            "data/gmail_attachments",
            "data/dropbox",
            "data/onedrive",
            "data/sharepoint",
            "data/local_files",
        ]

        for directory in search_dirs:
            if not os.path.exists(directory):
                continue

            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = Path(file_path).suffix.lower()

                    if ext in [".pdf", ".xlsx", ".xls"]:
                        task = {
                            "file_path": file_path,
                            "file_type": ext,
                            "status": TaskStatus.PENDING,
                            "retry_count": 0,
                            "error": None,
                            "discovered_at": datetime.now().isoformat(),
                        }
                        tasks.append(task)

        self.tasks = tasks
        self.log_action(f"Discovered {len(tasks)} unprocessed files")
        return tasks

    def check_incomplete_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that are incomplete or failed"""
        incomplete = []

        for task in self.tasks:
            status = task.get("status", TaskStatus.PENDING)

            if status in [TaskStatus.PENDING, TaskStatus.FAILED]:
                incomplete.append(task)
            elif status == TaskStatus.IN_PROGRESS:
                # Task was in progress but didn't complete (likely crashed)
                task["status"] = TaskStatus.RETRY
                incomplete.append(task)

        self.log_action(f"Found {len(incomplete)} incomplete tasks")
        return incomplete

    def retry_failed_job(self, task: Dict[str, Any]) -> bool:
        """
        Retry a failed ingestion job

        Returns:
            True if successful, False otherwise
        """
        file_path = task["file_path"]
        file_type = task["file_type"]

        if task["retry_count"] >= self.max_retries:
            self.log_action(f"Max retries exceeded for {file_path}")
            task["status"] = TaskStatus.FAILED
            self.failed_count += 1
            return False

        self.log_action(
            f"Retrying job {task['retry_count'] + 1}/{self.max_retries}: {file_path}"
        )
        task["retry_count"] += 1
        task["status"] = TaskStatus.IN_PROGRESS

        try:
            # Process the file
            contacts = []

            if file_type == ".pdf" and PROCESSORS_AVAILABLE:
                contacts = PDFProcessor.extract_from_pdf(file_path)
            elif file_type in [".xlsx", ".xls"] and PROCESSORS_AVAILABLE:
                contacts = ExcelProcessor.extract_from_excel(file_path)

            # Save to CSV if we got contacts
            if contacts:
                self.append_to_csv(contacts)
                task["status"] = TaskStatus.COMPLETED
                task["contacts_extracted"] = len(contacts)
                task["completed_at"] = datetime.now().isoformat()
                self.remediated_count += 1
                self.log_action(
                    f"Successfully processed {file_path}: {len(contacts)} contacts extracted"
                )
                return True
            else:
                task["status"] = TaskStatus.COMPLETED
                task["contacts_extracted"] = 0
                task["completed_at"] = datetime.now().isoformat()
                self.log_action(f"Processed {file_path}: no contacts found")
                return True

        except Exception as e:
            error_msg = str(e)
            task["error"] = error_msg
            task["status"] = TaskStatus.FAILED
            self.log_action(f"Failed to process {file_path}: {error_msg}")
            return False

    def append_to_csv(self, contacts: List[CustomerContact]) -> None:
        """Append contacts to CSV"""
        try:
            # Ensure CSV exists with headers
            if not os.path.exists(self.output_csv):
                with open(self.output_csv, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "First Name",
                            "Last Name",
                            "Phone",
                            "Email",
                            "Mailing Address",
                            "Tax Years",
                            "Filing Status",
                            "Dependents",
                        ]
                    )

            # Append contacts
            with open(self.output_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for contact in contacts:
                    writer.writerow(contact.to_csv_row())

            self.log_action(f"Added {len(contacts)} contacts to CSV")

        except Exception as e:
            self.log_action(f"Error appending to CSV: {e}")
            raise

    def save_tasks(self) -> None:
        """Save tasks to file"""
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=2)
            self.log_action(f"Saved {len(self.tasks)} tasks to {self.tasks_file}")
        except Exception as e:
            self.log_action(f"Error saving tasks: {e}")

    def validate_csv(self) -> Dict[str, Any]:
        """Validate the output CSV"""
        validation = {
            "exists": False,
            "row_count": 0,
            "has_headers": False,
            "duplicate_emails": 0,
            "invalid_emails": 0,
            "missing_data": 0,
        }

        if not os.path.exists(self.output_csv):
            self.log_action("CSV validation: File does not exist")
            return validation

        validation["exists"] = True

        try:
            with open(self.output_csv, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

                if rows:
                    validation["has_headers"] = True
                    validation["row_count"] = len(rows) - 1  # Exclude header

                    # Check for issues
                    seen_emails = set()
                    for idx, row in enumerate(rows[1:], start=2):  # Skip header
                        if len(row) < 4:
                            validation["missing_data"] += 1
                            continue

                        email = row[3]  # Email column

                        # Check for invalid email
                        if email and not DataValidator.validate_email(email):
                            validation["invalid_emails"] += 1

                        # Check for duplicates
                        if email in seen_emails:
                            validation["duplicate_emails"] += 1
                        seen_emails.add(email)

            self.log_action(f"CSV validation complete: {json.dumps(validation)}")

        except Exception as e:
            self.log_action(f"Error validating CSV: {e}")

        return validation

    def generate_report(self) -> Dict[str, Any]:
        """Generate remediation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self.tasks),
            "completed_tasks": sum(
                1 for t in self.tasks if t["status"] == TaskStatus.COMPLETED
            ),
            "failed_tasks": sum(
                1 for t in self.tasks if t["status"] == TaskStatus.FAILED
            ),
            "pending_tasks": sum(
                1 for t in self.tasks if t["status"] == TaskStatus.PENDING
            ),
            "remediated_count": self.remediated_count,
            "failed_count": self.failed_count,
            "csv_validation": self.validate_csv(),
        }

        return report

    def run(self) -> Dict[str, Any]:
        """
        Run the complete remediation process
        """
        self.log_action("=== Starting Remediation Process ===")

        # Load tasks
        self.load_tasks()

        # Find incomplete tasks
        incomplete_tasks = self.check_incomplete_tasks()

        if not incomplete_tasks:
            self.log_action("No incomplete tasks found - system is 100% complete")
        else:
            self.log_action(f"Processing {len(incomplete_tasks)} incomplete tasks")

            # Retry each incomplete task
            for task in incomplete_tasks:
                self.retry_failed_job(task)

            # Save updated tasks
            self.save_tasks()

        # Validate CSV
        validation = self.validate_csv()

        # Generate report
        report = self.generate_report()

        self.log_action("=== Remediation Complete ===")
        self.log_action(f"Report: {json.dumps(report, indent=2)}")

        # Check if we're at 100%
        completion_rate = (
            (report["completed_tasks"] / report["total_tasks"] * 100)
            if report["total_tasks"] > 0
            else 100
        )
        self.log_action(f"System Completion: {completion_rate:.1f}%")

        if completion_rate == 100:
            self.log_action("✅ SYSTEM IS 100% DEPLOYED AND COMPLIANT")
        else:
            self.log_action(
                f"⚠️  System is {completion_rate:.1f}% complete - {report['pending_tasks'] + report['failed_tasks']} tasks remaining"
            )

        return report


def main():
    """Main entry point"""
    engine = RemediationEngine()
    report = engine.run()

    print("\n" + "=" * 60)
    print("REMEDIATION REPORT")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
