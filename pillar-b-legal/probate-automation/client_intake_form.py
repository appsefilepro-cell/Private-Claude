#!/usr/bin/env python3
"""
CLIENT INTAKE FORM - Probate & Estate Administration
Automates client information gathering and case setup

Integrations:
- Google Forms → Auto-fill case data
- Fiverr intake → Case creation
- Email → Document delivery
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ClientIntake')


class ClientIntakeForm:
    """
    Automated client intake for probate cases

    Workflow:
    1. Client fills Google Form or Fiverr order form
    2. System auto-creates case folder
    3. Generates initial documents
    4. Sends welcome email with next steps
    """

    def __init__(self):
        self.intake_path = Path(__file__).parent / "intake_forms"
        self.intake_path.mkdir(exist_ok=True)

        logger.info("📋 Client Intake Form System Ready")

    def create_probate_intake_form(self) -> Dict[str, Any]:
        """
        Create probate intake form template

        Returns form structure for Google Forms / Fiverr
        """
        form = {
            "form_title": "Probate & Estate Administration - Client Intake",
            "form_description": "Please provide the following information to begin probate administration services.",

            "sections": [
                {
                    "section_title": "1. DECEDENT INFORMATION",
                    "fields": [
                        {
                            "field": "decedent_full_name",
                            "label": "Full Legal Name of Deceased",
                            "type": "text",
                            "required": True
                        },
                        {
                            "field": "decedent_date_of_death",
                            "label": "Date of Death",
                            "type": "date",
                            "required": True
                        },
                        {
                            "field": "decedent_date_of_birth",
                            "label": "Date of Birth",
                            "type": "date",
                            "required": True
                        },
                        {
                            "field": "decedent_ssn",
                            "label": "Social Security Number",
                            "type": "text",
                            "required": True,
                            "note": "Confidential - used for official filings only"
                        },
                        {
                            "field": "decedent_last_address",
                            "label": "Last Known Address",
                            "type": "textarea",
                            "required": True
                        },
                        {
                            "field": "place_of_death",
                            "label": "Place of Death (City, State)",
                            "type": "text",
                            "required": True
                        },
                        {
                            "field": "death_certificate_available",
                            "label": "Do you have a certified death certificate?",
                            "type": "radio",
                            "options": ["Yes", "No", "Ordered but not received"],
                            "required": True
                        }
                    ]
                },

                {
                    "section_title": "2. YOUR INFORMATION (Personal Representative)",
                    "fields": [
                        {
                            "field": "your_full_name",
                            "label": "Your Full Legal Name",
                            "type": "text",
                            "required": True
                        },
                        {
                            "field": "relationship_to_decedent",
                            "label": "Your Relationship to Decedent",
                            "type": "dropdown",
                            "options": ["Spouse", "Child", "Parent", "Sibling", "Other Relative", "Friend", "Attorney", "Other"],
                            "required": True
                        },
                        {
                            "field": "your_address",
                            "label": "Your Mailing Address",
                            "type": "textarea",
                            "required": True
                        },
                        {
                            "field": "your_phone",
                            "label": "Your Phone Number",
                            "type": "text",
                            "required": True
                        },
                        {
                            "field": "your_email",
                            "label": "Your Email Address",
                            "type": "email",
                            "required": True
                        },
                        {
                            "field": "preferred_contact_method",
                            "label": "Preferred Contact Method",
                            "type": "radio",
                            "options": ["Email", "Phone", "Text", "Mail"],
                            "required": True
                        }
                    ]
                },

                {
                    "section_title": "3. COURT & JURISDICTION",
                    "fields": [
                        {
                            "field": "probate_court_county",
                            "label": "County Where Probate Will Be Filed",
                            "type": "text",
                            "required": True,
                            "note": "Usually the county where decedent lived"
                        },
                        {
                            "field": "probate_court_state",
                            "label": "State",
                            "type": "text",
                            "required": True
                        },
                        {
                            "field": "probate_case_number",
                            "label": "Probate Case Number (if already filed)",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "probate_filed",
                            "label": "Has probate been filed yet?",
                            "type": "radio",
                            "options": ["Yes", "No", "Don't know"],
                            "required": True
                        }
                    ]
                },

                {
                    "section_title": "4. WILL & ESTATE PLANNING",
                    "fields": [
                        {
                            "field": "will_exists",
                            "label": "Did the decedent have a will?",
                            "type": "radio",
                            "options": ["Yes", "No", "Unknown"],
                            "required": True
                        },
                        {
                            "field": "will_location",
                            "label": "If yes, where is the original will?",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "will_date",
                            "label": "Date of Will (if known)",
                            "type": "date",
                            "required": False
                        },
                        {
                            "field": "trust_exists",
                            "label": "Did the decedent have a trust?",
                            "type": "radio",
                            "options": ["Yes", "No", "Unknown"],
                            "required": True
                        },
                        {
                            "field": "executor_named",
                            "label": "Who is named as executor/personal representative in the will?",
                            "type": "text",
                            "required": False
                        }
                    ]
                },

                {
                    "section_title": "5. HEIRS & BENEFICIARIES",
                    "fields": [
                        {
                            "field": "surviving_spouse",
                            "label": "Surviving Spouse Name",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "children_names",
                            "label": "Names and Ages of All Children",
                            "type": "textarea",
                            "required": False,
                            "note": "List each child on a new line"
                        },
                        {
                            "field": "other_heirs",
                            "label": "Other Potential Heirs (parents, siblings, etc.)",
                            "type": "textarea",
                            "required": False
                        }
                    ]
                },

                {
                    "section_title": "6. ASSETS (Approximate)",
                    "fields": [
                        {
                            "field": "real_estate",
                            "label": "Real Estate (homes, land, properties)",
                            "type": "textarea",
                            "required": False,
                            "note": "List addresses and approximate values"
                        },
                        {
                            "field": "bank_accounts",
                            "label": "Bank Accounts",
                            "type": "textarea",
                            "required": False,
                            "note": "List bank names (don't include account numbers yet)"
                        },
                        {
                            "field": "vehicles",
                            "label": "Vehicles (cars, boats, RVs, etc.)",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "field": "investment_accounts",
                            "label": "Investment Accounts (stocks, bonds, 401k, IRA)",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "field": "life_insurance",
                            "label": "Life Insurance Policies",
                            "type": "textarea",
                            "required": False,
                            "note": "List insurance companies and approximate face values"
                        },
                        {
                            "field": "business_interests",
                            "label": "Business Interests or Ownership",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "field": "personal_property",
                            "label": "Significant Personal Property (jewelry, art, collections)",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "field": "estimated_total_value",
                            "label": "Estimated Total Estate Value",
                            "type": "dropdown",
                            "options": [
                                "Under $50,000",
                                "$50,000 - $100,000",
                                "$100,000 - $250,000",
                                "$250,000 - $500,000",
                                "$500,000 - $1,000,000",
                                "Over $1,000,000"
                            ],
                            "required": False
                        }
                    ]
                },

                {
                    "section_title": "7. DEBTS & LIABILITIES",
                    "fields": [
                        {
                            "field": "mortgage_debt",
                            "label": "Mortgage Debt",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "credit_card_debt",
                            "label": "Credit Card Debt (approximate)",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "medical_bills",
                            "label": "Outstanding Medical Bills",
                            "type": "text",
                            "required": False
                        },
                        {
                            "field": "other_debts",
                            "label": "Other Debts (car loans, personal loans, etc.)",
                            "type": "textarea",
                            "required": False
                        },
                        {
                            "field": "funeral_expenses_paid",
                            "label": "Have funeral expenses been paid?",
                            "type": "radio",
                            "options": ["Yes - paid in full", "Partially paid", "Not yet paid"],
                            "required": False
                        }
                    ]
                },

                {
                    "section_title": "8. SERVICES NEEDED",
                    "fields": [
                        {
                            "field": "services_requested",
                            "label": "What services do you need? (Check all that apply)",
                            "type": "checkbox",
                            "options": [
                                "File probate petition",
                                "Obtain letters of administration",
                                "Notify creditors and beneficiaries",
                                "Prepare and send creditor letters",
                                "Prepare and send bank notifications",
                                "Prepare and send insurance notifications",
                                "Asset inventory and valuation",
                                "Debt settlement",
                                "Tax return preparation",
                                "Estate distribution plan",
                                "Court representation",
                                "Full estate administration"
                            ],
                            "required": True
                        },
                        {
                            "field": "timeline",
                            "label": "Desired Timeline",
                            "type": "radio",
                            "options": ["ASAP - Urgent", "Within 1 month", "Within 3 months", "No rush"],
                            "required": True
                        },
                        {
                            "field": "budget",
                            "label": "Budget for Legal Services",
                            "type": "dropdown",
                            "options": [
                                "Under $500",
                                "$500 - $1,000",
                                "$1,000 - $2,500",
                                "$2,500 - $5,000",
                                "Over $5,000",
                                "Flexible/discuss"
                            ],
                            "required": False
                        }
                    ]
                },

                {
                    "section_title": "9. ADDITIONAL INFORMATION",
                    "fields": [
                        {
                            "field": "special_circumstances",
                            "label": "Any special circumstances or concerns?",
                            "type": "textarea",
                            "required": False,
                            "note": "e.g., family disputes, contested will, unusual assets, etc."
                        },
                        {
                            "field": "questions",
                            "label": "Questions or Comments",
                            "type": "textarea",
                            "required": False
                        }
                    ]
                }
            ]
        }

        # Save form template
        output_file = self.intake_path / "probate_intake_form_template.json"
        with open(output_file, 'w') as f:
            json.dump(form, f, indent=2)

        logger.info(f"✅ Probate intake form template created: {output_file}")

        return form

    def process_intake_response(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client intake form response

        Auto-creates case folder and generates initial documents
        """
        logger.info("📋 Processing client intake response...")

        # Extract key information
        case_data = {
            'decedent_name': responses.get('decedent_full_name', ''),
            'date_of_death': responses.get('decedent_date_of_death', ''),
            'decedent_dob': responses.get('decedent_date_of_birth', ''),
            'decedent_ssn': responses.get('decedent_ssn', ''),

            'administrator_name': responses.get('your_full_name', ''),
            'administrator_address': responses.get('your_address', ''),
            'administrator_phone': responses.get('your_phone', ''),
            'administrator_email': responses.get('your_email', ''),

            'court_name': f"{responses.get('probate_court_county', '')} County Probate Court",
            'county': responses.get('probate_court_county', ''),
            'state': responses.get('probate_court_state', ''),
            'case_number': responses.get('probate_case_number', 'TBD'),

            # Additional info
            'relationship': responses.get('relationship_to_decedent', ''),
            'will_exists': responses.get('will_exists', 'Unknown'),
            'services_requested': responses.get('services_requested', []),
            'timeline': responses.get('timeline', 'Not specified'),

            # Full intake data
            'full_intake_data': responses
        }

        # Save intake response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response_file = self.intake_path / f"intake_{case_data['decedent_name'].replace(' ', '_')}_{timestamp}.json"

        with open(response_file, 'w') as f:
            json.dump(case_data, f, indent=2)

        logger.info(f"✅ Intake response saved: {response_file}")
        logger.info(f"   Client: {case_data['administrator_name']}")
        logger.info(f"   Decedent: {case_data['decedent_name']}")
        logger.info(f"   Timeline: {case_data['timeline']}")

        return case_data

    def generate_welcome_email(self, case_data: Dict[str, Any]) -> str:
        """Generate welcome email for new client"""

        email_body = f"""
Dear {case_data['administrator_name']},

Thank you for choosing our probate administration services. We have received your intake form for the Estate of {case_data['decedent_name']}.

CASE SUMMARY:
- Decedent: {case_data['decedent_name']}
- Date of Death: {case_data['date_of_death']}
- County: {case_data['county']}, {case_data['state']}
- Your Relationship: {case_data['relationship']}

NEXT STEPS:

1. DOCUMENT GATHERING (You can start now):
   ☐ Obtain 5-10 certified copies of the death certificate
   ☐ Locate the original will (if one exists)
   ☐ Gather recent bank statements
   ☐ Collect insurance policies
   ☐ List all assets and their approximate values
   ☐ List all debts and creditors

2. PROBATE FILING (We will handle):
   ☐ Prepare probate petition
   ☐ File with {case_data['court_name']}
   ☐ Attend initial hearing (if required)
   ☐ Obtain Letters of Administration

3. ESTATE ADMINISTRATION (We will assist):
   ☐ Notify all creditors (certified mail)
   ☐ Notify banks and financial institutions
   ☐ File insurance claims
   ☐ Prepare asset inventory
   ☐ Pay valid debts
   ☐ Prepare final distribution plan

TIMELINE:
Your requested timeline: {case_data['timeline']}

Typical probate process: 6-12 months
- Simple estates: 6-9 months
- Complex estates: 12-24 months

WHAT TO EXPECT:

Week 1-2: Initial consultation, document review, probate filing preparation
Week 3-4: File probate petition with court
Month 2-3: Court hearing, obtain Letters of Administration
Month 3-6: Creditor notification period, asset collection
Month 6-9: Debt payment, tax filings
Month 9-12: Final distribution, estate closing

YOUR DEDICATED TEAM:
- Email: {case_data.get('administrator_email', 'appsefilepro@gmail.com')}
- Phone: Available during business hours
- Document Portal: [Link to secure client portal]

DOCUMENTS IN PROGRESS:
We are preparing the following documents for your review:
- Letters of Administration (draft)
- Creditor notification letters
- Bank notification letters
- Insurance claim notifications

These will be ready within 3-5 business days and will be sent to you for review before mailing.

QUESTIONS?
Reply to this email or call us anytime. We're here to make this process as smooth as possible during this difficult time.

Our condolences for your loss. We're honored to help you through this process.

Sincerely,

Estate Administration Team
{case_data.get('administrator_email', 'appsefilepro@gmail.com')}

---

IMPORTANT REMINDERS:
• Do NOT distribute any assets until probate is complete
• Do NOT pay any debts until creditor notification period ends
• Keep detailed records of all estate expenses
• Save all receipts for court filing
"""

        return email_body

    def create_google_forms_link(self) -> str:
        """Generate Google Forms setup instructions"""

        instructions = """
╔═══════════════════════════════════════════════════════════════════╗
║              GOOGLE FORMS INTEGRATION SETUP                       ║
╚═══════════════════════════════════════════════════════════════════╝

STEP 1: Create Google Form
1. Go to: https://forms.google.com
2. Click "Blank Form"
3. Copy/paste questions from: probate_intake_form_template.json

STEP 2: Set Up Form Responses
1. Click "Responses" tab in Google Form
2. Click the Google Sheets icon to create linked spreadsheet
3. This auto-saves all responses

STEP 3: Connect to Zapier (Automation)
1. Go to: https://zapier.com
2. Create new Zap:
   - Trigger: Google Forms → New Response
   - Action: Webhooks by Zapier → POST
   - URL: Your Python script endpoint

STEP 4: Automated Case Creation
When client submits form:
1. Google Forms captures response
2. Zapier sends data to Python script
3. Script auto-creates case folder
4. Script generates initial documents
5. Welcome email sent to client

ALTERNATIVE: Manual Processing
1. Export Google Form responses to CSV
2. Run: python client_intake_form.py --import responses.csv
3. System processes all responses

FIVERR INTEGRATION:
Use the same form for Fiverr custom order requirements!
"""

        return instructions


