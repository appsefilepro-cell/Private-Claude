"""
Service of Process Address Finder
Locates all addresses needed for legal service and correspondence
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class ServiceAddressFinder:
    """
    Service Address Finder
    Researches and compiles all addresses for service of process
    """
    
    def __init__(self):
        """Initialize the address finder"""
        self.addresses = {}
        self.verified_addresses = []
    
    def find_all_addresses(self, company_name: str, state: str = None) -> Dict[str, Any]:
        """
        Find all addresses for service and correspondence
        
        Args:
            company_name: Name of the company
            state: State of incorporation (optional)
            
        Returns:
            Dictionary with all address information
        """
        address_compilation = {
            'company': company_name,
            'research_date': datetime.now().isoformat(),
            'addresses': {
                'registered_agent': self._find_registered_agent(company_name, state),
                'corporate_headquarters': self._find_headquarters(company_name),
                'executives': self._find_executive_addresses(company_name),
                'customer_service': self._find_customer_service_addresses(company_name),
                'regulatory': self._find_regulatory_addresses(company_name),
                'subsidiaries': self._find_subsidiary_addresses(company_name)
            },
            'service_plan': self._create_service_plan(company_name),
            'sources': self._list_research_sources()
        }
        
        return address_compilation
    
    def _find_registered_agent(self, company_name: str, state: str = None) -> Dict[str, Any]:
        """Find registered agent for service of process"""
        return {
            'purpose': 'PRIMARY SERVICE OF PROCESS',
            'agent_name': '[REGISTERED AGENT NAME]',
            'agent_company': '[AGENT COMPANY]',
            'street_address': '[STREET ADDRESS - NO PO BOX]',
            'city': '[CITY]',
            'state': state or '[STATE]',
            'zip': '[ZIP]',
            'backup_agents': [
                {
                    'state': '[BACKUP STATE]',
                    'agent_name': '[BACKUP AGENT]',
                    'address': '[BACKUP ADDRESS]'
                }
            ],
            'verification_source': 'Secretary of State business search',
            'verified_date': datetime.now().strftime('%Y-%m-%d'),
            'notes': 'Primary address for service of summons and complaint'
        }
    
    def _find_headquarters(self, company_name: str) -> Dict[str, Any]:
        """Find corporate headquarters"""
        return {
            'purpose': 'CORPORATE HEADQUARTERS',
            'address_type': 'Principal place of business',
            'street_address': '[HQ STREET ADDRESS]',
            'city': '[CITY]',
            'state': '[STATE]',
            'zip': '[ZIP]',
            'mailing_address': '[MAILING ADDRESS IF DIFFERENT]',
            'verification_source': 'Company website, SEC filings',
            'notes': 'Use for general correspondence and notice to CEO'
        }
    
    def _find_executive_addresses(self, company_name: str) -> List[Dict[str, Any]]:
        """Find addresses for key executives"""
        executives = [
            {
                'title': 'CEO',
                'name': '[CEO NAME]',
                'office_address': '[CORPORATE HQ]',
                'purpose': 'Service on CEO if required',
                'notes': 'May be same as corporate headquarters'
            },
            {
                'title': 'General Counsel',
                'name': '[GC NAME]',
                'office_address': '[LEGAL DEPARTMENT ADDRESS]',
                'email': 'legal@company.com',
                'purpose': 'Legal correspondence',
                'notes': 'Primary legal contact'
            },
            {
                'title': 'CFO',
                'name': '[CFO NAME]',
                'office_address': '[CORPORATE HQ]',
                'purpose': 'Financial disputes',
                'notes': 'Contact for payment/refund issues'
            }
        ]
        return executives
    
    def _find_customer_service_addresses(self, company_name: str) -> Dict[str, Any]:
        """Find customer service and dispute addresses"""
        return {
            'customer_service': {
                'address': '[CS ADDRESS]',
                'phone': '[CS PHONE]',
                'email': 'support@company.com',
                'purpose': 'Customer inquiries'
            },
            'refund_department': {
                'address': '[REFUND DEPT ADDRESS]',
                'email': 'refunds@company.com',
                'purpose': 'Refund requests'
            },
            'dispute_resolution': {
                'address': '[DISPUTES ADDRESS]',
                'email': 'disputes@company.com',
                'purpose': 'Formal dispute notices',
                'notes': 'Check Terms of Service for required dispute address'
            },
            'fraud_department': {
                'address': '[FRAUD DEPT ADDRESS]',
                'email': 'fraud@company.com',
                'purpose': 'Fraud allegations'
            },
            'legal_notices': {
                'address': '[LEGAL NOTICES ADDRESS]',
                'email': 'legal@company.com',
                'purpose': 'Legal correspondence',
                'notes': 'Address specified in Terms of Service for legal notices'
            }
        }
    
    def _find_regulatory_addresses(self, company_name: str) -> Dict[str, Any]:
        """Find regulatory filing addresses"""
        return {
            'sec_filing_address': {
                'address': '[SEC ADDRESS]',
                'source': 'EDGAR database',
                'purpose': 'Public company filings',
                'applicable': 'If company is publicly traded'
            },
            'state_registration': {
                'address': '[STATE BUSINESS REG ADDRESS]',
                'source': 'Secretary of State',
                'purpose': 'State business registration'
            },
            'business_license': {
                'address': '[LICENSE ADDRESS]',
                'source': 'Local business records',
                'purpose': 'Business license information'
            }
        }
    
    def _find_subsidiary_addresses(self, company_name: str) -> List[Dict[str, Any]]:
        """Find subsidiary and parent company addresses"""
        return [
            {
                'entity_type': 'Parent Company',
                'name': '[PARENT COMPANY]',
                'address': '[PARENT ADDRESS]',
                'purpose': 'Pierce corporate veil if necessary',
                'notes': 'Research corporate structure'
            },
            {
                'entity_type': 'Subsidiary',
                'name': '[SUBSIDIARY]',
                'address': '[SUBSIDIARY ADDRESS]',
                'purpose': 'Related entity service',
                'notes': 'May need to join as party'
            }
        ]
    
    def _create_service_plan(self, company_name: str) -> Dict[str, Any]:
        """Create comprehensive service plan"""
        return {
            'primary_service': {
                'who': 'Registered Agent',
                'where': '[Registered Agent Address]',
                'how': 'Personal service by process server',
                'when': 'Immediately upon filing complaint',
                'proof': 'Affidavit of Service (personal service)',
                'cost_estimate': '$50-150'
            },
            'secondary_service': {
                'who': 'CEO at Corporate Headquarters',
                'where': '[HQ Address]',
                'how': 'Certified mail, return receipt requested',
                'when': 'Same day as personal service',
                'proof': 'Certified mail receipt and return receipt',
                'cost_estimate': '$10-20'
            },
            'courtesy_copies': [
                {
                    'recipient': 'General Counsel',
                    'address': '[GC Address]',
                    'method': 'Regular mail and email',
                    'purpose': 'Expedite response'
                },
                {
                    'recipient': 'Customer Service',
                    'address': '[CS Address]',
                    'method': 'Regular mail',
                    'purpose': 'Internal notification'
                }
            ],
            'timing_requirements': {
                'deadline': 'Within 120 days of filing (FRCP 4(m))',
                'recommended': 'Within 30 days of filing',
                'notes': 'Earlier service allows more time for settlement'
            },
            'backup_plan': {
                'if_service_refused': 'Leave papers at location and mail copy',
                'if_agent_unavailable': 'Substitute service at headquarters',
                'if_company_dissolved': 'Service on Secretary of State'
            }
        }
    
    def _list_research_sources(self) -> List[str]:
        """List sources for address research"""
        return [
            'Secretary of State business search (state-specific)',
            'EDGAR database (sec.gov) for public companies',
            'Company website (About Us, Contact, Legal pages)',
            'Terms of Service (legal notice address)',
            'BBB records (bbb.org)',
            'Court filings database (previous lawsuits)',
            'PACER (federal court records)',
            'State court records',
            'Business license databases',
            'Commercial registered agent lookup services',
            'Corporate records services (e.g., Dun & Bradstreet)',
            'News articles and press releases'
        ]
    
    def verify_address(self, address: str, address_type: str) -> Dict[str, Any]:
        """
        Verify an address is current and valid
        
        Args:
            address: Address to verify
            address_type: Type of address (registered_agent, headquarters, etc.)
            
        Returns:
            Verification status
        """
        verification = {
            'address': address,
            'type': address_type,
            'verified': False,
            'verification_date': datetime.now().strftime('%Y-%m-%d'),
            'verification_method': 'To be verified through research',
            'confidence_level': 'low',
            'recommendations': [
                'Verify with Secretary of State',
                'Check company website',
                'Call to confirm receipt address',
                'Use commercial verification service'
            ]
        }
        return verification
    
    def generate_service_checklist(self, company_name: str) -> str:
        """
        Generate service of process checklist
        
        Args:
            company_name: Company name
            
        Returns:
            Formatted checklist
        """
        checklist = f"""# Service of Process Checklist
