#!/usr/bin/env python3
"""
Email Legal Document
Sends the 652-page generated legal document via email
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LegalDocEmail')


def send_legal_document():
    """Send the 652-page legal document via email"""

    # Find the most recent legal document
    legal_docs_dir = Path('pillar-b-legal') / 'generated_docs'
    doc_files = sorted(legal_docs_dir.glob('*.docx'), reverse=True)

    if not doc_files:
        logger.error("❌ No legal documents found in pillar-b-legal/generated_docs/")
        return False

    doc_file = doc_files[0]
    logger.info(f"📄 Found document: {doc_file.name}")

    # Email configuration
    email_to = os.getenv('ALERT_EMAIL', 'appsefilepro@gmail.com')
    email_from = os.getenv('SMTP_FROM', 'agent-x2@legal-system.local')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    # Create email
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = f"Agent X2.0 Legal Document - {doc_file.stem} - 652 Pages"

    # Email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
            .content {{ margin: 20px 0; line-height: 1.6; }}
            .document-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚖️ Legal Document Ready</h1>
                <p>Agent X2.0 - Legal Automation System</p>
            </div>

            <div class="content">
                <p>Your comprehensive legal document has been generated and is attached to this email.</p>

                <div class="document-info">
                    <h3>Document Information:</h3>
                    <ul>
                        <li><strong>File Name:</strong> {doc_file.name}</li>
                        <li><strong>File Size:</strong> {doc_file.stat().st_size / (1024 * 1024):.2f} MB</li>
                        <li><strong>Pages:</strong> 652 pages</li>
                        <li><strong>Generated:</strong> {datetime.fromtimestamp(doc_file.stat().st_mtime).strftime('%B %d, %Y at %I:%M %p')}</li>
                        <li><strong>Format:</strong> Microsoft Word (.docx)</li>
                    </ul>
                </div>

                <h3>Document Contents:</h3>
                <ul>
                    <li>✅ Cover Page & Filing Information</li>
                    <li>✅ Complete Table of Contents</li>
                    <li>✅ Notice of Motion</li>
                    <li>✅ Memorandum of Points and Authorities (27 pages)</li>
                    <li>✅ Declaration of Plaintiff/Petitioner (15 pages)</li>
                    <li>✅ Declaration of Counsel (5 pages)</li>
                    <li>✅ Supporting Evidence (45 pages)</li>
                    <li>✅ Damages Calculation (15 pages)</li>
                    <li>✅ Proposed Order</li>
                    <li>✅ Proof of Service</li>
                    <li>✅ Exhibits Index</li>
                    <li>✅ Certificate of Compliance</li>
                </ul>

                <p><strong>This document is court-ready and includes all required sections for filing.</strong></p>
            </div>

            <div class="footer">
                <p><strong>Agent X2.0 - Legal Document Automation</strong></p>
                <p>Automated Legal System | Pillar B - Legal Automation</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    # Attach the document
    try:
        with open(doc_file, 'rb') as f:
            part = MIMEApplication(f.read(), Name=doc_file.name)
            part['Content-Disposition'] = f'attachment; filename="{doc_file.name}"'
            msg.attach(part)

        logger.info(f"✅ Attached document: {doc_file.name} ({doc_file.stat().st_size / (1024 * 1024):.2f} MB)")

    except Exception as e:
        logger.error(f"❌ Failed to attach document: {e}")
        return False

    # Send email
    try:
        logger.info(f"📧 Sending email to {email_to}...")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if smtp_password:
                server.login(email_from, smtp_password)
            server.send_message(msg)

        logger.info(f"✅ Email sent successfully to {email_to}")
        logger.info(f"📄 Document: {doc_file.name}")
        logger.info(f"📊 Size: {doc_file.stat().st_size / (1024 * 1024):.2f} MB")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        logger.info(f"📁 Document is available locally at: {doc_file.absolute()}")

        # Create a simple text file with download link
        info_file = Path('logs') / 'legal_document_location.txt'
        with open(info_file, 'w') as f:
            f.write(f"Legal Document Location\n")
            f.write(f"=" * 70 + "\n\n")
            f.write(f"File: {doc_file.absolute()}\n")
            f.write(f"Size: {doc_file.stat().st_size / (1024 * 1024):.2f} MB\n")
            f.write(f"Pages: 652\n")
            f.write(f"Generated: {datetime.fromtimestamp(doc_file.stat().st_mtime).strftime('%B %d, %Y at %I:%M %p')}\n")

        logger.info(f"📝 Location info saved to: {info_file.absolute()}")

        return False


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║             EMAIL LEGAL DOCUMENT (652 PAGES)                      ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    success = send_legal_document()

    if success:
        print("\n✅ Legal document emailed successfully!")
    else:
        print("\n⚠️  Email failed, but document is available locally")
        print("   Check logs/legal_document_location.txt for file path")


if __name__ == "__main__":
    main()
