#!/usr/bin/env python3
"""
Email Data Extraction and Automation System
Extracts tasks, reminders, deadlines, and documents from incoming emails
Integrates with Google Tasks, Calendar, and Agent 5.0
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

class EmailDataExtractor:
    """Extract actionable data from emails"""

    def __init__(self):
        self.email_address = os.getenv('GOOGLE_EMAIL', 'terobinsonwy@gmail.com')
        self.app_password = os.getenv('GOOGLE_APP_PASSWORD')

    def connect_to_gmail(self):
        """Connect to Gmail via IMAP"""
        try:
            imap = imaplib.IMAP4_SSL('imap.gmail.com')
            imap.login(self.email_address, self.app_password)
            return imap
        except Exception as e:
            print(f"Gmail connection error: {e}")
            return None

    def extract_tasks(self, email_body: str) -> List[Dict[str, Any]]:
        """Extract to-do items from email"""
        tasks = []

        # Task patterns
        patterns = [
            r'(?:TODO|To do|Task):\s*(.+)',
            r'(?:Please|Need to|Must)\s+(.+?)(?:\.|$)',
            r'[\-\*]\s*(.+?)(?:\n|$)',  # Bullet points
            r'(\d+[\.\)]\s+.+?)(?:\n|$)',  # Numbered lists
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, email_body, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_text = match.group(1).strip()
                if len(task_text) > 10:  # Filter out noise
                    tasks.append({
                        'title': task_text[:100],
                        'description': task_text,
                        'source': 'email',
                        'created_at': datetime.utcnow().isoformat()
                    })

        return tasks

    def extract_deadlines(self, email_body: str) -> List[Dict[str, Any]]:
        """Extract deadlines and due dates"""
        deadlines = []

        # Date patterns
        date_patterns = [
            r'(?:due|deadline|by|before)\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, email_body, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1)
                deadlines.append({
                    'date': date_str,
                    'context': email_body[max(0, match.start()-50):match.end()+50],
                    'extracted_at': datetime.utcnow().isoformat()
                })

        return deadlines

    def extract_documents_needed(self, email_body: str) -> List[str]:
        """Extract document requirements"""
        documents = []

        doc_patterns = [
            r'(?:need|require|send|attach|submit)\s+(?:the\s+)?(.+?(?:form|document|file|pdf|contract|agreement))',
            r'(?:Form\s+\d+[\w-]*)',
            r'(?:W-2|1099|1040|1023|990)',
        ]

        for pattern in doc_patterns:
            matches = re.finditer(pattern, email_body, re.IGNORECASE)
            for match in matches:
                doc = match.group(0).strip()
                if doc and doc not in documents:
                    documents.append(doc)

        return documents

    def extract_reminders(self, email_body: str) -> List[Dict[str, Any]]:
        """Extract reminder requests"""
        reminders = []

        reminder_patterns = [
            r'(?:remind me|reminder|don\'t forget)\s+(?:to\s+)?(.+?)(?:\.|$)',
            r'(?:follow up|check in)\s+(.+?)(?:\.|$)',
        ]

        for pattern in reminder_patterns:
            matches = re.finditer(pattern, email_body, re.IGNORECASE)
            for match in matches:
                reminder_text = match.group(1).strip()
                reminders.append({
                    'reminder': reminder_text,
                    'created_at': datetime.utcnow().isoformat()
                })

        return reminders

    def process_email(self, msg) -> Dict[str, Any]:
        """Process a single email and extract all data"""
        # Decode subject
        subject = decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Extract all data
        extracted_data = {
            'subject': subject,
            'from': msg['From'],
            'date': msg['Date'],
            'tasks': self.extract_tasks(body),
            'deadlines': self.extract_deadlines(body),
            'documents_needed': self.extract_documents_needed(body),
            'reminders': self.extract_reminders(body),
            'processed_at': datetime.utcnow().isoformat()
        }

        return extracted_data

    def scan_inbox(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Scan inbox for unread emails"""
        imap = self.connect_to_gmail()
        if not imap:
            return []

        try:
            imap.select('INBOX')
            _, messages = imap.search(None, 'UNSEEN')

            email_ids = messages[0].split()
            recent_emails = email_ids[-limit:] if len(email_ids) > limit else email_ids

            processed_emails = []
            for email_id in recent_emails:
                _, msg_data = imap.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)

                extracted = self.process_email(msg)
                processed_emails.append(extracted)

            imap.close()
            imap.logout()

            return processed_emails

        except Exception as e:
            print(f"Error scanning inbox: {e}")
            return []


