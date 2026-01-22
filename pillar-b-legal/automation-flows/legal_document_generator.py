"""
Legal Document Generator
Automates generation of court-ready legal documents using templates and case data
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegalDocumentGenerator")


class LegalDocument:
    """Legal document data model"""

    def __init__(self, doc_type: str, case_name: str):
        self.doc_type = doc_type
        self.case_name = case_name
        self.template = None
        self.variables = {}
        self.generated_content = None
        self.output_path = None

    def load_template(self, template_path: str) -> bool:
        """Load document template"""
        try:
            with open(template_path, "r") as f:
                self.template = f.read()
            logger.info(f"Loaded template: {template_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return False

    def populate_template(self, variables: Dict[str, Any]) -> str:
        """Populate template with case-specific variables"""
        self.variables = variables
        content = self.template

        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        self.generated_content = content
        return content

    def save(self, output_dir: str) -> str:
        """Save generated document"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.case_name}_{self.doc_type}_{timestamp}.docx"
        self.output_path = os.path.join(output_dir, filename)

        try:
            # In production, this would create a proper .docx file
            # For now, save as text
            txt_path = self.output_path.replace(".docx", ".txt")
            with open(txt_path, "w") as f:
                f.write(self.generated_content)

            logger.info(f"Document saved: {txt_path}")
            return txt_path
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return None


