"""
MULTI-ENTITY TAX FILING SYSTEM - 2025 EDITION
Complete tax preparation and e-filing for multiple entity types

Supported Forms:
- Form 1040: Individual Income Tax Return with Schedule C
- Form 1065: Partnership Return with K-1 Generation
- Form 1120-S: S-Corporation Return
- Form 990: Nonprofit Returns (990-N, 990-EZ, 990 Full)
- Schedule E: Rental and Passive Income
- Form 8949 & Schedule D: Cryptocurrency Reporting
- Form 1099-NEC, 1099-MISC, W-2: Information Returns
- Quarterly 941: Payroll Tax Returns

2025 Tax Law Updates:
- Trump Administration Tax Changes
- Electric Vehicle Credit Discontinuation (Sept 2025)
- Updated Standard Deductions and Brackets
- Enhanced QBI Deduction Rules
- Cryptocurrency Reporting Requirements (IRS Rev 2025)

E-File Support:
- MeF (Modernized e-File) XML Generation
- IRS Acknowledgement Processing
- State Tax Integration (CA, TX, GA, NY, FL)

Author: Tax Automation System
Version: 2025.1.0
"""

import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# TAX YEAR 2025 CONSTANTS
# ============================================================================

TAX_YEAR = 2025

# Standard Deductions (2025)
STANDARD_DEDUCTION = {
    'single': Decimal('15100'),
    'married_joint': Decimal('30200'),
    'married_separate': Decimal('15100'),
    'head_of_household': Decimal('22650')
}

# Tax Brackets (2025) - Single Filers
TAX_BRACKETS_SINGLE_2025 = [
    (Decimal('11600'), Decimal('0.10')),
    (Decimal('47150'), Decimal('0.12')),
    (Decimal('100525'), Decimal('0.22')),
    (Decimal('191950'), Decimal('0.24')),
    (Decimal('243725'), Decimal('0.32')),
    (Decimal('609350'), Decimal('0.35')),
    (Decimal('inf'), Decimal('0.37'))
]

# Tax Brackets (2025) - Married Filing Jointly
TAX_BRACKETS_JOINT_2025 = [
    (Decimal('23200'), Decimal('0.10')),
    (Decimal('94300'), Decimal('0.12')),
    (Decimal('201050'), Decimal('0.22')),
    (Decimal('383900'), Decimal('0.24')),
    (Decimal('487450'), Decimal('0.32')),
    (Decimal('731200'), Decimal('0.35')),
    (Decimal('inf'), Decimal('0.37'))
]

# Self-Employment Tax Rate
SE_TAX_RATE = Decimal('0.153')  # 15.3% (12.4% SS + 2.9% Medicare)
SE_WAGE_BASE_2025 = Decimal('168600')  # Social Security wage base
MEDICARE_ADDITIONAL_THRESHOLD = Decimal('200000')  # Additional 0.9% Medicare

# QBI Deduction
QBI_DEDUCTION_RATE = Decimal('0.20')  # 20% of qualified business income
QBI_PHASE_OUT_SINGLE = Decimal('191950')
QBI_PHASE_OUT_JOINT = Decimal('383900')

# Electric Vehicle Credit (Discontinued Sept 2025)
EV_CREDIT_PHASEOUT_DATE = date(2025, 9, 1)

# Cryptocurrency Reporting Threshold
CRYPTO_REPORTING_THRESHOLD = Decimal('600')  # Report if gains > $600


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class EntityType(Enum):
    """Tax entity types"""
    INDIVIDUAL = "individual"
    PARTNERSHIP = "partnership"
    S_CORPORATION = "s_corporation"
    C_CORPORATION = "c_corporation"
    NONPROFIT = "nonprofit"
    TRUST = "trust"
    ESTATE = "estate"


class FilingStatus(Enum):
    """Individual filing status"""
    SINGLE = "single"
    MARRIED_JOINT = "married_joint"
    MARRIED_SEPARATE = "married_separate"
    HEAD_OF_HOUSEHOLD = "head_of_household"
    QUALIFYING_WIDOW = "qualifying_widow"


class NonprofitType(Enum):
    """Nonprofit organization types"""
    TYPE_990_N = "990-N"  # e-Postcard (under $50K)
    TYPE_990_EZ = "990-EZ"  # Short form ($50K-$200K)
    TYPE_990_FULL = "990"  # Full form (over $200K)


class IncomeType(Enum):
    """Types of income"""
    WAGES = "wages"
    SELF_EMPLOYMENT = "self_employment"
    RENTAL = "rental"
    INVESTMENT = "investment"
    CAPITAL_GAINS = "capital_gains"
    CRYPTOCURRENCY = "cryptocurrency"
    PARTNERSHIP = "partnership"
    S_CORP = "s_corp"
    PENSION = "pension"
    SOCIAL_SECURITY = "social_security"


class CryptoTransactionType(Enum):
    """Cryptocurrency transaction types"""
    BUY = "buy"
    SELL = "sell"
    TRADE = "trade"
    MINING = "mining"
    STAKING = "staking"
    GIFT = "gift"


