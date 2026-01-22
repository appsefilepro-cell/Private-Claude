"""
Forensic Legal Data Analyzer - Agent 3.0 Integration
Comprehensive multi-source litigation data extraction and case assembly
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForensicAnalyzer")


class Case:
    """Individual litigation case data structure"""

    def __init__(self, case_number: int, caption: str):
        self.case_number = case_number
        self.caption = caption
        self.plaintiffs = []
        self.defendants = []
        self.jurisdiction = ""
        self.claims = []
        self.chronology = []
        self.evidence = []
        self.witnesses = []
        self.damages = {}
        self.keywords = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert case to dictionary"""
        return {
            "case_number": self.case_number,
            "caption": self.caption,
            "plaintiffs": self.plaintiffs,
            "defendants": self.defendants,
            "jurisdiction": self.jurisdiction,
            "claims": self.claims,
            "chronology": self.chronology,
            "evidence": self.evidence,
            "witnesses": self.witnesses,
            "damages": self.damages,
        }


class ForensicDataAnalyzer:
    """
    Main forensic analyzer for 40 litigation cases
    Coordinates multi-source data extraction and case assembly
    """

    # Master case list
    MASTER_CASE_LIST = [
        {
            "number": 1,
            "caption": "Thurman Malik Robinson, Jr. & APPS Holdings WY, Inc. v. City of Los Angeles; LAPD; Adilah Robinson; Does 1-50",
            "keywords": [
                "LAPD",
                "police",
                "excessive force",
                "1983",
                "ADA",
                "assault",
                "battery",
                "Adilah Robinson",
                "City of Los Angeles",
            ],
            "jurisdiction": "U.S. District Court, Central District of California",
            "claims": [
                "42 USC 1983",
                "ADA",
                "Assault & Battery",
                "IIED",
                "Defamation",
                "Negligence",
                "Monell",
                "Fraud",
            ],
        },
        {
            "number": 2,
            "caption": "Thurman Malik Robinson, Jr. & APPS Holdings WY, Inc. v. New Forest Houston / Novu Apartments",
            "keywords": [
                "Novu",
                "New Forest",
                "eviction",
                "ADA",
                "FHA",
                "lease",
                "apartment",
            ],
            "jurisdiction": "Harris County Civil Court / Southern District of Texas",
            "claims": ["ADA", "FHA", "Breach of Lease", "Wrongful Eviction", "IIED"],
        },
        {
            "number": 3,
            "caption": "Thurman Malik Robinson, Jr. & APPS Holdings WY, Inc. v. BMO Harris Bank",
            "keywords": ["BMO", "bank", "ADA", "financial", "accessibility"],
            "jurisdiction": "Southern District of Texas",
            "claims": ["ADA Violations", "Financial Harm", "Emotional Distress"],
        },
        # Add all 40 cases here - template provided
    ]

    def __init__(self):
        self.cases = {}
        self.global_document_index = []
        self.case_mapping = {}  # Maps document_id to case_numbers

        # Initialize all 40 cases
        for case_info in self.MASTER_CASE_LIST:
            case = Case(case_info["number"], case_info["caption"])
            case.jurisdiction = case_info["jurisdiction"]
            case.claims = case_info["claims"]
            case.keywords = case_info["keywords"]
            self.cases[case_info["number"]] = case

        logger.info(f"Initialized {len(self.cases)} cases for analysis")

    def index_document(self, doc_metadata: Dict[str, Any]) -> None:
        """
        Add document to global index and map to relevant cases

        Args:
            doc_metadata: {
                'id': unique_id,
                'filename': filename,
                'source': 'gmail|dropbox|sharepoint|onedrive',
                'path': file_path,
                'created_date': date,
                'modified_date': date,
                'content_preview': text_snippet,
                'entities': [names, companies, emails]
            }
        """
        self.global_document_index.append(doc_metadata)

        # Map to cases based on keywords
        doc_text = doc_metadata.get("content_preview", "").lower()
        doc_filename = doc_metadata.get("filename", "").lower()

        for case_num, case in self.cases.items():
            # Check if any case keywords appear in document
            for keyword in case.keywords:
                if keyword.lower() in doc_text or keyword.lower() in doc_filename:
                    if doc_metadata["id"] not in self.case_mapping:
                        self.case_mapping[doc_metadata["id"]] = []
                    if case_num not in self.case_mapping[doc_metadata["id"]]:
                        self.case_mapping[doc_metadata["id"]].append(case_num)
                        logger.debug(
                            f"Mapped doc {doc_metadata['id']} to Case {case_num}"
                        )

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using regex patterns"""
        entities = {
            "emails": [],
            "phones": [],
            "dates": [],
            "names": [],
            "dollar_amounts": [],
        }

        # Email regex
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        entities["emails"] = re.findall(email_pattern, text)

        # Phone regex (various formats)
        phone_pattern = r"(\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}"
        entities["phones"] = re.findall(phone_pattern, text)

        # Date regex (MM/DD/YYYY, etc)
        date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        entities["dates"] = re.findall(date_pattern, text)

        # Dollar amounts
        dollar_pattern = r"\$[\d,]+\.?\d{0,2}"
        entities["dollar_amounts"] = re.findall(dollar_pattern, text)

        return entities

    def build_case_chronology(self, case_number: int) -> List[Dict[str, Any]]:
        """
        Build chronological timeline for a specific case

        Returns:
            List of events sorted by date
        """
        case = self.cases[case_number]
        events = []

        # Get all documents mapped to this case
        relevant_docs = [
            doc
            for doc in self.global_document_index
            if doc["id"] in self.case_mapping
            and case_number in self.case_mapping[doc["id"]]
        ]

        # Extract events from documents
        for doc in relevant_docs:
            # Create event entry
            event = {
                "date": doc.get("created_date", ""),
                "description": f"Document: {doc['filename']}",
                "source_doc": doc["path"],
                "source_id": doc["id"],
                "entities": self.extract_entities(doc.get("content_preview", "")),
            }
            events.append(event)

        # Sort by date
        events.sort(key=lambda x: x["date"])

        return events

    def generate_case_dossier(self, case_number: int) -> str:
        """
        Generate complete case dossier in Markdown format

        Args:
            case_number: Case number from master list

        Returns:
            Markdown-formatted dossier
        """
        case = self.cases[case_number]

        dossier = f"""
