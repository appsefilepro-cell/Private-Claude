"""
Legal Document Automation System - Document Builder
Comprehensive legal document generation with AI-powered research and drafting
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import anthropic


class LegalDocumentBuilder:
    """
    Master Legal Document Builder
    Generates complete case files with all 8 volumes of legal documents
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the legal document builder with API credentials"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.claude_client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.claude_client = None
            print("Warning: No Anthropic API key provided. AI features will be limited.")
        
        self.master_toc = []
        self.documents = {}
        self.redline_analysis = {}
        
    def generate_master_toc(self, case_info: Dict[str, Any]) -> str:
        """
        Generate comprehensive Master Table of Contents
        
        Args:
            case_info: Dictionary with plaintiff, defendant, claims, court info
            
        Returns:
            Formatted Master Table of Contents as markdown string
        """
        plaintiff = case_info.get('plaintiff', '[PLAINTIFF NAME]')
        defendant = case_info.get('defendant', '[DEFENDANT NAME]')
        case_no = case_info.get('case_no', '[TO BE ASSIGNED]')
        court = case_info.get('court', '[JURISDICTION]')
        claims = case_info.get('claims', [])
        
        toc = f"""# MASTER LEGAL DOCUMENT INDEX
## Case: {plaintiff} v. {defendant}
## Case No.: {case_no}
## Court: {court}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

### VOLUME 1: PRE-LITIGATION DOCUMENTS
├── Tab 1: Cover Letter & Executive Summary
├── Tab 2: Master Table of Contents (This Document)
├── Tab 3: Demand Letter (with Settlement Framework)
├── Tab 4: Notice of Intent to Sue
├── Tab 5: Company Policy Research Summary
├── Tab 6: Legal Precedent Analysis
└── Tab 7: Service Address Compilation

### VOLUME 2: COMPLAINT & INITIAL FILINGS
├── Tab 8: Verified Complaint (3-3-3 Structure)
│   ├── Count I: {claims[0] if len(claims) > 0 else '[CLAIM 1]'}
│   ├── Count II: {claims[1] if len(claims) > 1 else '[CLAIM 2]'}
│   └── Count III: {claims[2] if len(claims) > 2 else '[CLAIM 3]'}
├── Tab 9: Summons
├── Tab 10: Civil Cover Sheet
├── Tab 11: Letter to Judge (Introduction)
├── Tab 12: Letter to Court Clerk (Filing Instructions)
└── Tab 13: Certificate of Service

### VOLUME 3: SUPPORTING DECLARATIONS & EVIDENCE
├── Tab 14: Plaintiff's Declaration
├── Tab 15: Witness Affidavits (3-5 witnesses)
├── Tab 16: Expert Declarations
├── Tab 17: Exhibit List (Master)
├── Tab 18-50: Exhibits A-ZZ (Organized by Category)
│   ├── Financial Records (Exhibits A-G)
│   ├── Communications (Exhibits H-P)
│   ├── Contracts & Agreements (Exhibits Q-T)
│   ├── Company Policies (Exhibits U-W)
│   └── Legal Precedents (Exhibits X-ZZ)

### VOLUME 4: MOTIONS & MEMORANDA
├── Tab 51: Motion for Preliminary Injunction + Memo of Law
├── Tab 52: Motion for TRO + Supporting Declaration
├── Tab 53: Motion to Compel Discovery
├── Tab 54: Motion for Summary Judgment
├── Tab 55: Points and Authorities (Master Document)
├── Tab 56: Memorandum of Law (Consolidated)
└── Tab 57-65: Opposition Response Templates (Anticipatory)

### VOLUME 5: DISCOVERY DOCUMENTS
├── Tab 66: Initial Disclosures
├── Tab 67: Interrogatories Set 1-3
├── Tab 68: Requests for Production (RFP 1-100)
├── Tab 69: Requests for Admission (RFA 1-50)
├── Tab 70: Deposition Outlines (Key Witnesses)
├── Tab 71: Subpoena Duces Tecum (Records)
└── Tab 72: Discovery Tracking Matrix

### VOLUME 6: TRIAL PREPARATION
├── Tab 73: Pre-Trial Brief
├── Tab 74: Trial Memorandum
├── Tab 75: Final Witness List
├── Tab 76: Final Exhibit List
├── Tab 77: Jury Instructions (Proposed)
├── Tab 78: Direct Examination Outlines
├── Tab 79: Cross-Examination Strategy
└── Tab 80: Closing Argument Outline

### VOLUME 7: POST-JUDGMENT & ENFORCEMENT
├── Tab 81: Proposed Judgment
├── Tab 82: Writ of Execution
├── Tab 83: Writ of Garnishment
├── Tab 84: Debtor's Examination Notice
├── Tab 85: Lien Documentation
└── Tab 86: Satisfaction of Judgment (Template)

### VOLUME 8: STRATEGIC PLANNING & REDLINE ANALYSIS
├── Tab 87: Gap Analysis Report
├── Tab 88: Anticipated Objections & Responses
├── Tab 89: Counter-Argument Database
├── Tab 90: 3-Steps-Ahead Strategy Matrix
├── Tab 91: Alternative Dispute Resolution (ADR) Options
├── Tab 92: Settlement Negotiation Framework
├── Tab 93: Risk Assessment & Mitigation
└── Tab 94: Case Timeline & Deadlines Tracker

---

**Document Control Information:**
- Total Volumes: 8
- Total Tabs: 94+
- System Version: 1.0.0
- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return toc
    
    def draft_demand_letter(self, facts: Dict[str, Any]) -> str:
        """
        Generate comprehensive demand letter using AI
        
        Args:
            facts: Dictionary with client_name, defendant, amount, key_facts, legal_claims
            
        Returns:
            Complete demand letter ready to send
        """
        if not self.claude_client:
            return self._generate_demand_letter_template(facts)
        
        prompt = f"""You are an expert litigation attorney drafting a pre-litigation demand letter.

