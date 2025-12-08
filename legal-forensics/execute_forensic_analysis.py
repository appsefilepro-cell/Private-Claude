"""
MASTER EXECUTION SCRIPT - Forensic Legal Data Analysis
Activates Agent 3.0 and orchestrates 40-case litigation data extraction
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forensic_data_analyzer import ForensicDataAnalyzer
from data_source_connectors import MultiSourceOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/forensic_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ForensicExecution')


def print_banner():
    """Print execution banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      AGENT X2.0 - FORENSIC LEGAL DATA ANALYSIS SYSTEM        ║
║                                                              ║
║  40-Case Litigation Portfolio Analysis                      ║
║  Multi-Source Data Extraction & Assembly                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main execution flow"""
    print_banner()

    logger.info("="*80)
    logger.info("PHASE 1: INITIALIZATION")
    logger.info("="*80)

    # Step 1: Initialize forensic analyzer
    logger.info("Initializing Forensic Data Analyzer...")
    analyzer = ForensicDataAnalyzer()
    logger.info(f"✓ Loaded {len(analyzer.cases)} cases from master list")

    # Step 2: Initialize data source connectors
    logger.info("Initializing Multi-Source Orchestrator...")
    orchestrator = MultiSourceOrchestrator()
    logger.info("✓ Data source connectors initialized")

    logger.info("\n" + "="*80)
    logger.info("PHASE 2: AUTHENTICATION & CONNECTION")
    logger.info("="*80)

    # Step 3: Authenticate with all data sources
    logger.info("Attempting authentication with all data sources...")
    auth_results = orchestrator.authenticate_all()

    authenticated_count = sum(1 for result in auth_results.values() if result)
    logger.info(f"\n✓ Authentication complete: {authenticated_count}/{len(auth_results)} sources connected")

    # Print detailed status
    connection_status = orchestrator.get_connection_status()
    print("\nDATA SOURCE STATUS:")
    print("-" * 60)
    for source, status in connection_status.items():
        icon = "✓" if status == "CONNECTED" else "✗"
        print(f"  {icon} {source}: {status}")
    print("-" * 60)

    logger.info("\n" + "="*80)
    logger.info("PHASE 3: DATA COLLECTION")
    logger.info("="*80)

    if authenticated_count == 0:
        logger.warning("⚠ No data sources authenticated")
        logger.warning("Generating template dossiers with framework structure...")
        logger.info("\nTO ENABLE DATA COLLECTION:")
        logger.info("1. Configure API credentials in config/.env")
        logger.info("2. See docs/API_SETUP_INSTRUCTIONS.md for detailed setup")
        logger.info("3. Re-run this script after configuration")
    else:
        logger.info(f"Collecting documents from {authenticated_count} authenticated sources...")
        all_documents = orchestrator.collect_all_documents([])
        logger.info(f"✓ Collected {len(all_documents)} total documents")

        # Index all documents
        logger.info("Indexing documents and mapping to cases...")
        for doc in all_documents:
            analyzer.index_document(doc)

        stats = analyzer.get_statistics()
        logger.info(f"✓ Indexed {stats['total_documents_indexed']} documents")
        logger.info(f"✓ Created {stats['total_mappings']} case-to-document mappings")

    logger.info("\n" + "="*80)
    logger.info("PHASE 4: CASE DOSSIER GENERATION")
    logger.info("="*80)

    # Step 4: Generate all 40 case dossiers
    logger.info("Generating case dossiers for all 40 cases...")
    output_dir = "case-dossiers"
    analyzer.generate_all_dossiers(output_dir)

    logger.info(f"✓ Generated all dossiers in {output_dir}/")
    logger.info(f"✓ Master report: {output_dir}/MASTER_ALL_40_CASES.md")

    logger.info("\n" + "="*80)
    logger.info("PHASE 5: COMPLETION & SUMMARY")
    logger.info("="*80)

    # Final statistics
    stats = analyzer.get_statistics()
    print("\nFINAL STATISTICS:")
    print("-" * 60)
    print(f"  Total Cases: {stats['total_cases']}")
    print(f"  Documents Indexed: {stats['total_documents_indexed']}")
    print(f"  Case-Document Mappings: {stats['total_mappings']}")
    print(f"  Cases with Evidence: {stats['cases_with_evidence']}")
    print("-" * 60)

    print("\nOUTPUT DELIVERABLES:")
    print("-" * 60)
    print(f"  1. Master Report: {output_dir}/MASTER_ALL_40_CASES.md")
    print(f"  2. Individual Dossiers: {output_dir}/case_XX_dossier.md (40 files)")
    print(f"  3. Execution Log: logs/forensic_execution_*.log")
    print("-" * 60)

    logger.info("\n✅ FORENSIC ANALYSIS COMPLETE")

    if authenticated_count == 0:
        print("\n⚠ IMPORTANT: Template dossiers generated.")
        print("To populate with actual data, configure API credentials and re-run.")
        print("See docs/API_SETUP_INSTRUCTIONS.md")
    else:
        print("\n✅ Full forensic analysis complete with real data.")

    logger.info("="*80)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nExecution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
