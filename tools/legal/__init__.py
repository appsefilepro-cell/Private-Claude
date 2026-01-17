"""
Legal Document Automation System
AI-powered legal research, drafting, and strategic planning tools
"""

__version__ = "1.0.0"
__author__ = "Agent X5 Legal Team"

from .document_builder import LegalDocumentBuilder
from .red_line_analyzer import RedLineAnalyzer
from .precedent_researcher import PrecedentResearcher
from .policy_crawler import PolicyCrawler
from .service_address_finder import ServiceAddressFinder

__all__ = [
    'LegalDocumentBuilder',
    'RedLineAnalyzer',
    'PrecedentResearcher',
    'PolicyCrawler',
    'ServiceAddressFinder'
]