# CASE DATA DOSSIER: {case.caption}

## 1. Core Metadata

**Case Title:** {case.caption}
**Case Number:** {case_number}
**Plaintiff(s):** Thurman Malik Robinson, Jr.; APPS Holdings WY, Inc.
**Defendant(s):** {', '.join(case.defendants) if case.defendants else 'See caption'}
**Jurisdiction:** {case.jurisdiction}
**Primary Legal Claims:**
{chr(10).join('- ' + claim for claim in case.claims)}

**Primary Case Theme:** [To be extracted from documents]

---

## 2. Master Chronology of Events

"""

        # Build chronology
        chronology = self.build_case_chronology(case_number)
        for event in chronology:
            dossier += f"""
### {event['date']}
**Event:** {event['description']}
**Source:** [{event['source_doc']}]

"""

        dossier += """
---

## 3. Key Individuals and Entities

[To be populated from extracted entities across all case documents]

---

## 4. Evidence Inventory

### Contracts & Agreements
[List all with document links]

### Financial Records
[List all with document links]

### Official Reports
[List all with document links]

### Written Communications
[List all email threads, letters with links]

### Supporting Documents
[List all other relevant files]

---

## 5. Verbatim Extractions for Complaint Drafting

### Direct Quotes from Defendant(s):
[Extract key quotes with source links]

### Key Factual Statements by Plaintiff(s):
[Extract statements with source links]

### Terms from Contracts:
[Extract specific clauses with source links]

---

## 6. Damages Analysis Data

### Economic Losses:
[List quantifiable losses with source documents]

### Emotional Distress Indicators:
[List evidence of emotional harm with sources]

### Statutory Violation Evidence:
[Link evidence supporting statutory claims]

---

**Dossier Generated:** {datetime.now().isoformat()}
**Documents Analyzed:** {len(chronology)}
**Status:** Phase 1 Complete - Awaiting Deep Extraction

"""

        return dossier

    def generate_all_dossiers(self, output_dir: str = "case-dossiers") -> None:
        """Generate dossiers for all 40 cases"""
        os.makedirs(output_dir, exist_ok=True)

        master_report = "# MASTER CASE DOSSIERS - ALL 40 CASES\n\n"
        master_report += f"**Generated:** {datetime.now().isoformat()}\n"
        master_report += f"**Total Cases:** {len(self.cases)}\n\n"
        master_report += "---\n\n"

        for case_num in sorted(self.cases.keys()):
            logger.info(f"Generating dossier for Case {case_num}")

            dossier = self.generate_case_dossier(case_num)

            # Save individual dossier
            filename = f"case_{case_num:02d}_dossier.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(dossier)

            # Add to master report
            master_report += dossier
            master_report += "\n\n" + "=" * 80 + "\n\n"

        # Save master report
        master_filepath = os.path.join(output_dir, "MASTER_ALL_40_CASES.md")
        with open(master_filepath, "w") as f:
            f.write(master_report)

        logger.info(f"Generated all dossiers in {output_dir}")
        logger.info(f"Master report: {master_filepath}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            "total_cases": len(self.cases),
            "total_documents_indexed": len(self.global_document_index),
            "total_mappings": sum(len(cases) for cases in self.case_mapping.values()),
            "cases_with_evidence": sum(
                1
                for case_num in self.cases.keys()
                if any(case_num in cases for cases in self.case_mapping.values())
            ),
        }


def main():
    """Main execution"""
    logger.info("=== FORENSIC LEGAL DATA ANALYZER ===")
    logger.info("Initializing Agent 3.0 forensic analysis system")

    analyzer = ForensicDataAnalyzer()

    # NOTE: In production, this would connect to actual data sources
    # For now, create framework ready for integration

    logger.info("System initialized and ready for data source integration")
    logger.info("To connect data sources, configure credentials in .env:")
    logger.info("  - GMAIL_CREDENTIALS")
    logger.info("  - DROPBOX_TOKEN")
    logger.info("  - MICROSOFT_365_CREDENTIALS")
    logger.info("  - SHAREPOINT_SITE")

    # Generate template dossiers
    logger.info("Generating template dossiers for all 40 cases")
    analyzer.generate_all_dossiers()

    # Print statistics
    stats = analyzer.get_statistics()
    logger.info(f"Analysis complete: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()
