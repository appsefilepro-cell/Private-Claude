# Legal Document Automation System

## Overview

AI-powered legal document generation system with comprehensive research, drafting, and strategic planning capabilities. Designed to stay 3 steps ahead of opposing counsel with automated gap analysis, objection prediction, and counter-strategy generation.

## Features

### 🏗️ Core Modules

1. **Document Builder** (`document_builder.py`)
   - Master Table of Contents generation
   - Demand letter drafting
   - 3-3-3 structured complaint generation
   - Complete 8-volume case file automation

2. **Red Line Analyzer** (`red_line_analyzer.py`)
   - Gap identification in legal documents
   - Weakness detection
   - Objection prediction
   - 3-steps-ahead strategic analysis

3. **Precedent Researcher** (`precedent_researcher.py`)
   - Case law research and analysis
   - Precedent applicability assessment
   - Case chart generation
   - Adverse precedent identification

4. **Policy Crawler** (`policy_crawler.py`)
   - Company policy research
   - Terms of Service analysis
   - Unconscionability detection
   - Policy contradiction identification

5. **Service Address Finder** (`service_address_finder.py`)
   - Registered agent location
   - Service of process planning
   - Contact database compilation
   - Address verification

### 📋 8-Volume Case File Structure

#### Volume 1: Pre-Litigation Documents
- Cover letter and executive summary
- Master table of contents
- Demand letter with settlement framework
- Notice of intent to sue
- Company policy research summary
- Legal precedent analysis
- Service address compilation

#### Volume 2: Complaint & Initial Filings
- Verified complaint (3-3-3 structure)
- Summons
- Civil cover sheet
- Letter to judge
- Letter to court clerk
- Certificate of service

#### Volume 3: Supporting Declarations & Evidence
- Plaintiff's declaration
- Witness affidavits
- Expert declarations
- Exhibit list (master)
- Organized exhibits (A-ZZ)

#### Volume 4: Motions & Memoranda
- Motion for preliminary injunction
- Motion for TRO
- Motion to compel discovery
- Motion for summary judgment
- Points and authorities
- Memorandum of law
- Opposition response templates

#### Volume 5: Discovery Documents
- Initial disclosures
- Interrogatories (3 sets)
- Requests for production
- Requests for admission
- Deposition outlines
- Subpoena forms
- Discovery tracking matrix

#### Volume 6: Trial Preparation
- Pre-trial brief
- Trial memorandum
- Final witness list
- Final exhibit list
- Jury instructions
- Examination outlines
- Closing argument outline

#### Volume 7: Post-Judgment & Enforcement
- Proposed judgment
- Writ of execution
- Writ of garnishment
- Debtor's examination notice
- Lien documentation
- Satisfaction of judgment

#### Volume 8: Strategic Planning & Red Line Analysis
- Gap analysis report
- Anticipated objections & responses
- Counter-argument database
- 3-steps-ahead strategy matrix
- ADR options
- Settlement negotiation framework
- Risk assessment & mitigation
- Case timeline & deadlines tracker

## AI Prompt Library

Located in `prompts/legal/`:

1. **01_company_policy_research.txt** - Company policy analysis
2. **02_precedent_research.txt** - Case law research
3. **03_demand_letter.txt** - Demand letter drafting
4. **04_complaint_333.txt** - 3-3-3 complaint structure
5. **05_injunction_motion.txt** - Emergency injunction motions
6. **06_discovery_strategy.txt** - Comprehensive discovery
7. **07_service_addresses.txt** - Service of process compilation
8. **08_objection_prediction.txt** - Devil's advocate analysis

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Basic Example

```python
from tools.legal import LegalDocumentBuilder

# Initialize builder
builder = LegalDocumentBuilder()

# Define case information
case_info = {
    'case_name': 'doe_v_company',
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

# Generate complete case file
output_dir = builder.build_complete_case_file(case_info)
print(f"Case file generated at: {output_dir}")
```

### Red Line Analysis