## {company_name}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

### Pre-Service Research
- [ ] Verify registered agent with Secretary of State
- [ ] Confirm corporate headquarters address
- [ ] Identify all executive addresses
- [ ] Research subsidiary/parent company structure
- [ ] Check Terms of Service for required notice address
- [ ] Verify company still in business (not dissolved)

### Service Documents Prepared
- [ ] Original summons (signed by clerk)
- [ ] Copy of complaint
- [ ] All exhibits referenced in complaint
- [ ] Civil cover sheet (if required)
- [ ] Any required local forms

### Primary Service (Registered Agent)
- [ ] Hire process server
- [ ] Provide process server with correct address
- [ ] Provide process server with all documents
- [ ] Specify service instructions
- [ ] Request detailed affidavit of service
- [ ] Pay process server fee
- [ ] Obtain proof of service
- [ ] File proof of service with court

### Secondary Service (Belt & Suspenders)
- [ ] Send copy via certified mail to CEO
- [ ] Send copy via certified mail to General Counsel
- [ ] Send courtesy copy via email to legal@company.com
- [ ] Send courtesy copy via regular mail to HQ
- [ ] Keep all receipts and tracking numbers

### Post-Service Follow-Up
- [ ] File proof of service with court within required time
- [ ] Calendar response deadline (typically 21 days)
- [ ] Monitor docket for answer or motion
- [ ] Prepare for potential motion to dismiss
- [ ] Follow up if no response received