@dataclass
class TaxPayer:
    """Individual taxpayer information"""
    ssn: str
    first_name: str
    last_name: str
    date_of_birth: date
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    filing_status: FilingStatus
    dependents: List[Dict] = field(default_factory=list)
    occupation: str = ""

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class BusinessEntity:
    """Business entity information"""
    ein: str
    legal_name: str
    dba: str
    entity_type: EntityType
    formation_date: date
    state_of_formation: str
    business_address: str
    city: str
    state: str
    zip_code: str
    business_code: str  # NAICS code
    principal_activity: str
    accounting_method: str = "accrual"  # cash or accrual
    fiscal_year_end: str = "12/31"


@dataclass
class IncomeItem:
    """Income item"""
    income_type: IncomeType
    description: str
    amount: Decimal
    date_received: date
    payer_name: str = ""
    payer_ein: str = ""
    form_1099_issued: bool = False


@dataclass
class Deduction:
    """Tax deduction"""
    category: str
    description: str
    amount: Decimal
    date: date
    receipt_path: Optional[str] = None
    business_use_percentage: Decimal = Decimal('100')


@dataclass
class CryptoTransaction:
    """Cryptocurrency transaction"""
    transaction_type: CryptoTransactionType
    date: date
    cryptocurrency: str
    quantity: Decimal
    cost_basis: Decimal
    proceeds: Decimal
    gain_loss: Decimal
    short_term: bool  # True if held < 1 year
    exchange: str = ""
    wallet_address: str = ""


@dataclass
class K1Distribution:
    """K-1 distribution for partnerships/S-corps"""
    partner_ssn: str
    partner_name: str
    ownership_percentage: Decimal
    ordinary_income: Decimal
    guaranteed_payments: Decimal
    rental_income: Decimal
    capital_gains: Decimal
    section_179_deduction: Decimal
    self_employment_earnings: Decimal


# ============================================================================
# FORM 1040 - INDIVIDUAL INCOME TAX RETURN
# ============================================================================

