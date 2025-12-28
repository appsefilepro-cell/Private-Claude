#!/usr/bin/env python3
"""
Generate PDF documents from text files for rental assistance applications
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
import os

def create_pdf_from_txt(txt_file, pdf_file):
    """Convert a text file to a formatted PDF"""

    # Read the text file
    with open(txt_file, 'r') as f:
        content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    # Container for flowables
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom style for body text
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        alignment=TA_LEFT
    )

    # Split content into paragraphs
    paragraphs = content.split('\n\n')

    for para in paragraphs:
        if para.strip():
            # Clean up the paragraph
            clean_para = para.replace('\n', ' ').strip()

            # Add to story
            p = Paragraph(clean_para, body_style)
            story.append(p)
            story.append(Spacer(1, 0.2*inch))

    # Build PDF
    doc.build(story)
    print(f"✓ Created: {pdf_file}")

def main():
    """Generate all PDFs"""

    # List of files to convert
    files = [
        ('HARDSHIP_LETTER_CURRENT_APARTMENT_CORRECTED.txt', 'Hardship_Letter_Robinson.pdf'),
        ('CATHOLIC_CHARITIES_RENTAL_ASSISTANCE_CORRECTED.txt', 'Catholic_Charities_Application.pdf'),
        ('FRONTIER_UTILITIES_PAYMENT_PLAN_CORRECTED.txt', 'Frontier_Payment_Plan.pdf'),
        ('FAX_COVER_CATHOLIC_CHARITIES_CORRECTED.txt', 'Fax_Cover_Catholic_Charities.pdf'),
        ('FAX_COVER_FRONTIER_UTILITIES_CORRECTED.txt', 'Fax_Cover_Frontier.pdf'),
        ('6301_EVICTION_APPEAL_CASE_01-25-00168-CV.txt', '6301_Eviction_Appeal.pdf'),
        ('BMO_BANK_DISPUTE_ACCOUNT_CLOSURE.txt', 'BMO_Dispute.pdf'),
        ('BRENAN_SCHOOLHOUSE_CONNECTION_SCHOLARSHIP.txt', 'Brenan_Scholarship_Application.pdf'),
        ('BRENAN_SNAP_APPLICATION_H1010.txt', 'Brenan_SNAP_Application.pdf'),
        ('BRENAN_YHDP_HOUSING_APPLICATION.txt', 'Brenan_YHDP_Housing_Application.pdf'),
    ]

    print("Generating PDFs...")
    print("=" * 50)

    for txt_file, pdf_file in files:
        if os.path.exists(txt_file):
            try:
                create_pdf_from_txt(txt_file, pdf_file)
            except Exception as e:
                print(f"✗ Error creating {pdf_file}: {e}")
        else:
            print(f"✗ File not found: {txt_file}")

    print("=" * 50)
    print("PDF generation complete!")
    print("\nAll PDFs are ready for submission.")

if __name__ == "__main__":
    main()
