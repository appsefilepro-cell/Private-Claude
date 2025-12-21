"""
Probate and Estate Administration Automation Module

This module provides comprehensive tools for managing estate probate processes,
including inventory management, court form generation, asset valuation, creditor
claim management, and beneficiary distributions.

Classes:
    - Estate: Main estate data model
    - Asset: Estate asset representation
    - Creditor: Creditor claim representation
    - Beneficiary: Beneficiary representation
    - EstateInventoryManager: Manages estate assets and inventory
    - CreditorClaimManager: Manages creditor claims
    - DistributionCalculator: Calculates beneficiary distributions
    - ProbateFormGenerator: Generates required court forms
    - ProbateWorkflowManager: Orchestrates probate workflow

Enums:
    - AssetType: Types of estate assets
    - CreditorType: Types of creditors
    - ProbateStatus: Probate process status
"""

from .probate_automation import (
    Estate,
    Asset,
    Creditor,
    Beneficiary,
    AssetType,
    CreditorType,
    ProbateStatus,
    EstateInventoryManager,
    CreditorClaimManager,
    DistributionCalculator,
    ProbateFormGenerator,
    ProbateWorkflowManager
)

__version__ = "1.0.0"
__author__ = "Legal Automation System"

__all__ = [
    "Estate",
    "Asset",
    "Creditor",
    "Beneficiary",
    "AssetType",
    "CreditorType",
    "ProbateStatus",
    "EstateInventoryManager",
    "CreditorClaimManager",
    "DistributionCalculator",
    "ProbateFormGenerator",
    "ProbateWorkflowManager"
]