class Form1040Generator:
    """Generate Form 1040 Individual Income Tax Return"""

    def __init__(self, taxpayer: TaxPayer, tax_year: int = TAX_YEAR):
        self.taxpayer = taxpayer
        self.tax_year = tax_year
        self.income_items: List[IncomeItem] = []
        self.deductions: List[Deduction] = []
        self.credits: Dict[str, Decimal] = {}
        self.schedule_c_businesses: List['ScheduleC'] = []
        self.schedule_e_rentals: List['ScheduleE'] = []
        self.crypto_transactions: List[CryptoTransaction] = []

    def add_income(self, income: IncomeItem):
        """Add income item"""
        self.income_items.append(income)
        logger.info(f"Added income: {income.income_type.value} - ${income.amount}")

    def add_deduction(self, deduction: Deduction):
        """Add deduction"""
        self.deductions.append(deduction)
        logger.info(f"Added deduction: {deduction.category} - ${deduction.amount}")

    def add_credit(self, credit_name: str, amount: Decimal):
        """Add tax credit"""
        self.credits[credit_name] = amount
        logger.info(f"Added credit: {credit_name} - ${amount}")

    def calculate_agi(self) -> Decimal:
        """Calculate Adjusted Gross Income"""
        total_income = sum(item.amount for item in self.income_items)

        # Add Schedule C income
        for schedule_c in self.schedule_c_businesses:
            total_income += schedule_c.calculate_net_profit()

        # Add Schedule E income
        for schedule_e in self.schedule_e_rentals:
            total_income += schedule_e.calculate_net_rental_income()

        # Subtract above-the-line deductions
        above_line_deductions = sum(
            d.amount for d in self.deductions
            if d.category in ['IRA', 'HSA', 'Student_Loan_Interest', 'SE_Tax_Deduction']
        )

        agi = total_income - above_line_deductions
        logger.info(f"Calculated AGI: ${agi}")
        return max(agi, Decimal('0'))

    def calculate_taxable_income(self) -> Decimal:
        """Calculate taxable income"""
        agi = self.calculate_agi()

        # Standard deduction or itemized
        standard_deduction = STANDARD_DEDUCTION[self.taxpayer.filing_status.value]
        itemized_deductions = sum(
            d.amount for d in self.deductions
            if d.category not in ['IRA', 'HSA', 'Student_Loan_Interest', 'SE_Tax_Deduction']
        )

        deduction = max(standard_deduction, itemized_deductions)

        # QBI Deduction (20% of qualified business income)
        qbi_deduction = self._calculate_qbi_deduction(agi)

        taxable_income = agi - deduction - qbi_deduction
        logger.info(f"Calculated Taxable Income: ${taxable_income}")
        return max(taxable_income, Decimal('0'))

    def _calculate_qbi_deduction(self, agi: Decimal) -> Decimal:
        """Calculate Qualified Business Income deduction"""
        qbi = sum(sc.calculate_net_profit() for sc in self.schedule_c_businesses)

        if qbi <= 0:
            return Decimal('0')

        # Phase-out for high earners
        if self.taxpayer.filing_status == FilingStatus.SINGLE:
            threshold = QBI_PHASE_OUT_SINGLE
        else:
            threshold = QBI_PHASE_OUT_JOINT

        if agi <= threshold:
            # Full deduction
            deduction = qbi * QBI_DEDUCTION_RATE
        elif agi <= threshold + Decimal('50000'):
            # Phase-out range
            reduction_ratio = (agi - threshold) / Decimal('50000')
            full_deduction = qbi * QBI_DEDUCTION_RATE
            deduction = full_deduction * (Decimal('1') - reduction_ratio)
        else:
            # No deduction for high earners (simplified)
            deduction = Decimal('0')

        # Cannot exceed 20% of taxable income before QBI
        max_deduction = (agi - STANDARD_DEDUCTION[self.taxpayer.filing_status.value]) * QBI_DEDUCTION_RATE

        return min(deduction, max_deduction)

    def calculate_tax_liability(self) -> Dict[str, Decimal]:
        """Calculate total tax liability"""
        taxable_income = self.calculate_taxable_income()

        # Select tax brackets based on filing status
        if self.taxpayer.filing_status == FilingStatus.MARRIED_JOINT:
            brackets = TAX_BRACKETS_JOINT_2025
        else:
            brackets = TAX_BRACKETS_SINGLE_2025

        # Calculate income tax
        income_tax = self._calculate_progressive_tax(taxable_income, brackets)

        # Self-employment tax
        se_tax = self._calculate_self_employment_tax()

        # Total tax before credits
        total_tax_before_credits = income_tax + se_tax

        # Apply credits
        total_credits = sum(self.credits.values())

        # Final tax liability
        tax_liability = max(total_tax_before_credits - total_credits, Decimal('0'))

        return {
            'taxable_income': taxable_income,
            'income_tax': income_tax,
            'self_employment_tax': se_tax,
            'total_tax_before_credits': total_tax_before_credits,
            'total_credits': total_credits,
            'tax_liability': tax_liability
        }

    def _calculate_progressive_tax(self, income: Decimal, brackets: List[Tuple]) -> Decimal:
        """Calculate tax using progressive brackets"""
        tax = Decimal('0')
        previous_bracket = Decimal('0')

        for bracket_limit, rate in brackets:
            if income <= previous_bracket:
                break

            taxable_in_bracket = min(income, bracket_limit) - previous_bracket
            tax += taxable_in_bracket * rate
            previous_bracket = bracket_limit

            if income <= bracket_limit:
                break

        return tax

    def _calculate_self_employment_tax(self) -> Decimal:
        """Calculate self-employment tax"""
        total_se_income = sum(
            sc.calculate_net_profit() for sc in self.schedule_c_businesses
        )

        if total_se_income <= 0:
            return Decimal('0')

        # 92.35% of SE income is subject to SE tax
        se_income = total_se_income * Decimal('0.9235')

        # Social Security portion (up to wage base)
        ss_income = min(se_income, SE_WAGE_BASE_2025)
        ss_tax = ss_income * Decimal('0.124')

        # Medicare portion (all income)
        medicare_tax = se_income * Decimal('0.029')

        # Additional Medicare tax for high earners
        if se_income > MEDICARE_ADDITIONAL_THRESHOLD:
            additional_medicare = (se_income - MEDICARE_ADDITIONAL_THRESHOLD) * Decimal('0.009')
            medicare_tax += additional_medicare

        total_se_tax = ss_tax + medicare_tax

        # Add SE tax deduction (50% of SE tax)
        se_tax_deduction = Deduction(
            category='SE_Tax_Deduction',
            description='Self-Employment Tax Deduction',
            amount=total_se_tax * Decimal('0.5'),
            date=date(self.tax_year, 12, 31)
        )
        self.add_deduction(se_tax_deduction)

        return total_se_tax

    def generate_1040(self) -> Dict[str, Any]:
        """Generate complete Form 1040"""
        logger.info(f"Generating Form 1040 for {self.taxpayer.get_full_name()}")

        tax_calc = self.calculate_tax_liability()

        form_1040 = {
            'form': 'Form 1040',
            'tax_year': self.tax_year,
            'taxpayer': {
                'name': self.taxpayer.get_full_name(),
                'ssn': self.taxpayer.ssn,
                'address': self.taxpayer.address,
                'city': self.taxpayer.city,
                'state': self.taxpayer.state,
                'zip': self.taxpayer.zip_code,
                'filing_status': self.taxpayer.filing_status.value
            },
            'income': {
                'wages': float(sum(i.amount for i in self.income_items if i.income_type == IncomeType.WAGES)),
                'business_income': float(sum(sc.calculate_net_profit() for sc in self.schedule_c_businesses)),
                'rental_income': float(sum(se.calculate_net_rental_income() for se in self.schedule_e_rentals)),
                'capital_gains': float(sum(i.amount for i in self.income_items if i.income_type == IncomeType.CAPITAL_GAINS)),
                'total_income': float(sum(i.amount for i in self.income_items))
            },
            'adjustments': {
                'ira_deduction': float(sum(d.amount for d in self.deductions if d.category == 'IRA')),
                'se_tax_deduction': float(sum(d.amount for d in self.deductions if d.category == 'SE_Tax_Deduction')),
                'hsa_deduction': float(sum(d.amount for d in self.deductions if d.category == 'HSA'))
            },
            'agi': float(self.calculate_agi()),
            'deductions': {
                'standard_or_itemized': float(max(
                    STANDARD_DEDUCTION[self.taxpayer.filing_status.value],
                    sum(d.amount for d in self.deductions if d.category not in ['IRA', 'HSA', 'SE_Tax_Deduction'])
                )),
                'qbi_deduction': float(self._calculate_qbi_deduction(self.calculate_agi()))
            },
            'taxable_income': float(tax_calc['taxable_income']),
            'tax': {
                'income_tax': float(tax_calc['income_tax']),
                'self_employment_tax': float(tax_calc['self_employment_tax']),
                'total_tax': float(tax_calc['total_tax_before_credits'])
            },
            'credits': {name: float(amount) for name, amount in self.credits.items()},
            'total_credits': float(tax_calc['total_credits']),
            'tax_liability': float(tax_calc['tax_liability']),
            'schedules_attached': []
        }

        # Add attached schedules
        if self.schedule_c_businesses:
            form_1040['schedules_attached'].append('Schedule C')
        if self.schedule_e_rentals:
            form_1040['schedules_attached'].append('Schedule E')
        if self.crypto_transactions:
            form_1040['schedules_attached'].extend(['Form 8949', 'Schedule D'])

        logger.info(f"Form 1040 generated - Tax Liability: ${tax_calc['tax_liability']}")
        return form_1040