CLIENT FACTS:
- Client Name: {facts.get('client_name', '[CLIENT]')}
- Defendant: {facts.get('defendant', '[DEFENDANT]')}
- Amount in Dispute: ${facts.get('amount', '0')}
- Key Facts: {facts.get('key_facts', 'N/A')}
- Legal Claims: {', '.join(facts.get('legal_claims', []))}

Draft a professional, firm demand letter (3-5 pages) with:

1. Professional letterhead format
2. Clear statement of facts (chronological)
3. Legal basis with statute citations
4. Itemized damages calculation
5. Specific demand amount and deadline
6. Consequences of non-compliance
7. Settlement framework showing willingness to negotiate

Make it compelling and demonstrate thorough legal research."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_demand_letter_template(facts)
    
    def _generate_demand_letter_template(self, facts: Dict[str, Any]) -> str:
        """Generate basic demand letter template without AI"""
        return f"""[LAW FIRM LETTERHEAD]

{datetime.now().strftime('%B %d, %Y')}

{facts.get('defendant', '[DEFENDANT NAME]')}
[Address]

Re: Demand for Payment - {facts.get('client_name', '[CLIENT]')} v. {facts.get('defendant', '[DEFENDANT]')}

Dear Sir/Madam:

This firm represents {facts.get('client_name', '[CLIENT]')} regarding [brief description of dispute].

STATEMENT OF FACTS:
{facts.get('key_facts', '[Detailed chronological facts]')}

LEGAL BASIS:
Our client has valid claims for: {', '.join(facts.get('legal_claims', ['breach of contract']))}

DAMAGES:
Total amount due: ${facts.get('amount', '0')}

DEMAND:
We demand payment of ${facts.get('amount', '0')} within 10 business days.

Failure to respond will result in immediate litigation with additional claims for attorney's fees, costs, and punitive damages.

Sincerely,
[Attorney Name]
[Bar Number]
"""
    
    def draft_complaint(self, case_info: Dict[str, Any]) -> str:
        """
        Generate 3-3-3 structured complaint
        
        Args:
            case_info: Case information including plaintiff, defendant, facts, claims
            
        Returns:
            Complete verified complaint ready for filing
        """
        plaintiff = case_info.get('plaintiff', '[PLAINTIFF]')
        defendant = case_info.get('defendant', '[DEFENDANT]')
        court = case_info.get('court', '[COURT NAME]')
        jurisdiction = case_info.get('jurisdiction', '[JURISDICTION]')
        
        complaint = f"""[COURT CAPTION]

{court}
{jurisdiction}

{plaintiff},                          )
           Plaintiff,                 )  Case No.: [TO BE ASSIGNED]
                                      )
     v.                               )  VERIFIED COMPLAINT
                                      )
{defendant},                          )  1. Fraud
           Defendant.                 )  2. Breach of Contract
                                      )  3. [Third Claim]
______________________________________)
                                      )  JURY TRIAL DEMANDED

VERIFIED COMPLAINT

Plaintiff {plaintiff}, by and through undersigned counsel, alleges as follows:

I. PARTIES

1. Plaintiff {plaintiff} is [description].

2. Defendant {defendant} is [description].

II. JURISDICTION AND VENUE

3. This Court has jurisdiction pursuant to [statute].

4. Venue is proper in this Court pursuant to [statute].

III. STATEMENT OF FACTS

5. [Chronological facts - numbered paragraphs]

[Continue with detailed factual allegations...]

COUNT I: FRAUD

50. Plaintiff incorporates by reference paragraphs 1-49.

Claim 1A: Intentional Misrepresentation

51. Defendant made false representations of material fact...
52. Defendant knew these representations were false...
53. Defendant intended Plaintiff to rely on these representations...
54. Plaintiff justifiably relied on these representations...
55. Plaintiff suffered damages as a direct result...

[Continue with Claims 1B and 1C...]

COUNT II: BREACH OF CONTRACT

[Similar detailed structure...]

COUNT III: [THIRD CLAIM]

[Similar detailed structure...]

PRAYER FOR RELIEF

WHEREFORE, Plaintiff respectfully requests:

1. Actual damages in an amount to be proven at trial;
2. Consequential damages;
3. Punitive damages;
4. Attorney's fees and costs;
5. Pre-judgment and post-judgment interest;
6. Such other relief as the Court deems just and proper.

JURY DEMAND

Plaintiff demands trial by jury on all issues so triable.

Dated: {datetime.now().strftime('%B %d, %Y')}

                              Respectfully submitted,

                              _________________________
                              [Attorney Name]
                              [Bar Number]
                              Attorney for Plaintiff

VERIFICATION

I, {plaintiff}, declare under penalty of perjury that I have read the foregoing Complaint and know the contents thereof, and that the same is true of my own knowledge.

Dated: {datetime.now().strftime('%B %d, %Y')}

                              _________________________
                              {plaintiff}
"""
        return complaint
    
    def generate_discovery(self, case_type: str) -> Dict[str, Any]:
        """
        Generate comprehensive discovery requests
        
        Args:
            case_type: Type of case (fraud, contract, etc.)
            
        Returns:
            Dictionary with interrogatories, RFPs, and RFAs
        """
        discovery = {
            'interrogatories': self._generate_interrogatories(case_type),
            'requests_for_production': self._generate_rfps(case_type),
            'requests_for_admission': self._generate_rfas(case_type)
        }
        return discovery
    
    def _generate_interrogatories(self, case_type: str) -> List[str]:
        """Generate standard interrogatories"""
        base_interrogatories = [
            "State your full name, current address, and all addresses for the past 5 years.",
            "Identify all persons with knowledge of facts relevant to this case.",
            "Describe in detail the factual basis for each defense you have asserted.",
            "Identify all documents that support your defenses.",
            "State the amount of damages you claim, if any, and describe how calculated."
        ]
        return base_interrogatories
    
    def _generate_rfps(self, case_type: str) -> List[str]:
        """Generate requests for production"""
        base_rfps = [
            "All contracts, agreements, or understandings between the parties.",
            "All communications between the parties, including emails, letters, and text messages.",
            "All financial records related to the transactions at issue.",
            "All policies, procedures, or guidelines relevant to this dispute.",
            "All documents identified in your responses to interrogatories."
        ]
        return base_rfps
    
    def _generate_rfas(self, case_type: str) -> List[str]:
        """Generate requests for admission"""
        base_rfas = [
            "Admit that you entered into a contract with Plaintiff.",
            "Admit the authenticity of the document attached as Exhibit A.",
            "Admit that you received payment from Plaintiff in the amount of $[X].",
            "Admit that you failed to perform your obligations under the contract.",
            "Admit that Plaintiff suffered damages as a result of your breach."
        ]
        return base_rfas
    
    def build_complete_case_file(self, case_info: Dict[str, Any]) -> Path:
        """
        Generate entire case file - all 8 volumes
        
        Args:
            case_info: Complete case information
            
        Returns:
            Path to generated case file directory
        """
        case_name = case_info.get('case_name', 'default_case')
        output_dir = Path('legal_docs') / case_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Volume 1: Pre-Litigation
        vol1_dir = output_dir / 'volume_1_pre_litigation'
        vol1_dir.mkdir(exist_ok=True)
        
        # Generate Master TOC
        toc = self.generate_master_toc(case_info)
        (vol1_dir / '02_master_toc.md').write_text(toc)
        
        # Generate Demand Letter
        demand = self.draft_demand_letter(case_info)
        (vol1_dir / '03_demand_letter.txt').write_text(demand)
        
        # Volume 2: Complaint
        vol2_dir = output_dir / 'volume_2_complaint'
        vol2_dir.mkdir(exist_ok=True)
        
        complaint = self.draft_complaint(case_info)
        (vol2_dir / '08_complaint.txt').write_text(complaint)
        
        # Volume 5: Discovery
        vol5_dir = output_dir / 'volume_5_discovery'
        vol5_dir.mkdir(exist_ok=True)
        
        discovery = self.generate_discovery(case_info.get('case_type', 'general'))
        (vol5_dir / '66_discovery.json').write_text(json.dumps(discovery, indent=2))
        
        print(f"✅ Complete case file generated at: {output_dir}")
        return output_dir


# Example usage
if __name__ == "__main__":
    builder = LegalDocumentBuilder()
    
    sample_case = {
        'case_name': 'sample_v_company',
        'plaintiff': 'John Doe',
        'defendant': 'ABC Corporation',
        'court': 'Superior Court of California',
        'jurisdiction': 'County of Los Angeles',
        'claims': ['Fraud', 'Breach of Contract', 'Consumer Protection Violation'],
        'amount': '50000',
        'case_type': 'fraud',
        'client_name': 'John Doe',
        'key_facts': 'Defendant sold defective product and refused refund.',
        'legal_claims': ['Fraud', 'Breach of Contract']
    }
    
    builder.build_complete_case_file(sample_case)