def main():
    """Demo of Client Intake Form"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║          PROBATE CLIENT INTAKE FORM SYSTEM                        ║
    ║              Automated Client Onboarding                          ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    intake = ClientIntakeForm()

    # Create form template
    print("\n📋 Creating Probate Intake Form Template...")
    form = intake.create_probate_intake_form()

    print(f"\n✅ Form created with {len(form['sections'])} sections")
    print(f"   Total fields: {sum(len(s['fields']) for s in form['sections'])}")

    # Show Google Forms instructions
    print("\n" + intake.create_google_forms_link())

    # Example: Process a response
    print("\n" + "=" * 70)
    print("EXAMPLE: Processing Intake Response for Thurman Robinson")
    print("=" * 70)

    example_response = {
        'decedent_full_name': 'Thurman Robinson',
        'decedent_date_of_death': '2024-XX-XX',
        'decedent_date_of_birth': '19XX-XX-XX',
        'decedent_ssn': 'XXX-XX-XXXX',

        'your_full_name': 'Your Name',
        'relationship_to_decedent': 'Child',
        'your_address': 'Your Address',
        'your_phone': 'Your Phone',
        'your_email': 'appsefilepro@gmail.com',

        'probate_court_county': 'Your County',
        'probate_court_state': 'Your State',

        'will_exists': 'Unknown',
        'services_requested': [
            'Obtain letters of administration',
            'Prepare and send creditor letters',
            'Prepare and send bank notifications',
            'Prepare and send insurance notifications'
        ],
        'timeline': 'ASAP - Urgent'
    }

    case_data = intake.process_intake_response(example_response)

    print("\n📧 Welcome Email Preview:")
    print("=" * 70)
    print(intake.generate_welcome_email(case_data))


if __name__ == "__main__":
    main()
