#!/usr/bin/env python3
"""
PDF Form Automation for Legal and Government Documents
Handles Form 1023, court filings, Texas procurement forms, and opioid grant applications
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from io import BytesIO

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("Installing reportlab...")
    os.system("pip install reportlab")
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

try:
    import fillpdf
except ImportError:
    print("Installing fillpdf...")
    os.system("pip install fillpdf")
    import fillpdf


class PDFFormAutomation:
    """Automated PDF form filling for legal and government documents"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.forms_dir = self.base_dir / 'legal-docs' / 'forms'
        self.output_dir = self.base_dir / 'legal-docs' / 'completed'
        self.templates_dir = self.base_dir / 'legal-docs' / 'templates'

        # Create directories
        for directory in [self.forms_dir, self.output_dir, self.templates_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Form URLs
        self.form_urls = {
            'form_1023': 'https://www.irs.gov/pub/irs-pdf/f1023.pdf',
            'form_1023ez': 'https://www.irs.gov/pub/irs-pdf/f1023ez.pdf',
            'form_990': 'https://www.irs.gov/pub/irs-pdf/f990.pdf',
            'form_8718': 'https://www.irs.gov/pub/irs-pdf/f8718.pdf'
        }

        # Organization data for nonprofit forms
        self.nonprofit_data = {
            'organization_name': 'APPS HOLDINGS WY INC',
            'ein': '',  # To be filled
            'address': '6301 Pale Sage Dr - 3206',
            'city': 'Houston',
            'state': 'Texas',
            'zip': '77079',
            'contact_person': 'Thurman Robinson',
            'email': 'terobinsonwy@gmail.com',
            'phone': '972-247-0653'
        }

    def download_form(self, form_key: str) -> Path:
        """
        Download IRS or government form

        Args:
            form_key: Key from form_urls dict

        Returns:
            Path to downloaded PDF
        """
        if form_key not in self.form_urls:
            print(f"❌ Unknown form: {form_key}")
            return None

        url = self.form_urls[form_key]
        filename = self.forms_dir / f"{form_key}.pdf"

        if filename.exists():
            print(f"✅ Form already exists: {filename}")
            return filename

        try:
            print(f"📥 Downloading {form_key} from {url}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Downloaded: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Error downloading {form_key}: {e}")
            return None

    def extract_form_fields(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract fillable field names from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of field names and properties
        """
        try:
            reader = PdfReader(str(pdf_path))

            if '/AcroForm' not in reader.trailer['/Root']:
                print("❌ PDF has no fillable fields")
                return {}

            fields = {}
            form = reader.trailer['/Root']['/AcroForm']

            if '/Fields' in form:
                for field in form['/Fields']:
                    field_obj = field.get_object()
                    field_name = field_obj.get('/T', 'Unknown')
                    field_type = field_obj.get('/FT', 'Unknown')
                    field_value = field_obj.get('/V', '')

                    fields[field_name] = {
                        'type': str(field_type),
                        'current_value': str(field_value)
                    }

            print(f"✅ Extracted {len(fields)} fields from {pdf_path.name}")
            return fields

        except Exception as e:
            print(f"❌ Error extracting fields: {e}")
            return {}

    def fill_form_1023_ez(self, org_data: Dict[str, str] = None) -> Path:
        """
        Fill Form 1023-EZ for 501(c)(3) application

        Args:
            org_data: Organization data dict

        Returns:
            Path to completed PDF
        """
        if org_data is None:
            org_data = self.nonprofit_data

        # Download form if needed
        form_path = self.download_form('form_1023ez')
        if not form_path:
            return None

        # Define field mappings (these are example field names - adjust based on actual PDF)
        field_data = {
            'OrganizationName': org_data.get('organization_name', ''),
            'EIN': org_data.get('ein', ''),
            'Address': org_data.get('address', ''),
            'City': org_data.get('city', ''),
            'State': org_data.get('state', ''),
            'ZIP': org_data.get('zip', ''),
            'ContactPerson': org_data.get('contact_person', ''),
            'Email': org_data.get('email', ''),
            'Phone': org_data.get('phone', ''),
            'FormationDate': datetime.now().strftime('%m/%d/%Y'),
            'PurposeStatement': 'Educational and charitable purposes',
            'ActivitiesDescription': 'Technology education and community outreach',
            'AnnualReceipts': '0',  # Under $50k for 1023-EZ
            'TotalAssets': '0'  # Under $250k for 1023-EZ
        }

        output_path = self.output_dir / f"Form_1023EZ_completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            # Use fillpdf to fill the form
            fillpdf.write_fillable_pdf(
                str(form_path),
                str(output_path),
                field_data
            )

            print(f"✅ Form 1023-EZ completed: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error filling form: {e}")
            print("   Trying alternative method...")

            # Alternative: Create overlay
            return self._fill_pdf_overlay(form_path, field_data, output_path)

    def _fill_pdf_overlay(
        self,
        template_path: Path,
        field_data: Dict[str, str],
        output_path: Path
    ) -> Path:
        """
        Fill PDF using overlay method (when direct field filling fails)

        Args:
            template_path: Path to blank PDF template
            field_data: Dictionary of field values
            output_path: Path for output file

        Returns:
            Path to completed PDF
        """
        try:
            # Create overlay with reportlab
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Example coordinates (adjust based on actual form)
            field_positions = {
                'OrganizationName': (100, 750),
                'EIN': (400, 750),
                'Address': (100, 720),
                'City': (100, 690),
                'State': (300, 690),
                'ZIP': (400, 690),
                'Email': (100, 660),
                'Phone': (350, 660)
            }

            # Draw text at coordinates
            for field_name, value in field_data.items():
                if field_name in field_positions:
                    x, y = field_positions[field_name]
                    can.drawString(x, y, str(value))

            can.save()

            # Merge overlay with template
            packet.seek(0)
            overlay = PdfReader(packet)
            template = PdfReader(str(template_path))
            output = PdfWriter()

            # Merge first page
            page = template.pages[0]
            page.merge_page(overlay.pages[0])
            output.add_page(page)

            # Add remaining pages
            for i in range(1, len(template.pages)):
                output.add_page(template.pages[i])

            # Write output
            with open(output_path, 'wb') as output_file:
                output.write(output_file)

            print(f"✅ PDF overlay method successful: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Overlay method failed: {e}")
            return None

    def generate_legal_complaint(
        self,
        case_data: Dict[str, str],
        template: str = 'default'
    ) -> Path:
        """
        Generate legal complaint from template

        Args:
            case_data: Case information dict
            template: Template name

        Returns:
            Path to generated PDF
        """
        output_path = self.output_dir / f"Complaint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            # Create PDF with reportlab
            can = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter

            # Header
            can.setFont("Helvetica-Bold", 16)
            can.drawString(100, height - 100, "IN THE DISTRICT COURT")

            can.setFont("Helvetica", 12)
            can.drawString(100, height - 130, case_data.get('court', 'HARRIS COUNTY, TEXAS'))

            # Case caption
            can.setFont("Helvetica-Bold", 14)
            can.drawString(100, height - 180, case_data.get('plaintiff', 'PLAINTIFF NAME'))
            can.drawString(100, height - 210, "vs.")
            can.drawString(100, height - 240, case_data.get('defendant', 'DEFENDANT NAME'))

            # Case number
            can.drawString(400, height - 180, f"CAUSE NO. {case_data.get('case_number', 'XXXXX')}")

            # Complaint body
            can.setFont("Helvetica", 11)
            y_position = height - 300

            complaint_text = case_data.get('complaint_body', [
                "TO THE HONORABLE JUDGE:",
                "",
                "COMES NOW the Plaintiff and files this Complaint...",
                "",
                "WHEREFORE, Plaintiff prays that Defendant be cited to appear..."
            ])

            for line in complaint_text:
                can.drawString(100, y_position, line)
                y_position -= 20

            # Signature block
            can.drawString(100, 100, "Respectfully submitted,")
            can.drawString(100, 70, f"By: {case_data.get('attorney', 'Attorney Name')}")

            can.save()

            print(f"✅ Legal complaint generated: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error generating complaint: {e}")
            return None

    def fill_texas_grant_application(
        self,
        grant_type: str,
        org_data: Dict[str, str] = None
    ) -> Path:
        """
        Fill Texas grant application (opioid or cybersecurity)

        Args:
            grant_type: 'opioid' or 'cybersecurity'
            org_data: Organization data

        Returns:
            Path to completed form
        """
        if org_data is None:
            org_data = self.nonprofit_data

        output_path = self.output_dir / f"Texas_{grant_type}_grant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            can = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter

            # Title
            can.setFont("Helvetica-Bold", 16)
            can.drawString(100, height - 100, f"TEXAS {grant_type.upper()} GRANT APPLICATION")

            # Organization info
            can.setFont("Helvetica", 11)
            y_pos = height - 150

            fields = [
                f"Organization Name: {org_data['organization_name']}",
                f"Address: {org_data['address']}",
                f"City: {org_data['city']}, State: {org_data['state']}, ZIP: {org_data['zip']}",
                f"Contact Person: {org_data['contact_person']}",
                f"Email: {org_data['email']}",
                f"Phone: {org_data['phone']}",
                "",
                "Grant Purpose:",
                f"  {grant_type.capitalize()} program funding for community outreach and support services"
            ]

            for field in fields:
                can.drawString(100, y_pos, field)
                y_pos -= 20

            can.save()

            print(f"✅ Texas {grant_type} grant application created: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating grant application: {e}")
            return None

    def batch_download_forms(self) -> List[Path]:
        """Download all common IRS forms"""
        downloaded = []

        print("\n📥 Downloading IRS forms...")

        for form_key in self.form_urls.keys():
            path = self.download_form(form_key)
            if path:
                downloaded.append(path)

        print(f"\n✅ Downloaded {len(downloaded)} forms")
        return downloaded

    def generate_dismissal_letter_pdf(self, case_data: Dict[str, str]) -> Path:
        """
        Generate dismissal notification letter as PDF

        Args:
            case_data: Case information dictionary

        Returns:
            Path to generated PDF
        """
        output_path = self.output_dir / f"Dismissal_Notice_{case_data.get('case_number', 'XXXXX')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        try:
            can = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter

            # Letterhead
            can.setFont("Helvetica-Bold", 14)
            can.drawString(100, height - 80, "APPS HOLDINGS WY INC")
            can.setFont("Helvetica", 10)
            can.drawString(100, height - 100, "6301 Pale Sage Dr - 3206, Houston, Texas 77079")
            can.drawString(100, height - 115, "Phone: 972-247-0653 | Email: terobinsonwy@gmail.com")

            # Date
            can.setFont("Helvetica", 11)
            can.drawString(100, height - 160, datetime.now().strftime('%B %d, %Y'))

            # Subject
            can.setFont("Helvetica-Bold", 12)
            can.drawString(100, height - 200, f"RE: Case No. {case_data.get('case_number', '')} - ORDER OF DISMISSAL")

            # Body
            can.setFont("Helvetica", 11)
            y_pos = height - 240

            letter_lines = [
                "Dear Stakeholder,",
                "",
                f"This letter confirms that Case No. {case_data.get('case_number', '')} has been DISMISSED FOR NONSUIT",
                "by ORDER dated February 24, 2025.",
                "",
                "CASE DETAILS:",
                f"  • Case Number: {case_data.get('case_number', '')}",
                f"  • Court: {case_data.get('court', '')}",
                f"  • Plaintiff: {case_data.get('plaintiff', '')}",
                f"  • Defendant: {case_data.get('defendant', '')}",
                f"  • Status: {case_data.get('status', 'DISMISSED')}",
                "",
                "The Honorable Jermaine Thomas, Judge Presiding, ordered:",
                "  • Case dismissed without prejudice",
                "  • Costs assessed against plaintiff",
                "  • Prior interlocutory judgments made final",
                "",
                "No further action is required at this time.",
                "",
                "Sincerely,",
                "",
                "",
                "Legal Department",
                "Apps Holdings WY Inc"
            ]

            for line in letter_lines:
                can.drawString(100, y_pos, line)
                y_pos -= 18

            can.save()

            print(f"✅ Dismissal notice PDF created: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating dismissal notice: {e}")
            return None


def main():
    """Main execution for testing"""
    print("="*70)
    print("PDF FORM AUTOMATION - LEGAL & GOVERNMENT DOCUMENTS")
    print("="*70)
    print()

    pdf_auto = PDFFormAutomation()

    # Test 1: Download IRS forms
    print("\n--- Test 1: Download IRS Forms ---")
    pdf_auto.batch_download_forms()

    # Test 2: Extract form fields
    print("\n--- Test 2: Extract Form Fields ---")
    form_1023ez_path = pdf_auto.forms_dir / 'form_1023ez.pdf'
    if form_1023ez_path.exists():
        fields = pdf_auto.extract_form_fields(form_1023ez_path)
        print(f"Form fields: {list(fields.keys())[:10]}...")  # Show first 10

    # Test 3: Generate dismissal notice
    print("\n--- Test 3: Generate Dismissal Notice PDF ---")
    case_data = {
        'case_number': '1241511',
        'court': 'Harris County - County Civil Court at Law No. 2',
        'plaintiff': 'NEW FOREST HOUSTON 2020 LLC',
        'defendant': 'THURMAN ROBINSON, ET AL.',
        'status': 'DISMISSED'
    }
    dismissal_pdf = pdf_auto.generate_dismissal_letter_pdf(case_data)

    # Test 4: Fill Form 1023-EZ (COMMENTED - uncomment when ready)
    # print("\n--- Test 4: Fill Form 1023-EZ ---")
    # pdf_auto.fill_form_1023_ez()

    # Test 5: Generate Texas grant application
    print("\n--- Test 5: Generate Texas Grant Application ---")
    pdf_auto.fill_texas_grant_application('opioid')
    pdf_auto.fill_texas_grant_application('cybersecurity')

    print("\n" + "="*70)
    print("✅ PDF automation test complete!")
    print(f"Output directory: {pdf_auto.output_dir}")
    print("="*70)


if __name__ == '__main__':
    main()