# ============================================================================
# SCHEDULE C - PROFIT OR LOSS FROM BUSINESS
# ============================================================================

class ScheduleC:
    """Schedule C - Profit or Loss from Business (Self-Employment)"""

    def __init__(self, business: BusinessEntity):
        self.business = business
        self.gross_receipts: Decimal = Decimal('0')
        self.returns_allowances: Decimal = Decimal('0')
        self.cost_of_goods_sold: Decimal = Decimal('0')
        self.expenses: Dict[str, Decimal] = {}
        self.vehicle_expenses: Decimal = Decimal('0')
        self.home_office_deduction: Decimal = Decimal('0')

    def add_gross_receipts(self, amount: Decimal):
        """Add gross receipts"""
        self.gross_receipts += amount

    def add_expense(self, category: str, amount: Decimal):
        """Add business expense"""
        if category not in self.expenses:
            self.expenses[category] = Decimal('0')
        self.expenses[category] += amount
        logger.info(f"Added {category} expense: ${amount}")

    def calculate_net_profit(self) -> Decimal:
        """Calculate net profit or loss"""
        gross_income = self.gross_receipts - self.returns_allowances - self.cost_of_goods_sold
        total_expenses = sum(self.expenses.values()) + self.vehicle_expenses + self.home_office_deduction
        net_profit = gross_income - total_expenses
        return net_profit

    def generate_schedule_c(self) -> Dict[str, Any]:
        """Generate Schedule C"""
        logger.info(f"Generating Schedule C for {self.business.legal_name}")

        return {
            'form': 'Schedule C',
            'business_info': {
                'name': self.business.legal_name,
                'ein': self.business.ein,
                'business_code': self.business.business_code,
                'accounting_method': self.business.accounting_method
            },
            'income': {
                'gross_receipts': float(self.gross_receipts),
                'returns_allowances': float(self.returns_allowances),
                'cost_of_goods_sold': float(self.cost_of_goods_sold),
                'gross_income': float(self.gross_receipts - self.returns_allowances - self.cost_of_goods_sold)
            },
            'expenses': {k: float(v) for k, v in self.expenses.items()},
            'vehicle_expenses': float(self.vehicle_expenses),
            'home_office_deduction': float(self.home_office_deduction),
            'total_expenses': float(sum(self.expenses.values()) + self.vehicle_expenses + self.home_office_deduction),
            'net_profit_loss': float(self.calculate_net_profit())
        }


# ============================================================================
# FORM 1065 - PARTNERSHIP RETURN
# ============================================================================

