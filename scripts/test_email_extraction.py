#!/usr/bin/env python3
"""
Email Extraction System - Test and Demo
Simulates email processing without requiring actual Gmail credentials
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

# Import modules
sys.path.append(str(Path(__file__).parent))
from email_data_extractor import EmailDataExtractor, TaskAutomation


# Sample test emails
SAMPLE_EMAILS = [
    {
        "subject": "Q4 Financial Review - Action Items",
        "from": "cfo@company.com",
        "date": "Mon, 18 Dec 2024 09:30:00 -0700",
        "body": """Hi Team,

Following up on our Q4 financial review meeting. Here are the action items:

TODO: Review and approve the Q4 budget report by December 28
TODO: Update the financial forecast spreadsheet with revised projections
- Prepare presentation slides for the board meeting
- Schedule follow-up meeting with department heads

Please send me the following documents:
- Form 1023 for tax-exempt status application
- Updated W-2 forms for all employees
- Final audit report from external auditors

Deadline: All items must be completed by December 31, 2024.

Remind me to follow up with the auditing team next Friday.

Best regards,
CFO
"""
    },
    {
        "subject": "Client Project - Deliverables and Timeline",
        "from": "project.manager@client.com",
        "date": "Tue, 19 Dec 2024 14:15:00 -0700",
        "body": """Hello,

Quick update on the project timeline. We need to address these items:

1. Complete the initial design mockups
2. Review API integration requirements
3. Set up staging environment for testing

Need to receive the technical documentation by December 26, 2024.

Please submit the following:
- Project proposal document
- Technical specification PDF
- Risk assessment report

Don't forget to schedule the kickoff meeting for early January.

Thanks!
PM
"""
    },
    {
        "subject": "Legal Documents Required - Urgent",
        "from": "legal@lawfirm.com",
        "date": "Wed, 20 Dec 2024 11:00:00 -0700",
        "body": """Dear Client,

We require the following documents to proceed with your case:

TODO: Sign and return the engagement agreement
TODO: Provide copies of all relevant contracts

Documents needed:
- Corporate bylaws and articles of incorporation
- Form 990 for the past 3 years
- Employment contracts for key personnel
- Partnership agreement (if applicable)

These must be received by December 27, 2024 to meet the filing deadline.

Remind me to follow up if we haven't received everything by Monday.

Regards,
Legal Team
"""
    },
    {
        "subject": "Conference Preparation Checklist",
        "from": "events@conference.org",
        "date": "Thu, 21 Dec 2024 16:45:00 -0700",
        "body": """Hi there,

As we prepare for the upcoming conference in January, please complete these tasks:

- Book travel arrangements (flights and hotel)
- Prepare your presentation slides (30-minute slot)
- Submit your bio and headshot for the program
- Review and approve the conference agenda

Need to submit your materials by January 5, 2025.

Follow up with the venue coordinator regarding A/V requirements.

Looking forward to your participation!
Event Team
"""
    },
    {
        "subject": "Monthly Team Sync - Discussion Topics",
        "from": "team.lead@company.com",
        "date": "Fri, 22 Dec 2024 10:30:00 -0700",
        "body": """Team,

For our upcoming monthly sync, please review these topics:

TODO: Prepare Q1 2025 goals and objectives
TODO: Review team performance metrics from December

Discussion items:
* Budget allocation for new tools and software
* Hiring plans for the first quarter
* Process improvements and efficiency gains

Please send the following before the meeting:
- Individual performance reports
- Department budget requests
- Training and development proposals

Remind me to send out the meeting agenda by end of day.

