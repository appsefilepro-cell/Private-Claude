#!/usr/bin/env python3
"""
Legal Document Automation System - Demo Script
Demonstrates all features of the legal automation system
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def demo_document_builder():
    """Demo the document builder"""
    print("\n" + "="*60)
    print("DEMO: Legal Document Builder")
    print("="*60)
    
    try:
        from tools.legal.document_builder import LegalDocumentBuilder
        
        builder = LegalDocumentBuilder()
        
        # Sample case
        case_info = {
            'case_name': 'demo_case',
            'plaintiff': 'Jane Doe',
            'defendant': 'XYZ Corporation',
            'court': 'Superior Court of California',
            'jurisdiction': 'County of Los Angeles',
            'claims': ['Fraud', 'Breach of Contract', 'Consumer Protection Violation'],
            'amount': '75000',
            'case_type': 'fraud',
            'client_name': 'Jane Doe',
            'key_facts': 'Defendant sold defective product, refused refund despite policy.',
            'legal_claims': ['Fraud', 'Breach of Contract', 'Consumer Protection']
        }
        
        print("\n✓ Document Builder initialized")
        print(f"✓ Sample case: {case_info['plaintiff']} v. {case_info['defendant']}")
        
        # Generate Master TOC
        print("\n📋 Generating Master Table of Contents...")
        toc = builder.generate_master_toc(case_info)
        print(f"✓ Generated TOC ({len(toc)} characters)")
        print("\nSample TOC (first 500 chars):")
        print(toc[:500] + "...")
        
        # Generate demand letter
        print("\n📜 Generating Demand Letter...")
        demand = builder.draft_demand_letter(case_info)
        print(f"✓ Generated demand letter ({len(demand)} characters)")
        
        # Generate complaint
        print("\n⚖️  Generating 3-3-3 Complaint...")
        complaint = builder.draft_complaint(case_info)
        print(f"✓ Generated complaint ({len(complaint)} characters)")
        
        # Generate discovery
        print("\n🔍 Generating Discovery Requests...")
        discovery = builder.generate_discovery('fraud')
        print(f"✓ Generated {len(discovery['interrogatories'])} interrogatories")
        print(f"✓ Generated {len(discovery['requests_for_production'])} RFPs")
        print(f"✓ Generated {len(discovery['requests_for_admission'])} RFAs")
        
        print("\n✅ Document Builder Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def demo_red_line_analyzer():
    """Demo the red line analyzer"""
    print("\n" + "="*60)
    print("DEMO: Red Line Analyzer")
    print("="*60)
    
    try:
        from tools.legal.red_line_analyzer import RedLineAnalyzer
        
        analyzer = RedLineAnalyzer()
        
        sample_complaint = """
        COMPLAINT FOR FRAUD
        
        Plaintiff alleges that Defendant made false statements about the product.
        Defendant knew the statements were false.
        Plaintiff relied on the statements and suffered damages of $50,000.
        """
        
        print("\n✓ Red Line Analyzer initialized")
        
        # Analyze complaint
        print("\n🔍 Analyzing complaint for gaps...")
        analysis = analyzer.analyze_complaint(sample_complaint)
        print(f"✓ Found {len(analysis['threshold_issues'])} threshold issues")
        print(f"✓ Found {len(analysis['element_gaps'])} element gaps")
        print(f"✓ Found {len(analysis['factual_weaknesses'])} factual weaknesses")
        
        # Predict objections
        print("\n⚠️  Predicting objections...")
        objections = analyzer.predict_objections('fraud', sample_complaint)
        print(f"✓ Predicted {len(objections)} likely objections")
        
        if objections:
            print(f"\nSample objection: {objections[0]['objection']}")
            print(f"Likelihood: {objections[0]['likelihood']}")
        
        # 3-steps-ahead analysis
        print("\n🎯 Generating 3-steps-ahead strategy...")
        strategy = analyzer.three_steps_ahead_analysis({'case_type': 'fraud'})
        print("✓ Generated strategic analysis")
        print(f"  - Step 1: {strategy['step_1_initial_filing']['our_action']}")
        print(f"  - Step 2: {strategy['step_2_discovery']['our_action']}")
        print(f"  - Step 3: {strategy['step_3_summary_judgment']['our_action']}")
        
        print("\n✅ Red Line Analyzer Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def demo_precedent_researcher():
    """Demo the precedent researcher"""
    print("\n" + "="*60)
    print("DEMO: Precedent Researcher")
    print("="*60)
    
    try:
        from tools.legal.precedent_researcher import PrecedentResearcher
        
        researcher = PrecedentResearcher()
        
        print("\n✓ Precedent Researcher initialized")
        
        # Research fraud cases
        print("\n📚 Researching fraud precedents...")
        cases = researcher.research_precedent('fraud', 'california', 'product misrepresentation')
        print(f"✓ Found {len(cases)} relevant cases")
        
        if cases:
            print(f"\nSample case: {cases[0]['case_name']}")
            print(f"Citation: {cases[0]['citation']}")
            print(f"Holding: {cases[0]['holding'][:100]}...")
            print(f"Relevance Score: {cases[0]['relevance_score']}/10")
        
        # Generate case chart
        print("\n📊 Generating case chart...")
        chart = researcher.generate_case_chart(cases)
        print(f"✓ Generated case chart ({len(chart)} characters)")
        
        # Build precedent database
        print("\n💾 Building precedent database...")
        database = researcher.build_precedent_database(['fraud', 'contract'], 'california')
        print(f"✓ Database contains {len(database)} claim types")
        print(f"  - Fraud cases: {len(database.get('fraud', []))}")
        print(f"  - Contract cases: {len(database.get('contract', []))}")
        
        print("\n✅ Precedent Researcher Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def demo_policy_crawler():
    """Demo the policy crawler"""
    print("\n" + "="*60)
    print("DEMO: Policy Crawler")
    print("="*60)
    
    try:
        from tools.legal.policy_crawler import PolicyCrawler
        
        crawler = PolicyCrawler()
        
        print("\n✓ Policy Crawler initialized")
        
        # Research company policies
        print("\n🔎 Researching company policies...")
        research = crawler.research_company_policies("Example Corp")
        print(f"✓ Research plan created for {research['company']}")
        print(f"✓ Policies to find: {len(research['policies_to_find'])}")
        
        # Analyze sample policy
        print("\n📄 Analyzing sample policy...")
        sample_policy = """
        Terms of Service
        
        We may modify these terms at any time without notice.
        All sales are final. No refunds under any circumstances.
        You agree to mandatory arbitration and waive class action rights.
        We are not liable for any damages whatsoever.
        """
        
        analysis = crawler.analyze_policy(sample_policy, "Terms of Service")
        print(f"✓ Policy analyzed")
        print(f"  - Unfair terms: {len(analysis['unfair_terms'])}")
        print(f"  - Unconscionable clauses: {len(analysis['unconscionable_clauses'])}")
        print(f"  - Violations: {len(analysis['consumer_protection_violations'])}")
        
        if analysis['unconscionable_clauses']:
            print(f"\nSample finding: {analysis['unconscionable_clauses'][0]['clause_type']}")
            print(f"Severity: {analysis['unconscionable_clauses'][0]['severity']}")
        
        print("\n✅ Policy Crawler Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def demo_service_finder():
    """Demo the service address finder"""
    print("\n" + "="*60)
    print("DEMO: Service Address Finder")
    print("="*60)
    
    try:
        from tools.legal.service_address_finder import ServiceAddressFinder
        
        finder = ServiceAddressFinder()
        
        print("\n✓ Service Address Finder initialized")
        
        # Find addresses
        print("\n📍 Finding service addresses...")
        addresses = finder.find_all_addresses("Example Corp", "Delaware")
        print(f"✓ Address compilation created")
        print(f"  - Research date: {addresses['research_date']}")
        print(f"  - Primary service: {addresses['addresses']['registered_agent']['purpose']}")
        
        # Generate service checklist
        print("\n✅ Generating service checklist...")
        checklist = finder.generate_service_checklist("Example Corp")
        print(f"✓ Checklist generated ({len(checklist)} characters)")
        
        # Verify address
        print("\n🔐 Verifying sample address...")
        verification = finder.verify_address("123 Main St, City, ST 12345", "registered_agent")
        print(f"✓ Verification status: {verification['confidence_level']}")
        print(f"✓ Recommendations: {len(verification['recommendations'])}")
        
        print("\n✅ Service Address Finder Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("LEGAL DOCUMENT AUTOMATION SYSTEM - FULL DEMO")
    print("Agent X5 Legal Intelligence Platform")
    print("="*60)
    
    results = {
        'Document Builder': demo_document_builder(),
        'Red Line Analyzer': demo_red_line_analyzer(),
        'Precedent Researcher': demo_precedent_researcher(),
        'Policy Crawler': demo_policy_crawler(),
        'Service Address Finder': demo_service_finder()
    }
    
    # Summary
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    for module, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {module}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} modules passed")
    
    if passed == total:
        print("\n🎉 All modules working correctly!")
        print("System ready for legal document generation.")
    else:
        print(f"\n⚠️  {total - passed} module(s) need attention")
    
    print("\n" + "="*60)
    print("Note: AI features require ANTHROPIC_API_KEY environment variable")
    print("="*60)

if __name__ == "__main__":
    main()