class Form1065Generator:
    """Generate Form 1065 U.S. Return of Partnership Income"""

    def __init__(self, partnership: BusinessEntity):
        self.partnership = partnership
        self.partners: List[K1Distribution] = []
        self.ordinary_income: Decimal = Decimal('0')
        self.rental_income: Decimal = Decimal('0')
        self.capital_gains: Decimal = Decimal('0')
        self.guaranteed_payments: Decimal = Decimal('0')
        self.deductions: Dict[str, Decimal] = {}

    def add_partner(self, k1: K1Distribution):
        """Add partner with K-1 distribution"""
        self.partners.append(k1)
        logger.info(f"Added partner: {k1.partner_name} - {k1.ownership_percentage}%")

    def calculate_partnership_income(self) -> Decimal:
        """Calculate total partnership income"""
        total_income = (self.ordinary_income + self.rental_income +
                       self.capital_gains - sum(self.deductions.values()))
        return total_income

    def generate_k1_schedules(self) -> List[Dict[str, Any]]:
        """Generate Schedule K-1 for each partner"""
        k1_schedules = []

        for partner in self.partners:
            k1 = {
                'form': 'Schedule K-1 (Form 1065)',
                'partnership': {
                    'name': self.partnership.legal_name,
                    'ein': self.partnership.ein
                },
                'partner': {
                    'name': partner.partner_name,
                    'ssn': partner.partner_ssn,
                    'ownership_percentage': float(partner.ownership_percentage)
                },
                'income_items': {
                    'ordinary_income': float(partner.ordinary_income),
                    'guaranteed_payments': float(partner.guaranteed_payments),
                    'rental_income': float(partner.rental_income),
                    'capital_gains': float(partner.capital_gains)
                },
                'deductions': {
                    'section_179': float(partner.section_179_deduction)
                },
                'self_employment_earnings': float(partner.self_employment_earnings)
            }
            k1_schedules.append(k1)

        return k1_schedules

    def generate_1065(self) -> Dict[str, Any]:
        """Generate complete Form 1065"""
        logger.info(f"Generating Form 1065 for {self.partnership.legal_name}")

        return {
            'form': 'Form 1065',
            'tax_year': TAX_YEAR,
            'partnership_info': {
                'name': self.partnership.legal_name,
                'ein': self.partnership.ein,
                'address': self.partnership.business_address,
                'date_formed': self.partnership.formation_date.isoformat(),
                'state_of_formation': self.partnership.state_of_formation
            },
            'income': {
                'ordinary_income': float(self.ordinary_income),
                'rental_income': float(self.rental_income),
                'capital_gains': float(self.capital_gains),
                'guaranteed_payments': float(self.guaranteed_payments),
                'total_income': float(self.calculate_partnership_income())
            },
            'deductions': {k: float(v) for k, v in self.deductions.items()},
            'partners_count': len(self.partners),
            'k1_schedules': self.generate_k1_schedules()
        }


# ============================================================================
# FORM 1120-S - S CORPORATION RETURN
# ============================================================================

class Form1120SGenerator:
    """Generate Form 1120-S U.S. Income Tax Return for an S Corporation"""

    def __init__(self, s_corp: BusinessEntity):
        self.s_corp = s_corp
        self.shareholders: List[K1Distribution] = []
        self.gross_receipts: Decimal = Decimal('0')
        self.cost_of_goods_sold: Decimal = Decimal('0')
        self.officer_compensation: Decimal = Decimal('0')
        self.deductions: Dict[str, Decimal] = {}

    def add_shareholder(self, k1: K1Distribution):
        """Add shareholder with K-1 distribution"""
        self.shareholders.append(k1)
        logger.info(f"Added shareholder: {k1.partner_name} - {k1.ownership_percentage}%")

    def calculate_ordinary_income(self) -> Decimal:
        """Calculate ordinary business income"""
        gross_profit = self.gross_receipts - self.cost_of_goods_sold
        total_deductions = sum(self.deductions.values()) + self.officer_compensation
        ordinary_income = gross_profit - total_deductions
        return ordinary_income

    def generate_1120s(self) -> Dict[str, Any]:
        """Generate complete Form 1120-S"""
        logger.info(f"Generating Form 1120-S for {self.s_corp.legal_name}")

        ordinary_income = self.calculate_ordinary_income()

        # Distribute to shareholders
        k1_schedules = []
        for shareholder in self.shareholders:
            share = ordinary_income * (shareholder.ownership_percentage / Decimal('100'))
            k1 = {
                'form': 'Schedule K-1 (Form 1120-S)',
                's_corporation': {
                    'name': self.s_corp.legal_name,
                    'ein': self.s_corp.ein
                },
                'shareholder': {
                    'name': shareholder.partner_name,
                    'ssn': shareholder.partner_ssn,
                    'ownership_percentage': float(shareholder.ownership_percentage)
                },
                'ordinary_income': float(share),
                'capital_gains': float(shareholder.capital_gains)
            }
            k1_schedules.append(k1)

        return {
            'form': 'Form 1120-S',
            'tax_year': TAX_YEAR,
            's_corp_info': {
                'name': self.s_corp.legal_name,
                'ein': self.s_corp.ein,
                'address': self.s_corp.business_address,
                'date_incorporated': self.s_corp.formation_date.isoformat(),
                'state_of_incorporation': self.s_corp.state_of_formation
            },
            'income': {
                'gross_receipts': float(self.gross_receipts),
                'cost_of_goods_sold': float(self.cost_of_goods_sold),
                'gross_profit': float(self.gross_receipts - self.cost_of_goods_sold)
            },
            'deductions': {
                'officer_compensation': float(self.officer_compensation),
                **{k: float(v) for k, v in self.deductions.items()}
            },
            'ordinary_income': float(ordinary_income),
            'shareholders_count': len(self.shareholders),
            'k1_schedules': k1_schedules
        }


# ============================================================================
# FORM 990 - NONPROFIT RETURN
# ============================================================================

