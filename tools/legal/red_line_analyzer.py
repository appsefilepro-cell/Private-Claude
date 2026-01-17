"""
Red Line Analysis Framework
Identifies gaps, weaknesses, and potential objections in legal documents
"""

from typing import List, Dict, Any, Optional
import anthropic
import os


class RedLineAnalyzer:
    """
    Red Line Analyzer - Devil's Advocate System
    Finds weaknesses and predicts opposing counsel's strategy
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the red line analyzer"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.claude_client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.claude_client = None
        
        self.gaps = []
        self.objections = []
        self.counter_strategies = []
    
    def analyze_complaint(self, complaint_text: str) -> Dict[str, Any]:
        """
        Analyze complaint for weaknesses and gaps
        
        Args:
            complaint_text: Full text of the complaint
            
        Returns:
            Dictionary with identified gaps, weaknesses, and recommendations
        """
        analysis = {
            'threshold_issues': self._check_threshold_issues(complaint_text),
            'element_gaps': self._check_element_sufficiency(complaint_text),
            'factual_weaknesses': self._identify_factual_weaknesses(complaint_text),
            'legal_vulnerabilities': self._identify_legal_vulnerabilities(complaint_text),
            'recommendations': []
        }
        
        # Generate recommendations based on findings
        if analysis['threshold_issues']:
            analysis['recommendations'].append("Address threshold defenses before filing")
        if analysis['element_gaps']:
            analysis['recommendations'].append("Strengthen pleading of required elements")
        
        return analysis
    
    def _check_threshold_issues(self, complaint_text: str) -> List[Dict[str, str]]:
        """Check for threshold defense issues"""
        issues = []
        
        # Check for common threshold issues
        checks = [
            ('standing', 'Standing properly alleged?'),
            ('jurisdiction', 'Subject matter jurisdiction clear?'),
            ('venue', 'Venue properly alleged?'),
            ('statute of limitations', 'Within limitations period?')
        ]
        
        for issue_type, question in checks:
            # Simple keyword check (would use AI in production)
            if issue_type.lower() not in complaint_text.lower():
                issues.append({
                    'type': issue_type,
                    'severity': 'high',
                    'description': f"May lack proper {issue_type} allegations",
                    'recommendation': f"Ensure {issue_type} is clearly established"
                })
        
        return issues
    
    def _check_element_sufficiency(self, complaint_text: str) -> List[Dict[str, str]]:
        """Check if all required elements are properly pled"""
        gaps = []
        
        # Check for fraud elements (if fraud is alleged)
        if 'fraud' in complaint_text.lower():
            fraud_elements = [
                'false representation',
                'knowledge of falsity',
                'intent to induce reliance',
                'justifiable reliance',
                'damages'
            ]
            
            for element in fraud_elements:
                if element not in complaint_text.lower():
                    gaps.append({
                        'claim': 'fraud',
                        'missing_element': element,
                        'severity': 'high',
                        'recommendation': f"Add specific allegations regarding {element}"
                    })
        
        return gaps
    
    def _identify_factual_weaknesses(self, complaint_text: str) -> List[Dict[str, str]]:
        """Identify potential factual weaknesses"""
        weaknesses = []
        
        # Check for vague allegations
        vague_terms = ['approximately', 'about', 'around', 'some', 'various']
        for term in vague_terms:
            if term in complaint_text.lower():
                weaknesses.append({
                    'type': 'vague_allegation',
                    'term': term,
                    'severity': 'medium',
                    'recommendation': 'Replace with specific facts and dates'
                })
        
        return weaknesses
    
    def _identify_legal_vulnerabilities(self, complaint_text: str) -> List[Dict[str, str]]:
        """Identify legal vulnerabilities"""
        vulnerabilities = []
        
        # Check for lack of legal citations
        if 'pursuant to' not in complaint_text.lower() and '§' not in complaint_text:
            vulnerabilities.append({
                'type': 'lack_of_citations',
                'severity': 'medium',
                'description': 'Few or no statutory citations',
                'recommendation': 'Add specific statute citations for each claim'
            })
        
        return vulnerabilities
    
    def predict_objections(self, claim_type: str, complaint_text: str) -> List[Dict[str, Any]]:
        """
        Predict objections opposing counsel will raise
        
        Args:
            claim_type: Type of legal claim (fraud, contract, etc.)
            complaint_text: Full complaint text
            
        Returns:
            List of predicted objections with counter-strategies
        """
        objections = []
        
        # Common objections by claim type
        if claim_type.lower() == 'fraud':
            objections.extend(self._predict_fraud_objections())
        elif claim_type.lower() == 'contract':
            objections.extend(self._predict_contract_objections())
        
        # Add general procedural objections
        objections.extend(self._predict_procedural_objections())
        
        return objections
    
    def _predict_fraud_objections(self) -> List[Dict[str, Any]]:
        """Predict common fraud defense strategies"""
        return [
            {
                'objection': 'Motion to Dismiss - Failure to Plead with Particularity',
                'legal_basis': 'FRCP 9(b) requires fraud to be pled with specificity',
                'likelihood': 'high',
                'counter_strategy': 'Ensure complaint includes who, what, when, where, and how of each fraudulent statement',
                'case_law': ['Ashcroft v. Iqbal (specificity requirements)']
            },
            {
                'objection': 'Statute of Limitations Defense',
                'legal_basis': 'Fraud claims typically have 3-year limitations period',
                'likelihood': 'medium',
                'counter_strategy': 'Document discovery date and apply delayed discovery rule',
                'case_law': ['State-specific fraud SOL cases']
            },
            {
                'objection': 'Economic Loss Rule',
                'legal_basis': 'Tort claims barred when arising from contract',
                'likelihood': 'high',
                'counter_strategy': 'Distinguish fraud from mere breach; show independent tort duty',
                'case_law': ['Robinson Helicopter Co. v. Dana Corp.']
            }
        ]
    
    def _predict_contract_objections(self) -> List[Dict[str, Any]]:
        """Predict common contract defense strategies"""
        return [
            {
                'objection': 'Statute of Frauds',
                'legal_basis': 'Certain contracts must be in writing',
                'likelihood': 'medium',
                'counter_strategy': 'Produce written agreement or prove exception (partial performance, etc.)',
                'case_law': ['State-specific Statute of Frauds']
            },
            {
                'objection': 'Failure to Mitigate Damages',
                'legal_basis': 'Plaintiff must mitigate damages',
                'likelihood': 'high',
                'counter_strategy': 'Document mitigation efforts; show damages unavoidable',
                'case_law': ['Parker v. Twentieth Century-Fox']
            }
        ]
    
    def _predict_procedural_objections(self) -> List[Dict[str, Any]]:
        """Predict common procedural objections"""
        return [
            {
                'objection': 'Motion to Compel Arbitration',
                'legal_basis': 'Arbitration clause in agreement',
                'likelihood': 'varies',
                'counter_strategy': 'Challenge arbitration clause as unconscionable; argue waiver',
                'case_law': ['AT&T Mobility v. Concepcion']
            },
            {
                'objection': 'Motion for More Definite Statement',
                'legal_basis': 'FRCP 12(e) - complaint too vague',
                'likelihood': 'low',
                'counter_strategy': 'Ensure initial complaint is detailed and specific',
                'case_law': []
            }
        ]
    
    def generate_counter_arguments(self, objection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate counter-arguments to predicted objections
        
        Args:
            objection: Dictionary describing the objection
            
        Returns:
            Dictionary with primary, secondary, and tertiary responses
        """
        counter = {
            'objection': objection.get('objection', ''),
            'responses': {
                'primary': self._generate_primary_response(objection),
                'secondary': self._generate_secondary_response(objection),
                'tertiary': self._generate_tertiary_response(objection)
            },
            'supporting_evidence': [],
            'case_law': objection.get('case_law', [])
        }
        return counter
    
    def _generate_primary_response(self, objection: Dict[str, Any]) -> str:
        """Generate primary response to objection"""
        return f"Primary Response: {objection.get('counter_strategy', 'Address objection directly with facts and law')}"
    
    def _generate_secondary_response(self, objection: Dict[str, Any]) -> str:
        """Generate fallback response"""
        return "Secondary Response: Alternative legal theory if primary response fails"
    
    def _generate_tertiary_response(self, objection: Dict[str, Any]) -> str:
        """Generate final fallback response"""
        return "Tertiary Response: Final alternative argument or procedural defense"
    
    def three_steps_ahead_analysis(self, case_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate 3-steps-ahead strategic analysis
        
        Args:
            case_info: Complete case information
            
        Returns:
            Strategic analysis with multiple levels of contingency planning
        """
        analysis = {
            'step_1_initial_filing': {
                'our_action': 'File complaint',
                'their_response': 'Motion to dismiss or answer',
                'our_counter': 'Opposition to motion or proceed to discovery'
            },
            'step_2_discovery': {
                'our_action': 'Serve comprehensive discovery',
                'their_response': 'Objections and limited responses',
                'our_counter': 'Motion to compel with specific deficiencies'
            },
            'step_3_summary_judgment': {
                'our_action': 'File motion for summary judgment',
                'their_response': 'Opposition with disputed facts',
                'our_counter': 'Reply brief with undisputed material facts'
            },
            'contingency_plans': {
                'if_dismissed': 'Amend complaint within 30 days addressing deficiencies',
                'if_arbitration': 'Challenge arbitration clause; if forced, pursue parallel claims',
                'if_settlement_offer': 'Evaluate against trial value with damages analysis'
            },
            'risk_assessment': {
                'likelihood_of_success': 'To be determined based on evidence',
                'major_risks': ['Statute of limitations', 'Lack of damages proof', 'Arbitration clause'],
                'mitigation_strategies': ['Document timeline', 'Expert witness on damages', 'Challenge arbitration']
            }
        }
        return analysis


# Example usage
if __name__ == "__main__":
    analyzer = RedLineAnalyzer()
    
    sample_complaint = """
    COMPLAINT FOR FRAUD
    
    Plaintiff alleges that Defendant made false statements about the product.
    Defendant knew the statements were false.
    Plaintiff relied on the statements and suffered damages.
    """
    
    # Analyze complaint
    analysis = analyzer.analyze_complaint(sample_complaint)
    print("Gap Analysis:", analysis)
    
    # Predict objections
    objections = analyzer.predict_objections('fraud', sample_complaint)
    print("\nPredicted Objections:", objections)
    
    # Generate 3-steps-ahead analysis
    strategy = analyzer.three_steps_ahead_analysis({'case_type': 'fraud'})
    print("\n3-Steps-Ahead Strategy:", strategy)