Thanks,
Team Lead
"""
    }
]


def simulate_email_processing():
    """Simulate processing sample emails"""
    print("="*70)
    print("EMAIL EXTRACTION SYSTEM - TEST MODE")
    print("="*70)
    print(f"Testing with {len(SAMPLE_EMAILS)} sample emails")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize components
    extractor = EmailDataExtractor()
    automation = TaskAutomation()

    # Process each sample email
    all_results = []
    total_tasks = 0
    total_reminders = 0
    total_docs = 0
    total_deadlines = 0

    for idx, email in enumerate(SAMPLE_EMAILS, 1):
        print(f"\n[{idx}/{len(SAMPLE_EMAILS)}] Processing: {email['subject']}")
        print(f"From: {email['from']}")
        print("-" * 70)

        # Simulate email processing
        class MockEmail:
            def __init__(self, email_data):
                self.data = email_data

            def __getitem__(self, key):
                return self.data.get(key.lower(), '')

            def is_multipart(self):
                return False

            def get_payload(self, decode=False):
                return self.data['body'].encode() if decode else self.data['body']

        mock_msg = MockEmail(email)

        # Extract data
        result = {
            'subject': email['subject'],
            'from': email['from'],
            'date': email['date'],
            'tasks': extractor.extract_tasks(email['body']),
            'deadlines': extractor.extract_deadlines(email['body']),
            'documents_needed': extractor.extract_documents_needed(email['body']),
            'reminders': extractor.extract_reminders(email['body']),
            'processed_at': datetime.utcnow().isoformat()
        }

        # Display results
        if result['tasks']:
            print(f"\n✅ Tasks extracted ({len(result['tasks'])}):")
            for task in result['tasks']:
                print(f"   • {task['title']}")
                automation.save_task_locally(task)
                total_tasks += 1

        if result['reminders']:
            print(f"\n⏰ Reminders extracted ({len(result['reminders'])}):")
            for reminder in result['reminders']:
                print(f"   • {reminder['reminder']}")
                automation.save_reminder_locally(reminder)
                total_reminders += 1

        if result['deadlines']:
            print(f"\n📅 Deadlines extracted ({len(result['deadlines'])}):")
            for deadline in result['deadlines']:
                print(f"   • {deadline['date']}")
                total_deadlines += 1

        if result['documents_needed']:
            print(f"\n📄 Documents identified ({len(result['documents_needed'])}):")
            for doc in result['documents_needed']:
                print(f"   • {doc}")
            automation.save_document_request(result['documents_needed'], email['subject'])
            total_docs += len(result['documents_needed'])

        # Save processed email
        automation.save_processed_email(result)
        all_results.append(result)

    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"📧 Emails processed: {len(SAMPLE_EMAILS)}")
    print(f"✅ Total tasks extracted: {total_tasks}")
    print(f"⏰ Total reminders extracted: {total_reminders}")
    print(f"📄 Total documents identified: {total_docs}")
    print(f"📅 Total deadlines found: {total_deadlines}")
    print("\n💾 Data saved to:")
    print(f"   • /home/user/Private-Claude/data/email_tasks/tasks/")
    print(f"   • /home/user/Private-Claude/data/email_tasks/reminders/")
    print(f"   • /home/user/Private-Claude/data/email_tasks/documents/")
    print(f"   • /home/user/Private-Claude/data/email_tasks/processed_emails/")
    print("="*70 + "\n")

    # Create test report
    test_report = {
        "test_type": "simulated_email_processing",
        "timestamp": datetime.now().isoformat(),
        "email_account": "terobinsonwy@gmail.com",
        "status": "success",
        "summary": {
            "emails_processed": len(SAMPLE_EMAILS),
            "tasks_extracted": total_tasks,
            "reminders_extracted": total_reminders,
            "documents_identified": total_docs,
            "deadlines_found": total_deadlines
        },
        "emails": all_results,
        "extraction_patterns": {
            "tasks": [
                "TODO/To do patterns",
                "Action verbs (please, need to, must)",
                "Bullet points (-/*)",
                "Numbered lists (1.2.3.)"
            ],
            "reminders": [
                "Remind me/reminder",
                "Don't forget",
                "Follow up/check in"
            ],
            "deadlines": [
                "Due/deadline/by/before + date",
                "Date formats: MM/DD/YYYY, YYYY-MM-DD",
                "Written dates"
            ],
            "documents": [
                "Form + number",
                "Tax forms (W-2, 1099, 990, 1023)",
                "Document keywords + types"
            ]
        },
        "next_steps": [
            "Configure Gmail app password in .env",
            "Set up Zapier webhooks for task/reminder creation",
            "Test with actual Gmail inbox",
            "Enable continuous automation mode"
        ]
    }

    # Save test report
    report_path = "/home/user/Private-Claude/logs/email_automation_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(test_report, f, indent=2)

    print(f"📊 Full test report saved to: {report_path}\n")

    return test_report


if __name__ == '__main__':
    simulate_email_processing()