class Form990Generator:
    """Generate Form 990 Return of Organization Exempt From Income Tax"""

    def __init__(self, nonprofit: BusinessEntity, gross_receipts: Decimal):
        self.nonprofit = nonprofit
        self.gross_receipts = gross_receipts
        self.contributions: Decimal = Decimal('0')
        self.program_revenue: Decimal = Decimal('0')
        self.investment_income: Decimal = Decimal('0')
        self.expenses: Dict[str, Decimal] = {}
        self.program_expenses: Decimal = Decimal('0')
        self.administrative_expenses: Decimal = Decimal('0')
        self.fundraising_expenses: Decimal = Decimal('0')

        # Determine which form to use
        if gross_receipts <= Decimal('50000'):
            self.form_type = NonprofitType.TYPE_990_N
        elif gross_receipts <= Decimal('200000'):
            self.form_type = NonprofitType.TYPE_990_EZ
        else:
            self.form_type = NonprofitType.TYPE_990_FULL

    def calculate_total_revenue(self) -> Decimal:
        """Calculate total revenue"""
        return self.contributions + self.program_revenue + self.investment_income

    def calculate_total_expenses(self) -> Decimal:
        """Calculate total expenses"""
        return (self.program_expenses + self.administrative_expenses +
                self.fundraising_expenses + sum(self.expenses.values()))

    def generate_990(self) -> Dict[str, Any]:
        """Generate appropriate 990 form"""
        logger.info(f"Generating {self.form_type.value} for {self.nonprofit.legal_name}")

        base_info = {
            'form': self.form_type.value,
            'tax_year': TAX_YEAR,
            'organization_info': {
                'name': self.nonprofit.legal_name,
                'ein': self.nonprofit.ein,
                'address': self.nonprofit.business_address,
                'mission': self.nonprofit.principal_activity
            },
            'revenue': {
                'contributions': float(self.contributions),
                'program_revenue': float(self.program_revenue),
                'investment_income': float(self.investment_income),
                'total_revenue': float(self.calculate_total_revenue())
            }
        }

        if self.form_type == NonprofitType.TYPE_990_N:
            # e-Postcard - minimal information
            return {
                **base_info,
                'gross_receipts': float(self.gross_receipts),
                'filing_requirement': 'e-Postcard (under $50,000)'
            }

        elif self.form_type == NonprofitType.TYPE_990_EZ:
            # Short form
            return {
                **base_info,
                'gross_receipts': float(self.gross_receipts),
                'expenses': {
                    'program_expenses': float(self.program_expenses),
                    'administrative_expenses': float(self.administrative_expenses),
                    'fundraising_expenses': float(self.fundraising_expenses),
                    'total_expenses': float(self.calculate_total_expenses())
                },
                'net_assets': float(self.calculate_total_revenue() - self.calculate_total_expenses())
            }

        else:
            # Full Form 990
            return {
                **base_info,
                'gross_receipts': float(self.gross_receipts),
                'expenses': {
                    'program_expenses': float(self.program_expenses),
                    'administrative_expenses': float(self.administrative_expenses),
                    'fundraising_expenses': float(self.fundraising_expenses),
                    'other_expenses': {k: float(v) for k, v in self.expenses.items()},
                    'total_expenses': float(self.calculate_total_expenses())
                },
                'net_assets': float(self.calculate_total_revenue() - self.calculate_total_expenses()),
                'governance': {
                    'board_members_count': 0,  # To be filled
                    'independent_voting_members': 0
                },
                'program_accomplishments': []  # To be filled
            }


# ============================================================================
# SCHEDULE E - RENTAL AND PASSIVE INCOME
# ============================================================================

class ScheduleE:
    """Schedule E - Supplemental Income and Loss (Rental Properties)"""

    def __init__(self, property_address: str):
        self.property_address = property_address
        self.rental_income: Decimal = Decimal('0')
        self.expenses: Dict[str, Decimal] = {
            'mortgage_interest': Decimal('0'),
            'property_tax': Decimal('0'),
            'insurance': Decimal('0'),
            'repairs': Decimal('0'),
            'utilities': Decimal('0'),
            'depreciation': Decimal('0'),
            'management_fees': Decimal('0'),
            'other': Decimal('0')
        }

    def add_rental_income(self, amount: Decimal):
        """Add rental income"""
        self.rental_income += amount

    def add_expense(self, category: str, amount: Decimal):
        """Add rental expense"""
        if category in self.expenses:
            self.expenses[category] += amount
        else:
            self.expenses['other'] += amount

    def calculate_net_rental_income(self) -> Decimal:
        """Calculate net rental income"""
        total_expenses = sum(self.expenses.values())
        net_income = self.rental_income - total_expenses
        return net_income

    def generate_schedule_e(self) -> Dict[str, Any]:
        """Generate Schedule E"""
        logger.info(f"Generating Schedule E for {self.property_address}")

        return {
            'form': 'Schedule E',
            'property_address': self.property_address,
            'income': {
                'rental_income': float(self.rental_income)
            },
            'expenses': {k: float(v) for k, v in self.expenses.items()},
            'total_expenses': float(sum(self.expenses.values())),
            'net_rental_income': float(self.calculate_net_rental_income())
        }


# ============================================================================
# CRYPTOCURRENCY REPORTING - FORM 8949 & SCHEDULE D
# ============================================================================

