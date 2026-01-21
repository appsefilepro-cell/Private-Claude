#!/usr/bin/env python3
'''
EMAIL INDEX SYSTEM
==================
Indexes all emails including:
- Inbox disputes
- Sent emails (who you're engaging with)
- Email threads
- Attachments
'''

import json
import os
from pathlib import Path
from datetime import datetime

class EmailIndexer:
    def __init__(self):
        self.inbox_emails = []
        self.sent_emails = []
        self.dispute_emails = []
        self.engagement_map = {}

    def index_email(self, email_type: str, sender: str, recipient: str,
                    subject: str, date: str, body_preview: str = "",
                    attachments: list = None):
        '''Index an email'''

        email = {
            "id": len(self.inbox_emails) + len(self.sent_emails) + 1,
            "type": email_type,
            "from": sender,
            "to": recipient,
            "subject": subject,
            "date": date,
            "body_preview": body_preview[:200],
            "attachments": attachments or [],
            "indexed_at": datetime.now().isoformat()
        }

        if email_type == "inbox":
            self.inbox_emails.append(email)
        elif email_type == "sent":
            self.sent_emails.append(email)

            # Track engagement
            if recipient not in self.engagement_map:
                self.engagement_map[recipient] = []
            self.engagement_map[recipient].append(email)

        # Check if it's a dispute
        if any(word in subject.lower() for word in ["dispute", "complaint", "fraud", "unauthorized"]):
            self.dispute_emails.append(email)

        return email

    def generate_engagement_report(self):
        '''Report on who you're engaging with (from sent emails)'''

        print("\n📊 ENGAGEMENT REPORT (From Sent Emails):")
        print("=" * 60)

        for recipient, emails in sorted(self.engagement_map.items(),
                                       key=lambda x: len(x[1]),
                                       reverse=True):
            print(f"\n{recipient}: {len(emails)} emails sent")
            for email in emails[:3]:  # Show first 3
                print(f"  - {email['date']}: {email['subject'][:50]}")
            if len(emails) > 3:
                print(f"  ... and {len(emails) - 3} more")

    def export_for_lawsuit(self, output_file="email_evidence.json"):
        '''Export all emails for lawsuit evidence'''

        data = {
            "inbox_count": len(self.inbox_emails),
            "sent_count": len(self.sent_emails),
            "dispute_count": len(self.dispute_emails),
            "engagement_summary": {k: len(v) for k, v in self.engagement_map.items()},
            "all_emails": {
                "inbox": self.inbox_emails,
                "sent": self.sent_emails,
                "disputes": self.dispute_emails
            }
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ Email evidence exported: {output_file}")
        return data


# Example usage
if __name__ == "__main__":
    indexer = EmailIndexer()

    # Example: Index sent email (engagement)
    indexer.index_email(
        email_type="sent",
        sender="you@example.com",
        recipient="bank@example.com",
        subject="Dispute unauthorized charge",
        date="2025-01-15",
        body_preview="I am writing to dispute the unauthorized charge...",
        attachments=["receipt.pdf"]
    )

    # Example: Index inbox dispute
    indexer.index_email(
        email_type="inbox",
        sender="merchant@example.com",
        recipient="you@example.com",
        subject="RE: Dispute - Transaction declined",
        date="2025-01-16",
        body_preview="We received your dispute and are investigating..."
    )

    indexer.generate_engagement_report()
    indexer.export_for_lawsuit()

    print("\n✅ Email indexing system ready!")
    print("\n📝 NOTE: Connect to Gmail/Outlook API to auto-index all emails")