```python
from tools.legal import RedLineAnalyzer

analyzer = RedLineAnalyzer()

# Analyze complaint for weaknesses
analysis = analyzer.analyze_complaint(complaint_text)

# Predict objections
objections = analyzer.predict_objections('fraud', complaint_text)

# Generate 3-steps-ahead strategy
strategy = analyzer.three_steps_ahead_analysis(case_info)
```

### Precedent Research

```python
from tools.legal import PrecedentResearcher

researcher = PrecedentResearcher()

# Research case law
cases = researcher.research_precedent('fraud', 'california', 'product misrepresentation')

# Generate case chart
chart = researcher.generate_case_chart(cases)

# Find adverse precedent
adverse_cases = researcher.find_adverse_precedent('fraud', 'california')
```

### Policy Analysis

```python
from tools.legal import PolicyCrawler

crawler = PolicyCrawler()

# Research company policies
research = crawler.research_company_policies("Example Corp")

# Analyze specific policy
analysis = crawler.analyze_policy(policy_text, "Terms of Service")

# Find contradictions
contradictions = crawler.find_policy_contradictions(policies_dict)
```

### Service Planning

```python
from tools.legal import ServiceAddressFinder

finder = ServiceAddressFinder()

# Find all addresses
addresses = finder.find_all_addresses("Example Corp", "Delaware")

# Generate service checklist
checklist = finder.generate_service_checklist("Example Corp")

# Verify address
verification = finder.verify_address(address, "registered_agent")
```

## 3-3-3 Complaint Structure

The system uses a proven 3-3-3 framework for maximum claim coverage:

- **3 Counts**: Three distinct legal theories (e.g., Fraud, Contract, Statute)
- **3 Claims per Count**: Three sub-theories or alternative bases per count
- **3+ Elements per Claim**: All required elements explicitly pled

This structure ensures:
- Multiple paths to recovery
- Comprehensive coverage of facts
- Difficulty in dismissing entire case
- Strong foundation for settlement leverage

## Red Line Analysis Framework

Automated "devil's advocate" analysis that:

1. **Identifies Gaps**: Missing elements, weak allegations, unclear facts
2. **Predicts Objections**: Likely motions and defenses
3. **Generates Counters**: Pre-prepared responses to all objections
4. **Maps Precedent**: Cases supporting AND opposing our position
5. **Analyzes Policy**: Company policies that help/hurt case

## Security & Privacy

⚠️ **IMPORTANT**: This system generates attorney work product and may contain privileged information.

- All generated legal documents are excluded from git (see `.gitignore`)
- API keys should be stored in environment variables
- Never commit case files or client information
- Use secure channels for sharing generated documents

## GitLab Duo Integration

The system includes `.gitlab-ci.yml` configuration for:

- Code intelligence and suggestions
- Automated security scanning
- Vulnerability detection and auto-fix
- CI/CD pipeline optimization
- Documentation generation

## Directory Structure

```
tools/legal/
├── __init__.py
├── document_builder.py
├── red_line_analyzer.py
├── precedent_researcher.py
├── policy_crawler.py
└── service_address_finder.py

prompts/legal/
├── 01_company_policy_research.txt
├── 02_precedent_research.txt
├── 03_demand_letter.txt
├── 04_complaint_333.txt
├── 05_injunction_motion.txt
├── 06_discovery_strategy.txt
├── 07_service_addresses.txt
└── 08_objection_prediction.txt

legal_docs/
└── [case_name]/
    ├── volume_1_pre_litigation/
    ├── volume_2_complaint/
    ├── volume_3_declarations/
    ├── volume_4_motions/
    ├── volume_5_discovery/
    ├── volume_6_trial_prep/
    ├── volume_7_post_judgment/
    └── volume_8_strategy/
```

## License

This system is part of the Agent X5 Legal Intelligence Platform.

## Disclaimer

This software is provided for legal research and document preparation assistance only. It does not constitute legal advice. Always review generated documents with qualified legal counsel before filing or sending. Users are responsible for ensuring compliance with all applicable rules of professional conduct and court rules.

## Support

For issues or questions, see the main repository documentation.

---

**Agent X5 Legal Intelligence Platform**
*Staying 3 Steps Ahead*