class TaskAutomation:
    """Automate task creation and reminders"""

    def __init__(self):
        self.output_dir = "/home/user/Private-Claude/data/email_tasks"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_google_task(self, task: Dict[str, Any]) -> bool:
        """Create task in Google Tasks (via Zapier webhook)"""
        webhook_url = os.getenv('ZAPIER_TASK_WEBHOOK')
        if not webhook_url:
            # Save locally if no webhook
            self.save_task_locally(task)
            return False

        try:
            import requests
            response = requests.post(webhook_url, json=task, timeout=10)
            return response.status_code == 200
        except:
            self.save_task_locally(task)
            return False

    def save_task_locally(self, task: Dict[str, Any]):
        """Save task to local JSON file"""
        tasks_dir = f"{self.output_dir}/tasks"
        os.makedirs(tasks_dir, exist_ok=True)
        filename = f"{tasks_dir}/tasks_{datetime.now().strftime('%Y%m%d')}.json"

        tasks = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                tasks = json.load(f)

        task['saved_at'] = datetime.utcnow().isoformat()
        tasks.append(task)

        with open(filename, 'w') as f:
            json.dump(tasks, f, indent=2)

        print(f"   ✅ Task saved: {task.get('title', 'Untitled')[:50]}...")

    def create_reminder(self, reminder: Dict[str, Any]) -> bool:
        """Create reminder in Google Calendar"""
        webhook_url = os.getenv('ZAPIER_REMINDER_WEBHOOK')
        if not webhook_url:
            self.save_reminder_locally(reminder)
            return False

        try:
            import requests
            response = requests.post(webhook_url, json=reminder, timeout=10)
            return response.status_code == 200
        except:
            self.save_reminder_locally(reminder)
            return False

    def save_reminder_locally(self, reminder: Dict[str, Any]):
        """Save reminder to local JSON file"""
        reminders_dir = f"{self.output_dir}/reminders"
        os.makedirs(reminders_dir, exist_ok=True)
        filename = f"{reminders_dir}/reminders_{datetime.now().strftime('%Y%m%d')}.json"

        reminders = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                reminders = json.load(f)

        reminder['saved_at'] = datetime.utcnow().isoformat()
        reminders.append(reminder)

        with open(filename, 'w') as f:
            json.dump(reminders, f, indent=2)

        print(f"   ⏰ Reminder saved: {reminder.get('reminder', 'Untitled')[:50]}...")

    def generate_document_request(self, documents: List[str]) -> Dict[str, Any]:
        """Generate document generation request"""
        return {
            'event': 'document_generation_requested',
            'documents': documents,
            'requested_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }

    def save_document_request(self, documents: List[str], email_subject: str):
        """Save document request to local file"""
        docs_dir = f"{self.output_dir}/documents"
        os.makedirs(docs_dir, exist_ok=True)
        filename = f"{docs_dir}/document_requests_{datetime.now().strftime('%Y%m%d')}.json"

        requests = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                requests = json.load(f)

        doc_request = {
            'email_subject': email_subject,
            'documents': documents,
            'requested_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        requests.append(doc_request)

        with open(filename, 'w') as f:
            json.dump(requests, f, indent=2)

        print(f"   📄 Document request saved: {len(documents)} documents")

    def save_processed_email(self, email_data: Dict[str, Any]):
        """Save processed email metadata"""
        processed_dir = f"{self.output_dir}/processed_emails"
        os.makedirs(processed_dir, exist_ok=True)
        filename = f"{processed_dir}/processed_{datetime.now().strftime('%Y%m%d')}.json"

        emails = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                emails = json.load(f)

        emails.append(email_data)

        with open(filename, 'w') as f:
            json.dump(emails, f, indent=2)


def main():
    """Main execution"""
    print("="*60)
    print("EMAIL DATA EXTRACTION & AUTOMATION")
    print("="*60)

    # Extract from emails
    extractor = EmailDataExtractor()
    print("\n📧 Scanning inbox...")
    emails = extractor.scan_inbox(limit=20)

    print(f"Found {len(emails)} unread emails")

    # Process extracted data
    automation = TaskAutomation()

    total_tasks = 0
    total_reminders = 0
    total_docs = 0

    for email_data in emails:
        print(f"\n📨 Processing: {email_data['subject']}")

        # Create tasks
        for task in email_data['tasks']:
            automation.create_google_task(task)
            total_tasks += 1

        # Create reminders
        for reminder in email_data['reminders']:
            automation.create_reminder(reminder)
            total_reminders += 1

        # Track documents needed
        if email_data['documents_needed']:
            total_docs += len(email_data['documents_needed'])
            automation.save_document_request(email_data['documents_needed'], email_data['subject'])

        # Save processed email metadata
        automation.save_processed_email(email_data)

    # Summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"✅ Tasks created: {total_tasks}")
    print(f"⏰ Reminders set: {total_reminders}")
    print(f"📄 Documents identified: {total_docs}")
    print(f"📧 Emails processed: {len(emails)}")
    print("\nData saved to: /home/user/Private-Claude/data/email_tasks/")


if __name__ == '__main__':
    main()
