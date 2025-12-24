#!/usr/bin/env python3
"""
MASTER LEGAL AUTOMATION ORCHESTRATOR
Integrates Gmail, PDF forms, template scraping, and AI tools for complete legal automation
Specifically handles probate Case No. 1241511 and nonprofit operations
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our automation modules
try:
    from legal_automation.gmail_automation import LegalGmailAutomation
    from legal_automation.pdf_form_automation import PDFFormAutomation
    from legal_automation.template_scraper import GovernmentTemplateScraper
except ImportError:
    # If imports fail, we're running from different location
    pass


class MasterLegalOrchestrator:
    """Master orchestrator for complete legal automation system"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.logs_dir = self.base_dir / 'logs' / 'legal-automation'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.gmail = None
        self.pdf_automation = None
        self.template_scraper = None

        # Probate case details
        self.probate_case = {
            'case_number': '1241511',
            'court': 'Harris County - County Civil Court at Law No. 2',
            'plaintiff': 'NEW FOREST HOUSTON 2020 LLC',
            'defendant': 'THURMAN ROBINSON, ET AL.',
            'defendant_address': '6301 Pale Sage Dr - 3206, Houston, Texas 77079',
            'status': 'DISMISSED',
            'dismissal_date': '2025-02-24',
            'judge': 'Honorable Jermaine Thomas',
            'property_location': 'Long Beach, California'
        }

        # Nonprofit data
        self.nonprofit_data = {
            'organization_name': 'APPS HOLDINGS WY INC',
            'address': '6301 Pale Sage Dr - 3206',
            'city': 'Houston',
            'state': 'Texas',
            'zip': '77079',
            'contact_person': 'Thurman Robinson',
            'email': 'terobinsonwy@gmail.com',
            'phone': '972-247-0653'
        }

        # Free AI tools to integrate
        self.ai_tools = {
            'casemark': {
                'url': 'https://casemark.ai',
                'api_key': None,
                'status': 'pending',
                'free_tier': '10 documents/month'
            },
            'spellbook': {
                'url': 'https://www.spellbook.legal',
                'api_key': None,
                'status': 'pending',
                'free_trial': '14 days'
            },
            'harvey_ai': {
                'url': 'https://harvey.ai',
                'api_key': None,
                'status': 'pending',
                'free_trial': '7 days'
            },
            'jotform_ai': {
                'url': 'https://www.jotform.com/ai/',
                'api_key': None,
                'status': 'active',
                'free_tier': '100 submissions/month'
            }
        }

    def initialize_all_systems(self) -> bool:
        """Initialize all automation components"""
        print("="*70)
        print("INITIALIZING MASTER LEGAL AUTOMATION SYSTEM")
        print("="*70)
        print()

        success = True

        # 1. Initialize Gmail automation
        print("1. Initializing Gmail automation...")
        try:
            self.gmail = LegalGmailAutomation()
            if self.gmail.authenticate():
                print("   ✅ Gmail automation ready")
            else:
                print("   ⚠️  Gmail authentication pending - manual setup required")
                success = False
        except Exception as e:
            print(f"   ❌ Gmail initialization error: {e}")
            success = False

        # 2. Initialize PDF automation
        print("\n2. Initializing PDF form automation...")
        try:
            self.pdf_automation = PDFFormAutomation()
            print("   ✅ PDF automation ready")
        except Exception as e:
            print(f"   ❌ PDF initialization error: {e}")
            success = False

        # 3. Initialize template scraper
        print("\n3. Initializing template scraper...")
        try:
            self.template_scraper = GovernmentTemplateScraper()
            print("   ✅ Template scraper ready")
        except Exception as e:
            print(f"   ❌ Scraper initialization error: {e}")
            success = False

        print("\n" + "="*70)
        if success:
            print("✅ ALL SYSTEMS INITIALIZED SUCCESSFULLY")
        else:
            print("⚠️  SOME SYSTEMS NEED MANUAL CONFIGURATION")
        print("="*70 + "\n")

        return success

    def execute_probate_case_workflow(self) -> bool:
        """Execute complete workflow for probate Case No. 1241511"""
        print("\n" + "="*70)
        print(f"PROBATE CASE WORKFLOW - CASE NO. {self.probate_case['case_number']}")
        print("="*70)
        print()

        workflow_log = {
            'case_number': self.probate_case['case_number'],
            'execution_time': datetime.now().isoformat(),
            'steps': []
        }

        # Step 1: Generate dismissal notification PDF
        print("Step 1: Generating dismissal notification letter...")
        try:
            if self.pdf_automation:
                dismissal_pdf = self.pdf_automation.generate_dismissal_letter_pdf(self.probate_case)
                workflow_log['steps'].append({
                    'step': 'generate_dismissal_pdf',
                    'status': 'success',
                    'file': str(dismissal_pdf) if dismissal_pdf else None
                })
                print(f"   ✅ Dismissal PDF: {dismissal_pdf}")
            else:
                print("   ❌ PDF automation not initialized")
                workflow_log['steps'].append({'step': 'generate_dismissal_pdf', 'status': 'failed'})
        except Exception as e:
            print(f"   ❌ Error: {e}")
            workflow_log['steps'].append({'step': 'generate_dismissal_pdf', 'status': 'error', 'error': str(e)})

        # Step 2: Search Gmail for case-related emails
        print("\nStep 2: Searching Gmail for case emails...")
        try:
            if self.gmail and self.gmail.service:
                case_emails = self.gmail.search_emails(
                    f"subject:{self.probate_case['case_number']}",
                    max_results=10
                )
                workflow_log['steps'].append({
                    'step': 'search_case_emails',
                    'status': 'success',
                    'count': len(case_emails)
                })
                print(f"   ✅ Found {len(case_emails)} case-related emails")
            else:
                print("   ⚠️  Gmail not authenticated - skipping")
                workflow_log['steps'].append({'step': 'search_case_emails', 'status': 'skipped'})
        except Exception as e:
            print(f"   ❌ Error: {e}")
            workflow_log['steps'].append({'step': 'search_case_emails', 'status': 'error', 'error': str(e)})

        # Step 3: Auto-label case emails
        print("\nStep 3: Auto-labeling case emails...")
        try:
            if self.gmail and self.gmail.service:
                labeled_count = self.gmail.auto_label_case_emails(self.probate_case['case_number'])
                workflow_log['steps'].append({
                    'step': 'auto_label_emails',
                    'status': 'success',
                    'count': labeled_count
                })
                print(f"   ✅ Labeled {labeled_count} emails")
            else:
                print("   ⚠️  Gmail not authenticated - skipping")
                workflow_log['steps'].append({'step': 'auto_label_emails', 'status': 'skipped'})
        except Exception as e:
            print(f"   ❌ Error: {e}")
            workflow_log['steps'].append({'step': 'auto_label_emails', 'status': 'error', 'error': str(e)})

        # Step 4: Send dismissal notifications (MANUAL APPROVAL REQUIRED)
        print("\nStep 4: Send dismissal notifications...")
        print("   ⚠️  MANUAL APPROVAL REQUIRED")
        print("   Recipients to notify:")
        print(f"      - {self.nonprofit_data['email']}")
        print("   To send, uncomment code and add recipient list.")
        workflow_log['steps'].append({
            'step': 'send_dismissal_notices',
            'status': 'pending_approval',
            'note': 'Requires manual approval before sending'
        })

        # UNCOMMENT when ready to send:
        # recipients = ['terobinsonwy@gmail.com']  # Add all stakeholders
        # if self.gmail and self.gmail.service:
        #     self.gmail.send_probate_dismissal_notice(recipients)
        #     workflow_log['steps'].append({'step': 'send_dismissal_notices', 'status': 'success'})

        # Save workflow log
        log_file = self.logs_dir / f"probate_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(workflow_log, f, indent=2)

        print(f"\n   📄 Workflow log saved: {log_file}")

        print("\n" + "="*70)
        print("✅ PROBATE CASE WORKFLOW COMPLETE")
        print("="*70 + "\n")

        return True

    def setup_nonprofit_forms(self) -> bool:
        """Set up and prepare nonprofit forms (Form 1023, grants)"""
        print("\n" + "="*70)
        print("NONPROFIT FORMS SETUP")
        print("="*70)
        print()

        # Step 1: Download IRS forms
        print("Step 1: Downloading IRS forms...")
        if self.pdf_automation:
            forms = self.pdf_automation.batch_download_forms()
            print(f"   ✅ Downloaded {len(forms)} IRS forms")
        else:
            print("   ❌ PDF automation not initialized")

        # Step 2: Generate Texas grant applications
        print("\nStep 2: Generating Texas grant applications...")
        try:
            if self.pdf_automation:
                opioid_grant = self.pdf_automation.fill_texas_grant_application(
                    'opioid',
                    self.nonprofit_data
                )
                cyber_grant = self.pdf_automation.fill_texas_grant_application(
                    'cybersecurity',
                    self.nonprofit_data
                )
                print(f"   ✅ Opioid grant: {opioid_grant}")
                print(f"   ✅ Cybersecurity grant: {cyber_grant}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Step 3: Scrape government templates
        print("\nStep 3: Scraping government templates...")
        try:
            if self.template_scraper:
                results = self.template_scraper.scrape_all_sources()
                total_links = sum(
                    len(src.get('document_links', []))
                    for src in results.get('sources', {}).values()
                    if 'document_links' in src
                )
                print(f"   ✅ Found {total_links} template links")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "="*70)
        print("✅ NONPROFIT FORMS SETUP COMPLETE")
        print("="*70 + "\n")

        return True

    def activate_free_ai_tools(self) -> Dict[str, str]:
        """Activate and configure free AI tools"""
        print("\n" + "="*70)
        print("FREE AI TOOLS ACTIVATION")
        print("="*70)
        print()

        activation_status = {}

        for tool_name, tool_info in self.ai_tools.items():
            print(f"Tool: {tool_name.upper()}")
            print(f"  URL: {tool_info['url']}")
            print(f"  Free Tier: {tool_info.get('free_tier', tool_info.get('free_trial', 'N/A'))}")
            print(f"  Status: {tool_info['status']}")

            if tool_info['status'] == 'pending':
                print(f"  ⚠️  ACTION REQUIRED: Sign up and obtain API key")
                activation_status[tool_name] = 'manual_setup_required'
            else:
                activation_status[tool_name] = 'ready'

            print()

        print("="*70)
        print("AI TOOLS ACTIVATION SUMMARY")
        print("="*70)
        for tool, status in activation_status.items():
            print(f"  {tool}: {status}")
        print()

        return activation_status

    def run_complete_automation_loop(self, iterations: int = 1) -> bool:
        """
        Run complete automation loop (Agent X5 style)

        Args:
            iterations: Number of times to run the loop

        Returns:
            True if all iterations successful
        """
        print("\n" + "="*70)
        print(f"RUNNING COMPLETE AUTOMATION LOOP - {iterations} ITERATIONS")
        print("="*70)
        print()

        for i in range(1, iterations + 1):
            print(f"\n{'#'*70}")
            print(f"# ITERATION {i}/{iterations}")
            print(f"{'#'*70}\n")

            try:
                # Execute probate workflow
                self.execute_probate_case_workflow()

                # Setup nonprofit forms
                self.setup_nonprofit_forms()

                # Brief delay between iterations
                if i < iterations:
                    print(f"\nWaiting 5 seconds before iteration {i+1}...")
                    time.sleep(5)

            except Exception as e:
                print(f"\n❌ Error in iteration {i}: {e}")
                return False

        print("\n" + "="*70)
        print(f"✅ ALL {iterations} ITERATIONS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")

        return True

    def generate_master_report(self) -> Path:
        """Generate comprehensive master report"""
        report_data = {
            'report_timestamp': datetime.now().isoformat(),
            'system_status': 'operational',
            'probate_case': self.probate_case,
            'nonprofit_data': self.nonprofit_data,
            'ai_tools': self.ai_tools,
            'components': {
                'gmail': 'initialized' if self.gmail else 'not_initialized',
                'pdf_automation': 'initialized' if self.pdf_automation else 'not_initialized',
                'template_scraper': 'initialized' if self.template_scraper else 'not_initialized'
            }
        }

        report_file = self.logs_dir / f"master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📊 Master report generated: {report_file}")

        return report_file


def main():
    """Main execution"""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "MASTER LEGAL AUTOMATION SYSTEM" + " "*23 + "║")
    print("║" + " "*20 + "Case No. 1241511" + " "*32 + "║")
    print("╚" + "═"*68 + "╝")
    print()

    # Initialize orchestrator
    orchestrator = MasterLegalOrchestrator()

    # Initialize all systems
    orchestrator.initialize_all_systems()

    # Activate free AI tools
    orchestrator.activate_free_ai_tools()

    # Execute probate case workflow
    orchestrator.execute_probate_case_workflow()

    # Setup nonprofit forms
    orchestrator.setup_nonprofit_forms()

    # Generate master report
    orchestrator.generate_master_report()

    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Set up Gmail OAuth credentials (see LEGAL_AUTOMATION_MASTER_PLAN.md)")
    print("2. Review generated dismissal letters before sending")
    print("3. Activate free AI tool trials (CaseMark, Spellbook, Harvey AI)")
    print("4. Complete Form 1023-EZ with actual organization details")
    print("5. Review and submit Texas grant applications")
    print()
    print("For automated loop execution, run:")
    print("  orchestrator.run_complete_automation_loop(iterations=10)")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
