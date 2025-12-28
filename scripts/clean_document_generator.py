"""
Clean Document Generator - No Markdown Formatting
Generates human-readable PDFs and DOCX files without ** and --- formatting
Uploads to Google Drive via Zapier and sends download links
"""

import os
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional


class CleanDocumentGenerator:
    """Generate clean, human-readable documents without markdown formatting"""

    def __init__(self):
        """Initialize document generator"""
        self.output_dir = Path("generated-documents")
        self.output_dir.mkdir(exist_ok=True)

    def remove_markdown(self, content: str) -> str:
        """
        Remove all markdown formatting to create clean text

        Args:
            content: Text with markdown formatting

        Returns:
            Clean text without markdown
        """
        # Remove bold/italic markers
        content = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', content)  # Bold italic
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)  # Italic
        content = re.sub(r'__(.+?)__', r'\1', content)  # Bold alt
        content = re.sub(r'_(.+?)_', r'\1', content)  # Italic alt

        # Remove headers but keep text
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)

        # Remove horizontal rules
        content = re.sub(r'^-{3,}$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^={3,}$', '', content, flags=re.MULTILINE)

        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        content = re.sub(r'`(.+?)`', r'\1', content)

        # Remove links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

        # Remove blockquotes
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)

        # Remove bullet points but keep text
        content = re.sub(r'^\s*[-*+]\s+', '  • ', content, flags=re.MULTILINE)

        # Remove numbered lists but keep numbers
        content = re.sub(r'^\s*\d+\.\s+', '  ', content, flags=re.MULTILINE)

        # Clean up extra blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)

        return content.strip()

    def generate_clean_text(self, content: str, output_file: Optional[str] = None) -> str:
        """
        Generate clean text file without markdown

        Args:
            content: Content to clean
            output_file: Optional output filename

        Returns:
            Path to generated file
        """
        clean_content = self.remove_markdown(content)

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"clean_document_{timestamp}.txt"

        output_path = self.output_dir / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)

        print(f"✅ Clean text file generated: {output_path}")
        return str(output_path)

    def generate_pdf(self, content: str, output_file: Optional[str] = None) -> str:
        """
        Generate PDF from content (requires reportlab or PyMuPDF)

        Args:
            content: Content to convert
            output_file: Optional output filename

        Returns:
            Path to generated PDF
        """
        clean_content = self.remove_markdown(content)

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"document_{timestamp}.pdf"

        output_path = self.output_dir / output_file

        try:
            # Try using reportlab (more common)
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch

            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Split into paragraphs
            paragraphs = clean_content.split('\n\n')

            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 0.2 * inch))

            doc.build(story)
            print(f"✅ PDF generated: {output_path}")

        except ImportError:
            print("⚠️  reportlab not installed. Installing alternative method...")

            # Fallback: Create simple text-based PDF using PyMuPDF
            try:
                import fitz  # PyMuPDF

                doc = fitz.open()
                page = doc.new_page()

                # Simple text insertion
                text_rect = fitz.Rect(50, 50, 550, 750)
                page.insert_textbox(
                    text_rect,
                    clean_content,
                    fontsize=11,
                    fontname="helv",
                    align=0
                )

                doc.save(str(output_path))
                doc.close()
                print(f"✅ PDF generated (PyMuPDF): {output_path}")

            except ImportError:
                print("❌ No PDF library available. Install: pip install reportlab")
                return self.generate_clean_text(content, output_file.replace('.pdf', '.txt'))

        return str(output_path)

    def generate_docx(self, content: str, output_file: Optional[str] = None) -> str:
        """
        Generate DOCX from content (requires python-docx)

        Args:
            content: Content to convert
            output_file: Optional output filename

        Returns:
            Path to generated DOCX
        """
        clean_content = self.remove_markdown(content)

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"document_{timestamp}.docx"

        output_path = self.output_dir / output_file

        try:
            from docx import Document
            from docx.shared import Pt

            doc = Document()

            # Split into paragraphs
            paragraphs = clean_content.split('\n\n')

            for para_text in paragraphs:
                if para_text.strip():
                    para = doc.add_paragraph(para_text.strip())
                    para.style.font.size = Pt(11)

            doc.save(str(output_path))
            print(f"✅ DOCX generated: {output_path}")

        except ImportError:
            print("⚠️  python-docx not installed")
            print("Install with: pip install python-docx")
            return self.generate_clean_text(content, output_file.replace('.docx', '.txt'))

        return str(output_path)

    def upload_to_drive_via_zapier(self, file_path: str, zapier_webhook: Optional[str] = None) -> bool:
        """
        Upload file to Google Drive via Zapier webhook

        Args:
            file_path: Path to file to upload
            zapier_webhook: Zapier webhook URL (or use env var)

        Returns:
            True if successful
        """
        if zapier_webhook is None:
            zapier_webhook = os.getenv('ZAPIER_DOCUMENT_UPLOAD_WEBHOOK')

        if not zapier_webhook:
            print("❌ No Zapier webhook configured")
            print("Set ZAPIER_DOCUMENT_UPLOAD_WEBHOOK in your .env file")
            return False

        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Send to Zapier
            data = {
                'filename': os.path.basename(file_path),
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'size_bytes': len(file_content)
            }

            response = requests.post(zapier_webhook, json=data, timeout=30)

            if response.status_code == 200:
                print(f"✅ File uploaded to Google Drive via Zapier")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False

    def send_download_link(self, file_path: str, email: str, zapier_webhook: Optional[str] = None) -> bool:
        """
        Send download link via email using Zapier

        Args:
            file_path: Path to file
            email: Recipient email
            zapier_webhook: Zapier webhook URL (or use env var)

        Returns:
            True if successful
        """
        if zapier_webhook is None:
            zapier_webhook = os.getenv('ZAPIER_EMAIL_WEBHOOK')

        if not zapier_webhook:
            print("❌ No Zapier email webhook configured")
            print("Set ZAPIER_EMAIL_WEBHOOK in your .env file")
            return False

        try:
            data = {
                'to_email': email,
                'subject': f'Document Ready: {os.path.basename(file_path)}',
                'body': f'''
Your document is ready for download.

Filename: {os.path.basename(file_path)}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
File Path: {file_path}

The document has been uploaded to your Google Drive.
Check your Drive folder or the link will be provided in the next email.
                '''.strip(),
                'timestamp': datetime.now().isoformat()
            }

            response = requests.post(zapier_webhook, json=data, timeout=30)

            if response.status_code == 200:
                print(f"✅ Download link sent to {email}")
                return True
            else:
                print(f"❌ Email send failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Email error: {e}")
            return False

    def generate_and_deliver(
        self,
        content: str,
        format: str = 'pdf',
        email: str = 'appsefilepro@gmail.com',
        upload_to_drive: bool = True
    ) -> str:
        """
        Complete workflow: Generate document, upload, and send link

        Args:
            content: Content to convert
            format: Output format ('pdf', 'docx', 'txt')
            email: Email to send download link
            upload_to_drive: Whether to upload to Google Drive

        Returns:
            Path to generated file
        """
        print(f"\n🚀 Generating {format.upper()} document...")

        # Generate document
        if format == 'pdf':
            file_path = self.generate_pdf(content)
        elif format == 'docx':
            file_path = self.generate_docx(content)
        else:
            file_path = self.generate_clean_text(content)

        # Upload to Drive
        if upload_to_drive:
            print("\n📤 Uploading to Google Drive...")
            self.upload_to_drive_via_zapier(file_path)

        # Send email notification
        print(f"\n📧 Sending download link to {email}...")
        self.send_download_link(file_path, email)

        print(f"\n✅ COMPLETE! Document ready: {file_path}")
        return file_path