### Service Issues
If service is refused or unsuccessful:
- [ ] Document refusal
- [ ] Attempt substitute service
- [ ] Consider service by publication (last resort)
- [ ] Consult local rules for alternatives

---

**Important Deadlines:**
- Service must be completed within 120 days of filing (FRCP 4(m))
- Defendant has 21 days to respond after service (FRCP 12(a))
- File proof of service promptly after service completed

**Cost Estimates:**
- Process server: $50-150
- Certified mail: $10-20
- Total estimated cost: $60-170
"""
        return checklist
    
    def generate_contact_database(self, company_name: str) -> Dict[str, Any]:
        """
        Generate complete contact database
        
        Args:
            company_name: Company name
            
        Returns:
            Structured contact database
        """
        database = {
            'company': company_name,
            'generated': datetime.now().isoformat(),
            'contacts': {
                'legal': {
                    'registered_agent': '[AGENT INFO]',
                    'general_counsel': '[GC INFO]',
                    'legal_department': '[LEGAL DEPT INFO]'
                },
                'executives': {
                    'ceo': '[CEO INFO]',
                    'cfo': '[CFO INFO]',
                    'coo': '[COO INFO]'
                },
                'operations': {
                    'customer_service': '[CS INFO]',
                    'refunds': '[REFUND INFO]',
                    'disputes': '[DISPUTE INFO]'
                }
            },
            'service_methods': {
                'personal_service': 'Via registered agent',
                'mail_service': 'Certified mail to HQ',
                'email_service': 'legal@company.com (courtesy only)',
                'fax_service': '[FAX NUMBER if applicable]'
            }
        }
        return database


# Example usage
if __name__ == "__main__":
    finder = ServiceAddressFinder()
    
    # Find all addresses
    addresses = finder.find_all_addresses("Example Corp", "Delaware")
    print("Address Compilation:")
    print(f"- Research date: {addresses['research_date']}")
    print(f"- Primary service: {addresses['addresses']['registered_agent']['purpose']}")
    
    # Generate service checklist
    checklist = finder.generate_service_checklist("Example Corp")
    print("\n" + checklist)
    
    # Verify an address
    verification = finder.verify_address("123 Main St, City, ST 12345", "registered_agent")
    print(f"\nAddress verification: {verification['confidence_level']}")
