#!/usr/bin/env python3
"""
Gmail Automation for Legal Case Management
Handles probate case correspondence, document extraction, and automated responses
"""

import os
import base64
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]


class LegalGmailAutomation:
    """Automated Gmail management for legal cases"""

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Gmail automation

        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to save/load token pickle
        """
        self.base_dir = Path(__file__).parent.parent
        self.creds_path = credentials_path or self.base_dir / 'config' / 'gmail_credentials.json'
        self.token_path = token_path or self.base_dir / 'config' / 'gmail_token.pickle'

        self.service = None
        self.user_id = 'me'

        # Case-specific configuration
        self.probate_case = {
            'case_number': '1241511',
            'court': 'Harris County - County Civil Court at Law No. 2',
            'plaintiff': 'NEW FOREST HOUSTON 2020 LLC',
            'defendant': 'THURMAN ROBINSON, ET AL.',
            'status': 'DISMISSED',
            'contact_email': 'terobinsonwy@gmail.com'
        }

    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.creds_path.exists():
                    print("❌ Gmail credentials not found!")
                    print(f"   Download from: https://console.cloud.google.com/apis/credentials")
                    print(f"   Save to: {self.creds_path}")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.creds_path), SCOPES
                )
                creds = flow.run_local_server(port=8080)

            # Save token for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API authenticated successfully")
            return True
        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
            return False

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search emails using Gmail query syntax

        Args:
            query: Gmail search query (e.g., "from:court subject:case")
            max_results: Maximum number of results

        Returns:
            List of email message dictionaries
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return []

        try:
            results = self.service.users().messages().list(
                userId=self.user_id,
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                print(f"No emails found for query: {query}")
                return []

            email_list = []
            for msg in messages:
                email = self.get_email_details(msg['id'])
                if email:
                    email_list.append(email)

            return email_list

        except HttpError as error:
            print(f"❌ Error searching emails: {error}")
            return []

    def get_email_details(self, message_id: str) -> Dict[str, Any]:
        """Get full email details including headers and body"""
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])

            # Extract common headers
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': self._get_header(headers, 'Subject'),
                'from': self._get_header(headers, 'From'),
                'to': self._get_header(headers, 'To'),
                'date': self._get_header(headers, 'Date'),
                'snippet': message.get('snippet', ''),
                'body': self._get_email_body(message['payload'])
            }

            return email_data

        except HttpError as error:
            print(f"❌ Error getting email {message_id}: {error}")
            return {}

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract specific header value"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''

    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')

        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')

        return ''

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: List[str] = None,
        cc: str = None,
        bcc: str = None
    ) -> bool:
        """
        Send email with optional attachments

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body (plain text or HTML)
            attachments: List of file paths to attach
            cc: CC recipients
            bcc: BCC recipients

        Returns:
            True if sent successfully
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return False

        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc

            # Add body
            message.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=Path(file_path).name)
                            part['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
                            message.attach(part)

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            send_message = self.service.users().messages().send(
                userId=self.user_id,
                body={'raw': raw_message}
            ).execute()

            print(f"✅ Email sent successfully! Message ID: {send_message['id']}")
            return True

        except HttpError as error:
            print(f"❌ Error sending email: {error}")
            return False

    def send_probate_dismissal_notice(self, recipients: List[str]) -> bool:
        """
        Send automated dismissal notice for Case 1241511

        Args:
            recipients: List of email addresses to notify

        Returns:
            True if all emails sent successfully
        """
        subject = f"Case No. {self.probate_case['case_number']} - ORDER OF DISMISSAL"

        body = f"""Dear Stakeholder,

This letter confirms that Case No. {self.probate_case['case_number']} has been DISMISSED FOR NONSUIT by ORDER dated February 24, 2025.

CASE DETAILS:
- Case Number: {self.probate_case['case_number']}
- Court: {self.probate_case['court']}
- Plaintiff: {self.probate_case['plaintiff']}
- Defendant: {self.probate_case['defendant']}
- Status: {self.probate_case['status']}

The Honorable Jermaine Thomas, Judge Presiding, ordered:
- Case dismissed without prejudice
- Costs assessed against plaintiff
- Prior interlocutory judgments made final

No further action is required at this time. If you have any questions, please contact us at {self.probate_case['contact_email']}.

Sincerely,
Legal Department
Apps Holdings WY Inc

---
This is an automated notification. Court documents are attached for your records.
"""

        # Find dismissal order PDF
        dismissal_pdf = self.base_dir / 'legal-docs' / 'case_1241511_dismissal_order.pdf'
        attachments = [str(dismissal_pdf)] if dismissal_pdf.exists() else []

        success_count = 0
        for recipient in recipients:
            if self.send_email(recipient, subject, body, attachments):
                success_count += 1

        print(f"\n{'='*60}")
        print(f"Dismissal Notices Sent: {success_count}/{len(recipients)}")
        print(f"{'='*60}\n")

        return success_count == len(recipients)

    def monitor_legal_inbox(self, keywords: List[str] = None) -> List[Dict]:
        """
        Monitor inbox for legal correspondence

        Args:
            keywords: List of keywords to filter (e.g., ['case', 'court', 'filing'])

        Returns:
            List of matching emails
        """
        if keywords is None:
            keywords = ['case', 'court', 'filing', 'probate', 'dismissal', self.probate_case['case_number']]

        # Build query
        query_parts = [f'subject:{kw}' for kw in keywords]
        query = ' OR '.join(query_parts) + ' is:unread'

        print(f"🔍 Monitoring inbox with query: {query}")

        emails = self.search_emails(query, max_results=50)

        print(f"Found {len(emails)} unread legal emails")

        return emails

    def auto_label_case_emails(self, case_number: str, label_name: str = None) -> int:
        """
        Automatically label emails related to a case

        Args:
            case_number: Case number to search for
            label_name: Gmail label to apply (creates if doesn't exist)

        Returns:
            Number of emails labeled
        """
        if label_name is None:
            label_name = f"Case-{case_number}"

        # Create label if doesn't exist
        label_id = self._get_or_create_label(label_name)
        if not label_id:
            return 0

        # Search for case emails
        emails = self.search_emails(f'subject:{case_number}', max_results=100)

        labeled_count = 0
        for email in emails:
            try:
                self.service.users().messages().modify(
                    userId=self.user_id,
                    id=email['id'],
                    body={'addLabelIds': [label_id]}
                ).execute()
                labeled_count += 1
            except HttpError as error:
                print(f"❌ Error labeling {email['id']}: {error}")

        print(f"✅ Labeled {labeled_count} emails with '{label_name}'")
        return labeled_count

    def _get_or_create_label(self, label_name: str) -> str:
        """Get or create Gmail label"""
        try:
            # List existing labels
            results = self.service.users().labels().list(userId=self.user_id).execute()
            labels = results.get('labels', [])

            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']

            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }

            created_label = self.service.users().labels().create(
                userId=self.user_id,
                body=label_object
            ).execute()

            print(f"✅ Created label: {label_name}")
            return created_label['id']

        except HttpError as error:
            print(f"❌ Error with label: {error}")
            return None