class LegalDocumentGenerator:
    """Main generator for legal documents"""

    # Document types
    MOTION_SUMMARY_JUDGMENT = "motion_summary_judgment"
    DEMAND_LETTER = "demand_letter"
    DISCOVERY_INTERROGATORIES = "discovery_interrogatories"
    MOTION_DISMISS = "motion_dismiss"
    COMPLAINT = "complaint"

    def __init__(self, templates_dir: str = "pillar-b-legal/templates"):
        self.templates_dir = templates_dir
        self.cases_dir = "pillar-b-legal/case-management"
        self.output_dir = "pillar-b-legal/automation-flows/output"

        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        logger.info("Legal Document Generator initialized")

    def load_case_data(self, case_name: str) -> Dict[str, Any]:
        """Load case metadata and evidence"""
        case_file = os.path.join(self.cases_dir, case_name, "case_metadata.json")

        if not os.path.exists(case_file):
            logger.warning(f"Case file not found: {case_file}")
            return {}

        try:
            with open(case_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading case data: {e}")
            return {}

    def generate_motion_summary_judgment(
        self, case_name: str, case_data: Dict[str, Any]
    ) -> str:
        """Generate Motion for Summary Judgment"""
        template = """
CAUSE NO. {{case_number}}

{{plaintiff_name}}                    §    IN THE DISTRICT COURT
                                      §
VS.                                   §    {{court_name}}
                                      §
{{defendant_name}}                    §    {{jurisdiction}}

MOTION FOR SUMMARY JUDGMENT

TO THE HONORABLE JUDGE OF SAID COURT:

NOW COMES {{plaintiff_name}}, Plaintiff in the above-styled and numbered cause, and files this Motion for Summary Judgment pursuant to Rule 166a of the Texas Rules of Civil Procedure, and in support thereof would respectfully show the Court as follows:

I. SUMMARY OF THE CASE

{{case_summary}}

II. STATEMENT OF UNDISPUTED FACTS

The following material facts are established by the summary judgment evidence and are not controverted by Defendant:

{{undisputed_facts}}

III. LEGAL STANDARD

A court must grant summary judgment if the movant establishes that there is no genuine issue of material fact and that the movant is entitled to judgment as a matter of law. Tex. R. Civ. P. 166a(c).

IV. ARGUMENT

{{legal_argument}}

V. CONCLUSION

For the foregoing reasons, Plaintiff respectfully requests that the Court grant this Motion for Summary Judgment and enter judgment in favor of Plaintiff on all claims asserted in this lawsuit.

Respectfully submitted,

{{attorney_name}}
State Bar No. {{bar_number}}
{{law_firm}}
{{attorney_address}}
{{attorney_phone}}
{{attorney_email}}

ATTORNEY FOR PLAINTIFF

CERTIFICATE OF SERVICE

I hereby certify that a true and correct copy of the foregoing has been served on all counsel of record in accordance with the Texas Rules of Civil Procedure on this {{service_date}}.

{{attorney_name}}
"""

        doc = LegalDocument(self.MOTION_SUMMARY_JUDGMENT, case_name)
        doc.template = template

        # Populate with case data
        variables = {
            "case_number": case_data.get("case_number", ""),
            "plaintiff_name": case_data.get("plaintiff_name", ""),
            "defendant_name": case_data.get("defendant_name", ""),
            "court_name": case_data.get("court_name", ""),
            "jurisdiction": case_data.get("jurisdiction", ""),
            "case_summary": case_data.get("case_summary", ""),
            "undisputed_facts": case_data.get("undisputed_facts", ""),
            "legal_argument": case_data.get("legal_argument", ""),
            "attorney_name": case_data.get("attorney_name", "Thurman Malik Robinson"),
            "bar_number": case_data.get("bar_number", ""),
            "law_firm": case_data.get("law_firm", "APPS Holdings WY Inc."),
            "attorney_address": case_data.get("attorney_address", ""),
            "attorney_phone": case_data.get("attorney_phone", ""),
            "attorney_email": case_data.get("attorney_email", "appsefilepro@gmail.com"),
            "service_date": datetime.now().strftime("%B %d, %Y"),
        }

        doc.populate_template(variables)
        output_path = doc.save(self.output_dir)

        logger.info(f"Generated Motion for Summary Judgment: {output_path}")
        return output_path

    def generate_demand_letter(self, case_name: str, case_data: Dict[str, Any]) -> str:
        """Generate Demand Letter"""
        template = """
{{date}}

{{recipient_name}}
{{recipient_address}}

RE: Demand for {{demand_type}} - {{matter_description}}

Dear {{recipient_name}}:

This firm represents {{client_name}} regarding {{matter_description}}.

BACKGROUND

{{background}}

LEGAL BASIS FOR DEMAND

{{legal_basis}}

DEMAND

We demand the following:

{{demands}}

You have {{deadline_days}} days from receipt of this letter to respond. If we do not receive a satisfactory response within that timeframe, we will proceed with formal legal action without further notice.

Please direct all correspondence regarding this matter to the undersigned.

Sincerely,

{{attorney_name}}
{{law_firm}}
{{attorney_email}}
{{attorney_phone}}
"""

        doc = LegalDocument(self.DEMAND_LETTER, case_name)
        doc.template = template

        variables = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "recipient_name": case_data.get("recipient_name", ""),
            "recipient_address": case_data.get("recipient_address", ""),
            "demand_type": case_data.get("demand_type", "Payment"),
            "matter_description": case_data.get("matter_description", ""),
            "client_name": case_data.get("client_name", ""),
            "background": case_data.get("background", ""),
            "legal_basis": case_data.get("legal_basis", ""),
            "demands": case_data.get("demands", ""),
            "deadline_days": case_data.get("deadline_days", "30"),
            "attorney_name": case_data.get("attorney_name", "Thurman Malik Robinson"),
            "law_firm": case_data.get("law_firm", "APPS Holdings WY Inc."),
            "attorney_email": case_data.get("attorney_email", "appsefilepro@gmail.com"),
            "attorney_phone": case_data.get("attorney_phone", ""),
        }

        doc.populate_template(variables)
        output_path = doc.save(self.output_dir)

        logger.info(f"Generated Demand Letter: {output_path}")
        return output_path

    def generate_discovery_interrogatories(
        self, case_name: str, case_data: Dict[str, Any]
    ) -> str:
        """Generate Discovery Interrogatories"""
        template = """
CAUSE NO. {{case_number}}

{{plaintiff_name}}                    §    IN THE DISTRICT COURT
                                      §
VS.                                   §    {{court_name}}
                                      §
{{defendant_name}}                    §    {{jurisdiction}}

PLAINTIFF'S FIRST SET OF INTERROGATORIES TO DEFENDANT

TO: {{defendant_name}}

Plaintiff {{plaintiff_name}} requests that Defendant answer the following interrogatories under oath within thirty (30) days of service as required by the Texas Rules of Civil Procedure.

DEFINITIONS

1. "You" or "your" means {{defendant_name}} and all agents, employees, representatives, and attorneys.

2. "Document" means any written, recorded, or graphic matter however produced or reproduced.

INSTRUCTIONS

1. These interrogatories are continuing in character and require supplemental answers if additional information becomes available.

2. If you cannot answer an interrogatory in full, answer to the extent possible and state why you cannot answer fully.

INTERROGATORIES

{{interrogatories}}

Respectfully submitted,

{{attorney_name}}
State Bar No. {{bar_number}}
{{law_firm}}
Attorney for Plaintiff
"""

        doc = LegalDocument(self.DISCOVERY_INTERROGATORIES, case_name)
        doc.template = template

        # Generate standard interrogatories
        standard_interrogatories = """
1. State your full name, current address, date of birth, and all addresses where you have resided in the past five years.

2. Identify all persons with knowledge of relevant facts concerning this lawsuit.

3. Describe in detail all facts supporting your defense to Plaintiff's claims.

4. Identify all documents that support your defense to Plaintiff's claims.

5. Identify all experts you intend to call at trial and state the subject matter of their expected testimony.
"""

        variables = {
            "case_number": case_data.get("case_number", ""),
            "plaintiff_name": case_data.get("plaintiff_name", ""),
            "defendant_name": case_data.get("defendant_name", ""),
            "court_name": case_data.get("court_name", ""),
            "jurisdiction": case_data.get("jurisdiction", ""),
            "interrogatories": case_data.get(
                "interrogatories", standard_interrogatories
            ),
            "attorney_name": case_data.get("attorney_name", "Thurman Malik Robinson"),
            "bar_number": case_data.get("bar_number", ""),
            "law_firm": case_data.get("law_firm", "APPS Holdings WY Inc."),
        }

        doc.populate_template(variables)
        output_path = doc.save(self.output_dir)

        logger.info(f"Generated Discovery Interrogatories: {output_path}")
        return output_path

    def process_case(self, case_name: str, doc_types: List[str]) -> List[str]:
        """Process a case and generate specified documents"""
        logger.info(f"Processing case: {case_name}")

        # Load case data
        case_data = self.load_case_data(case_name)

        generated_docs = []

        for doc_type in doc_types:
            try:
                if doc_type == self.MOTION_SUMMARY_JUDGMENT:
                    doc_path = self.generate_motion_summary_judgment(
                        case_name, case_data
                    )
                    generated_docs.append(doc_path)
                elif doc_type == self.DEMAND_LETTER:
                    doc_path = self.generate_demand_letter(case_name, case_data)
                    generated_docs.append(doc_path)
                elif doc_type == self.DISCOVERY_INTERROGATORIES:
                    doc_path = self.generate_discovery_interrogatories(
                        case_name, case_data
                    )
                    generated_docs.append(doc_path)
                else:
                    logger.warning(f"Unknown document type: {doc_type}")

            except Exception as e:
                logger.error(f"Error generating {doc_type}: {e}")

        return generated_docs


def main():
    """Main entry point"""
    generator = LegalDocumentGenerator()

    # Example: Generate documents for NOVU case
    case_name = "NOVU_Apartments"
    doc_types = [
        LegalDocumentGenerator.MOTION_SUMMARY_JUDGMENT,
        LegalDocumentGenerator.DEMAND_LETTER,
        LegalDocumentGenerator.DISCOVERY_INTERROGATORIES,
    ]

    docs = generator.process_case(case_name, doc_types)

    print("\n=== Legal Documents Generated ===")
    for doc in docs:
        print(f"  - {doc}")


if __name__ == "__main__":
    main()