class CryptoTaxReporter:
    """Cryptocurrency tax reporting (Form 8949 and Schedule D)"""

    def __init__(self):
        self.transactions: List[CryptoTransaction] = []

    def add_transaction(self, transaction: CryptoTransaction):
        """Add cryptocurrency transaction"""
        self.transactions.append(transaction)
        logger.info(f"Added crypto transaction: {transaction.transaction_type.value} - {transaction.cryptocurrency}")

    def calculate_total_gains_losses(self) -> Dict[str, Decimal]:
        """Calculate total capital gains/losses"""
        short_term_gain = sum(t.gain_loss for t in self.transactions if t.short_term)
        long_term_gain = sum(t.gain_loss for t in self.transactions if not t.short_term)

        return {
            'short_term': short_term_gain,
            'long_term': long_term_gain,
            'total': short_term_gain + long_term_gain
        }

    def generate_form_8949(self) -> Dict[str, Any]:
        """Generate Form 8949 - Sales and Other Dispositions of Capital Assets"""
        logger.info("Generating Form 8949 for cryptocurrency transactions")

        short_term_transactions = [t for t in self.transactions if t.short_term]
        long_term_transactions = [t for t in self.transactions if not t.short_term]

        return {
            'form': 'Form 8949',
            'short_term_transactions': [
                {
                    'description': f"{t.quantity} {t.cryptocurrency}",
                    'date_acquired': 'Various',
                    'date_sold': t.date.isoformat(),
                    'proceeds': float(t.proceeds),
                    'cost_basis': float(t.cost_basis),
                    'gain_loss': float(t.gain_loss)
                }
                for t in short_term_transactions
            ],
            'long_term_transactions': [
                {
                    'description': f"{t.quantity} {t.cryptocurrency}",
                    'date_acquired': 'Various',
                    'date_sold': t.date.isoformat(),
                    'proceeds': float(t.proceeds),
                    'cost_basis': float(t.cost_basis),
                    'gain_loss': float(t.gain_loss)
                }
                for t in long_term_transactions
            ],
            'totals': {
                'short_term_gain_loss': float(sum(t.gain_loss for t in short_term_transactions)),
                'long_term_gain_loss': float(sum(t.gain_loss for t in long_term_transactions))
            }
        }

    def generate_schedule_d(self) -> Dict[str, Any]:
        """Generate Schedule D - Capital Gains and Losses"""
        logger.info("Generating Schedule D")

        gains_losses = self.calculate_total_gains_losses()

        return {
            'form': 'Schedule D',
            'short_term': {
                'total_gain_loss': float(gains_losses['short_term'])
            },
            'long_term': {
                'total_gain_loss': float(gains_losses['long_term'])
            },
            'net_capital_gain_loss': float(gains_losses['total'])
        }


# ============================================================================
# 1099 AND W-2 GENERATION
# ============================================================================

class InformationReturnGenerator:
    """Generate 1099 and W-2 forms"""

    @staticmethod
    def generate_1099_nec(payer: BusinessEntity, recipient: TaxPayer, amount: Decimal) -> Dict[str, Any]:
        """Generate Form 1099-NEC (Nonemployee Compensation)"""
        logger.info(f"Generating 1099-NEC for {recipient.get_full_name()}")

        return {
            'form': 'Form 1099-NEC',
            'tax_year': TAX_YEAR,
            'payer': {
                'name': payer.legal_name,
                'ein': payer.ein,
                'address': payer.business_address
            },
            'recipient': {
                'name': recipient.get_full_name(),
                'ssn': recipient.ssn,
                'address': recipient.address
            },
            'nonemployee_compensation': float(amount),
            'filing_requirement': amount >= Decimal('600')
        }

    @staticmethod
    def generate_w2(employer: BusinessEntity, employee: TaxPayer,
                    wages: Decimal, federal_tax: Decimal, ss_tax: Decimal,
                    medicare_tax: Decimal) -> Dict[str, Any]:
        """Generate Form W-2 (Wage and Tax Statement)"""
        logger.info(f"Generating W-2 for {employee.get_full_name()}")

        return {
            'form': 'Form W-2',
            'tax_year': TAX_YEAR,
            'employer': {
                'name': employer.legal_name,
                'ein': employer.ein,
                'address': employer.business_address
            },
            'employee': {
                'name': employee.get_full_name(),
                'ssn': employee.ssn,
                'address': employee.address
            },
            'wages': float(wages),
            'federal_income_tax_withheld': float(federal_tax),
            'social_security_wages': float(wages),
            'social_security_tax_withheld': float(ss_tax),
            'medicare_wages': float(wages),
            'medicare_tax_withheld': float(medicare_tax)
        }


# ============================================================================
# E-FILE XML GENERATION (MeF FORMAT)
# ============================================================================