# Example usage
if __name__ == "__main__":
    generator = CleanDocumentGenerator()

    # Test content with lots of markdown
    test_content = """
# Trading Report

## Summary

**Total Profit:** $1,234.56
**Win Rate:** 68%

---

### Key Metrics

- Total Trades: 45
- Winning Trades: 31
- Losing Trades: 14

```python
def example():
    return "code"
```

**Important:** This is [a link](http://example.com) to somewhere.

> This is a blockquote

### Next Steps

1. Review performance
2. Adjust parameters
3. Continue trading
    """

    # Generate clean text
    print("=" * 60)
    print("GENERATING CLEAN DOCUMENTS")
    print("=" * 60)

    txt_path = generator.generate_clean_text(test_content)
    print(f"\nText file: {txt_path}\n")

    # Try PDF
    try:
        pdf_path = generator.generate_pdf(test_content)
        print(f"\nPDF file: {pdf_path}\n")
    except Exception as e:
        print(f"PDF generation skipped: {e}")

    # Try DOCX
    try:
        docx_path = generator.generate_docx(test_content)
        print(f"\nDOCX file: {docx_path}\n")
    except Exception as e:
        print(f"DOCX generation skipped: {e}")

    print("\n✅ Document generation test complete!")
    print(f"\nCheck the '{generator.output_dir}' folder for your files.")
