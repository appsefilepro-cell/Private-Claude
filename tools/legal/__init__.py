"""
Legal Document Automation System
AI-powered legal research, drafting, and strategic planning tools
"""

__version__ = "1.0.0"
__author__ = "Agent X5 Legal Team"

# Import modules with graceful fallback
try:
    from .document_builder import LegalDocumentBuilder
except ImportError as e:
    print(f"Warning: Could not import LegalDocumentBuilder: {e}")
    LegalDocumentBuilder = None

try:
    from .red_line_analyzer import RedLineAnalyzer
except ImportError as e:
    print(f"Warning: Could not import RedLineAnalyzer: {e}")
    RedLineAnalyzer = None

try:
    from .precedent_researcher import PrecedentResearcher
except ImportError as e:
    print(f"Warning: Could not import PrecedentResearcher: {e}")
    PrecedentResearcher = None

try:
    from .policy_crawler import PolicyCrawler
except ImportError as e:
    print(f"Warning: Could not import PolicyCrawler: {e}")
    PolicyCrawler = None

try:
    from .service_address_finder import ServiceAddressFinder
except ImportError as e:
    print(f"Warning: Could not import ServiceAddressFinder: {e}")
    ServiceAddressFinder = None

__all__ = [
    'LegalDocumentBuilder',
    'RedLineAnalyzer',
    'PrecedentResearcher',
    'PolicyCrawler',
    'ServiceAddressFinder'
]