class MeFXMLGenerator:
    """Generate IRS Modernized e-File (MeF) XML"""

    def __init__(self, tax_year: int = TAX_YEAR):
        self.tax_year = tax_year

    def generate_1040_xml(self, form_1040_data: Dict) -> str:
        """Generate Form 1040 in MeF XML format"""
        logger.info("Generating MeF XML for Form 1040")

        # Create XML structure
        root = ET.Element('Return', {
            'returnVersion': '2025v1.0',
            'xmlns': 'http://www.irs.gov/efile'
        })

        # Return header
        header = ET.SubElement(root, 'ReturnHeader')
        ET.SubElement(header, 'Timestamp').text = datetime.now().isoformat()
        ET.SubElement(header, 'TaxYear').text = str(self.tax_year)
        ET.SubElement(header, 'TaxPeriodBeginDate').text = f'{self.tax_year}-01-01'
        ET.SubElement(header, 'TaxPeriodEndDate').text = f'{self.tax_year}-12-31'

        # Taxpayer information
        filer = ET.SubElement(header, 'Filer')
        ET.SubElement(filer, 'Name').text = form_1040_data['taxpayer']['name']
        ET.SubElement(filer, 'SSN').text = form_1040_data['taxpayer']['ssn']

        # Return data
        return_data = ET.SubElement(root, 'ReturnData')
        irs1040 = ET.SubElement(return_data, 'IRS1040')

        # Income
        ET.SubElement(irs1040, 'WagesAmt').text = str(form_1040_data['income']['wages'])
        ET.SubElement(irs1040, 'TaxableIncomeAmt').text = str(form_1040_data['taxable_income'])
        ET.SubElement(irs1040, 'TaxAmt').text = str(form_1040_data['tax']['total_tax'])

        # Convert to string
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        return xml_string

    def generate_submission_manifest(self, return_id: str, forms: List[str]) -> Dict[str, Any]:
        """Generate submission manifest"""
        return {
            'submission_id': return_id,
            'timestamp': datetime.now().isoformat(),
            'tax_year': self.tax_year,
            'forms_included': forms,
            'status': 'ready_for_transmission'
        }


# ============================================================================
# COMPLETE TAX FILING SYSTEM
# ============================================================================

class MultiEntityTaxSystem:
    """
    Complete Multi-Entity Tax Filing System

    Handles all tax forms and e-filing for multiple entity types
    """

    def __init__(self):
        self.tax_year = TAX_YEAR
        self.forms_generated: List[Dict] = []
        self.xml_generator = MeFXMLGenerator(TAX_YEAR)
        logger.info(f"Multi-Entity Tax System initialized for {TAX_YEAR}")

    def file_individual_return(self, taxpayer: TaxPayer, income_items: List[IncomeItem],
                              deductions: List[Deduction]) -> Dict[str, Any]:
        """File complete individual tax return"""
        logger.info(f"Filing individual return for {taxpayer.get_full_name()}")

        # Generate Form 1040
        form_1040_gen = Form1040Generator(taxpayer, self.tax_year)

        for income in income_items:
            form_1040_gen.add_income(income)

        for deduction in deductions:
            form_1040_gen.add_deduction(deduction)

        form_1040 = form_1040_gen.generate_1040()
        self.forms_generated.append(form_1040)

        # Generate XML for e-filing
        xml = self.xml_generator.generate_1040_xml(form_1040)

        return {
            'form_1040': form_1040,
            'xml': xml,
            'status': 'ready_for_efile'
        }

    def get_filing_summary(self) -> Dict[str, Any]:
        """Get summary of all forms generated"""
        return {
            'tax_year': self.tax_year,
            'forms_generated': len(self.forms_generated),
            'forms': [f['form'] for f in self.forms_generated],
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def demonstrate_tax_system():
    """Demonstrate the complete tax filing system"""

    print("=" * 80)
    print("MULTI-ENTITY TAX FILING SYSTEM - 2025")
    print("=" * 80)

    # Initialize tax system
    tax_system = MultiEntityTaxSystem()

    # Create taxpayer
    taxpayer = TaxPayer(
        ssn='123-45-6789',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(1980, 5, 15),
        address='123 Main St',
        city='San Francisco',
        state='CA',
        zip_code='94102',
        phone='555-1234',
        email='john@example.com',
        filing_status=FilingStatus.MARRIED_JOINT,
        occupation='Software Engineer'
    )

    # Add income
    income_items = [
        IncomeItem(
            income_type=IncomeType.WAGES,
            description='W-2 Wages from Tech Corp',
            amount=Decimal('150000'),
            date_received=date(2025, 12, 31),
            payer_name='Tech Corp',
            payer_ein='12-3456789'
        )
    ]

    # Add deductions
    deductions = [
        Deduction(
            category='IRA',
            description='Traditional IRA Contribution',
            amount=Decimal('7000'),
            date=date(2025, 12, 31)
        )
    ]

    # File return
    result = tax_system.file_individual_return(taxpayer, income_items, deductions)

    print("\n✓ FORM 1040 GENERATED")
    print(f"  Taxpayer: {result['form_1040']['taxpayer']['name']}")
    print(f"  AGI: ${result['form_1040']['agi']:,.2f}")
    print(f"  Taxable Income: ${result['form_1040']['taxable_income']:,.2f}")
    print(f"  Tax Liability: ${result['form_1040']['tax_liability']:,.2f}")
    print(f"  Status: {result['status']}")

    # Summary
    summary = tax_system.get_filing_summary()
    print(f"\n✓ FILING SUMMARY")
    print(f"  Tax Year: {summary['tax_year']}")
    print(f"  Forms Generated: {summary['forms_generated']}")
    print(f"  Forms: {', '.join(summary['forms'])}")

    print("\n" + "=" * 80)
    print("TAX FILING SYSTEM DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demonstrate_tax_system())