def main():
    """Main execution for testing"""
    print("="*70)
    print("LEGAL GMAIL AUTOMATION - PROBATE CASE MANAGEMENT")
    print("="*70)
    print()

    # Initialize
    gmail = LegalGmailAutomation()

    # Authenticate
    if not gmail.authenticate():
        print("❌ Authentication failed. Please set up Gmail API credentials.")
        print("   1. Go to: https://console.cloud.google.com/apis/credentials")
        print("   2. Create OAuth 2.0 Client ID")
        print(f"   3. Save credentials to: {gmail.creds_path}")
        return

    # Test: Search for case emails
    print("\n--- Searching for Case 1241511 emails ---")
    case_emails = gmail.search_emails(f"subject:{gmail.probate_case['case_number']}", max_results=5)
    print(f"Found {len(case_emails)} emails related to the case")

    # Test: Monitor legal inbox
    print("\n--- Monitoring legal inbox ---")
    legal_emails = gmail.monitor_legal_inbox()

    # Test: Auto-label case emails
    print("\n--- Auto-labeling case emails ---")
    gmail.auto_label_case_emails(gmail.probate_case['case_number'])

    # Test: Send dismissal notice (COMMENTED OUT - uncomment when ready)
    # print("\n--- Sending dismissal notices ---")
    # recipients = ['terobinsonwy@gmail.com']  # Replace with actual recipients
    # gmail.send_probate_dismissal_notice(recipients)

    print("\n" + "="*70)
    print("✅ Gmail automation test complete!")
    print("="*70)


if __name__ == '__main__':
    main()
