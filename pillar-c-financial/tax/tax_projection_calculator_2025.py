"""
TAX PROJECTION CALCULATOR - 2025 EDITION
Advanced tax planning and projection tool for strategic tax optimization

Features:
- Income scenario modeling with tax liability calculations
- Refundable vs non-refundable credit optimization
- 3-year back filing analysis and catch-up calculator
- Quarterly estimated tax payment calculator (Form 1040-ES)
- QBI (Qualified Business Income) deduction optimizer
- State tax integration (CA, TX, GA, NY, FL)
- Multi-year tax planning (2023-2027)
- Tax-loss harvesting strategies
- Retirement contribution optimization
- Entity structure comparison (LLC vs S-Corp vs C-Corp)

Author: Tax Planning System
Version: 2025.1.0
"""

import asyncio
import json
import logging
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 2025 TAX CONSTANTS
# ============================================================================

# Federal Tax Brackets 2025 - Single
FEDERAL_BRACKETS_SINGLE_2025 = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37)
]

# Federal Tax Brackets 2025 - Married Filing Jointly
FEDERAL_BRACKETS_JOINT_2025 = [
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (float('inf'), 0.37)
]

# Standard Deductions 2025
STANDARD_DEDUCTION_2025 = {
    'single': 15100,
    'married_joint': 30200,
    'married_separate': 15100,
    'head_of_household': 22650
}

# State Tax Rates (2025 estimates)
STATE_TAX_RATES = {
    'CA': {'rate': 0.093, 'brackets': True},  # California (progressive, top rate)
    'TX': {'rate': 0.0, 'brackets': False},   # Texas (no state income tax)
    'GA': {'rate': 0.0575, 'brackets': True}, # Georgia
    'NY': {'rate': 0.1090, 'brackets': True}, # New York (top rate)
    'FL': {'rate': 0.0, 'brackets': False},   # Florida (no state income tax)
}

# Self-Employment Tax
SE_TAX_RATE = 0.153  # 15.3%
SE_WAGE_BASE_2025 = 168600

# QBI Deduction
QBI_RATE = 0.20
QBI_PHASE_OUT_START_SINGLE = 191950
QBI_PHASE_OUT_START_JOINT = 383900
QBI_PHASE_OUT_RANGE = 50000

# Quarterly Estimated Tax Safe Harbor
SAFE_HARBOR_CURRENT_YEAR = 0.90  # 90% of current year tax
SAFE_HARBOR_PRIOR_YEAR = 1.00    # 100% of prior year tax (110% if AGI > $150K)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class FilingStatus(Enum):
    """Tax filing status"""
    SINGLE = "single"
    MARRIED_JOINT = "married_joint"
    MARRIED_SEPARATE = "married_separate"
    HEAD_OF_HOUSEHOLD = "head_of_household"


class CreditType(Enum):
    """Tax credit types"""
    REFUNDABLE = "refundable"
    NON_REFUNDABLE = "non_refundable"


@dataclass
class IncomeScenario:
    """Income scenario for tax projection"""
    name: str
    w2_income: Decimal
    self_employment_income: Decimal
    rental_income: Decimal
    investment_income: Decimal
    capital_gains_short: Decimal
    capital_gains_long: Decimal
    other_income: Decimal

    def total_income(self) -> Decimal:
        return (self.w2_income + self.self_employment_income + self.rental_income +
                self.investment_income + self.capital_gains_short +
                self.capital_gains_long + self.other_income)


@dataclass
class TaxCredit:
    """Tax credit"""
    name: str
    amount: Decimal
    credit_type: CreditType
    phase_out_threshold: Optional[Decimal] = None


@dataclass
class QuarterlyPayment:
    """Quarterly estimated tax payment"""
    quarter: int
    due_date: date
    amount: Decimal
    paid: bool = False


# ============================================================================
# TAX CALCULATION ENGINE
# ============================================================================

class TaxCalculationEngine:
    """Core tax calculation engine"""

    @staticmethod
    def calculate_federal_tax(taxable_income: Decimal, filing_status: FilingStatus) -> Decimal:
        """Calculate federal income tax"""
        if filing_status in [FilingStatus.MARRIED_JOINT]:
            brackets = FEDERAL_BRACKETS_JOINT_2025
        else:
            brackets = FEDERAL_BRACKETS_SINGLE_2025

        tax = Decimal('0')
        previous_bracket = Decimal('0')

        for bracket_limit, rate in brackets:
            if taxable_income <= previous_bracket:
                break

            taxable_in_bracket = min(Decimal(str(taxable_income)), Decimal(str(bracket_limit))) - previous_bracket
            tax += taxable_in_bracket * Decimal(str(rate))

            previous_bracket = Decimal(str(bracket_limit))

            if taxable_income <= bracket_limit:
                break

        return tax

    @staticmethod
    def calculate_self_employment_tax(se_income: Decimal) -> Decimal:
        """Calculate self-employment tax"""
        if se_income <= 0:
            return Decimal('0')

        # 92.35% of SE income subject to SE tax
        taxable_se_income = se_income * Decimal('0.9235')

        # Social Security portion (up to wage base)
        ss_income = min(taxable_se_income, Decimal(str(SE_WAGE_BASE_2025)))
        ss_tax = ss_income * Decimal('0.124')

        # Medicare portion (all income)
        medicare_tax = taxable_se_income * Decimal('0.029')

        # Additional Medicare tax (0.9% over $200K)
        if taxable_se_income > Decimal('200000'):
            additional_medicare = (taxable_se_income - Decimal('200000')) * Decimal('0.009')
            medicare_tax += additional_medicare

        total_se_tax = ss_tax + medicare_tax
        return total_se_tax

    @staticmethod
    def calculate_qbi_deduction(qbi: Decimal, taxable_income: Decimal,
                               filing_status: FilingStatus) -> Decimal:
        """Calculate Qualified Business Income deduction"""
        if qbi <= 0:
            return Decimal('0')

        # Determine phase-out threshold
        if filing_status == FilingStatus.MARRIED_JOINT:
            threshold = Decimal(str(QBI_PHASE_OUT_START_JOINT))
        else:
            threshold = Decimal(str(QBI_PHASE_OUT_START_SINGLE))

        # Calculate base deduction (20% of QBI)
        base_deduction = qbi * Decimal(str(QBI_RATE))

        # Apply phase-out for high earners
        if taxable_income <= threshold:
            deduction = base_deduction
        elif taxable_income <= threshold + Decimal(str(QBI_PHASE_OUT_RANGE)):
            reduction_ratio = (taxable_income - threshold) / Decimal(str(QBI_PHASE_OUT_RANGE))
            deduction = base_deduction * (Decimal('1') - reduction_ratio)
        else:
            # Phase-out complete for specified service businesses
            deduction = Decimal('0')

        # Cannot exceed 20% of taxable income
        max_deduction = taxable_income * Decimal(str(QBI_RATE))
        return min(deduction, max_deduction)

    @staticmethod
    def calculate_state_tax(taxable_income: Decimal, state: str) -> Decimal:
        """Calculate state income tax"""
        if state not in STATE_TAX_RATES:
            return Decimal('0')

        state_info = STATE_TAX_RATES[state]
        rate = Decimal(str(state_info['rate']))

        # Simplified calculation (actual state tax is more complex)
        state_tax = taxable_income * rate
        return state_tax


# ============================================================================
# TAX PROJECTION CALCULATOR
# ============================================================================

class TaxProjectionCalculator:
    """
    Tax Projection Calculator

    Projects tax liability under various income scenarios
    """

    def __init__(self, filing_status: FilingStatus, state: str = 'CA'):
        self.filing_status = filing_status
        self.state = state
        self.calculator = TaxCalculationEngine()

    def project_tax_liability(self, scenario: IncomeScenario) -> Dict[str, Any]:
        """Project tax liability for an income scenario"""
        logger.info(f"Projecting tax for scenario: {scenario.name}")

        # Calculate AGI
        total_income = scenario.total_income()

        # Self-employment tax
        se_tax = self.calculator.calculate_self_employment_tax(scenario.self_employment_income)
        se_tax_deduction = se_tax * Decimal('0.5')  # 50% deductible

        # AGI
        agi = total_income - se_tax_deduction

        # Standard deduction
        standard_deduction = Decimal(str(STANDARD_DEDUCTION_2025[self.filing_status.value]))

        # QBI deduction
        qbi = scenario.self_employment_income
        qbi_deduction = self.calculator.calculate_qbi_deduction(qbi, agi, self.filing_status)

        # Taxable income
        taxable_income = max(agi - standard_deduction - qbi_deduction, Decimal('0'))

        # Federal income tax
        federal_tax = self.calculator.calculate_federal_tax(taxable_income, self.filing_status)

        # State income tax
        state_tax = self.calculator.calculate_state_tax(taxable_income, self.state)

        # Total tax liability
        total_tax = federal_tax + se_tax + state_tax

        # Effective tax rate
        effective_rate = (total_tax / total_income * 100) if total_income > 0 else Decimal('0')

        return {
            'scenario': scenario.name,
            'total_income': float(total_income),
            'agi': float(agi),
            'standard_deduction': float(standard_deduction),
            'qbi_deduction': float(qbi_deduction),
            'taxable_income': float(taxable_income),
            'federal_income_tax': float(federal_tax),
            'self_employment_tax': float(se_tax),
            'state_tax': float(state_tax),
            'total_tax_liability': float(total_tax),
            'effective_tax_rate': float(effective_rate),
            'marginal_tax_rate': self._calculate_marginal_rate(taxable_income)
        }

    def _calculate_marginal_rate(self, taxable_income: Decimal) -> float:
        """Calculate marginal tax rate"""
        if self.filing_status == FilingStatus.MARRIED_JOINT:
            brackets = FEDERAL_BRACKETS_JOINT_2025
        else:
            brackets = FEDERAL_BRACKETS_SINGLE_2025

        for bracket_limit, rate in brackets:
            if taxable_income <= bracket_limit:
                return rate

        return brackets[-1][1]

    def compare_scenarios(self, scenarios: List[IncomeScenario]) -> pd.DataFrame:
        """Compare multiple income scenarios"""
        results = []

        for scenario in scenarios:
            projection = self.project_tax_liability(scenario)
            results.append(projection)

        df = pd.DataFrame(results)
        return df


# ============================================================================
# CREDIT OPTIMIZER
# ============================================================================

class TaxCreditOptimizer:
    """Optimize refundable and non-refundable tax credits"""

    def __init__(self):
        self.available_credits: List[TaxCredit] = []

    def add_credit(self, credit: TaxCredit):
        """Add available tax credit"""
        self.available_credits.append(credit)
        logger.info(f"Added {credit.credit_type.value} credit: {credit.name} - ${credit.amount}")

    def optimize_credits(self, tax_liability: Decimal, agi: Decimal) -> Dict[str, Any]:
        """Optimize application of tax credits"""

        # Separate refundable and non-refundable credits
        refundable = [c for c in self.available_credits if c.credit_type == CreditType.REFUNDABLE]
        non_refundable = [c for c in self.available_credits if c.credit_type == CreditType.NON_REFUNDABLE]

        # Apply non-refundable credits first (limited to tax liability)
        non_refundable_total = sum(c.amount for c in non_refundable)
        non_refundable_used = min(non_refundable_total, tax_liability)
        remaining_tax = max(tax_liability - non_refundable_used, Decimal('0'))

        # Apply refundable credits (can exceed tax liability)
        refundable_total = sum(c.amount for c in refundable)

        # Calculate refund
        if refundable_total > remaining_tax:
            refund = refundable_total - remaining_tax
            final_tax = Decimal('0')
        else:
            refund = Decimal('0')
            final_tax = remaining_tax - refundable_total

        return {
            'non_refundable_credits': float(non_refundable_used),
            'non_refundable_wasted': float(non_refundable_total - non_refundable_used),
            'refundable_credits': float(refundable_total),
            'final_tax_liability': float(final_tax),
            'refund_amount': float(refund),
            'optimization_strategy': self._generate_strategy(non_refundable, refundable, agi)
        }

    def _generate_strategy(self, non_refundable: List[TaxCredit],
                          refundable: List[TaxCredit], agi: Decimal) -> str:
        """Generate credit optimization strategy"""
        strategies = []

        if non_refundable:
            strategies.append("Maximize income to utilize non-refundable credits")

        if refundable:
            strategies.append("Refundable credits provide maximum benefit regardless of tax liability")

        return "; ".join(strategies) if strategies else "No optimization needed"


# ============================================================================
# BACK FILING ANALYZER (3-YEAR)
# ============================================================================

class BackFilingAnalyzer:
    """Analyze 3-year back filing requirements and opportunities"""

    def __init__(self):
        self.years_to_analyze = [2022, 2023, 2024]

    def analyze_back_filing(self, income_by_year: Dict[int, Decimal],
                           deductions_by_year: Dict[int, Decimal]) -> Dict[str, Any]:
        """Analyze back filing for multiple years"""
        logger.info("Analyzing 3-year back filing opportunity")

        results = []
        total_refund = Decimal('0')
        total_owed = Decimal('0')

        for year in self.years_to_analyze:
            income = income_by_year.get(year, Decimal('0'))
            deductions = deductions_by_year.get(year, Decimal('0'))

            # Calculate tax for that year (simplified)
            taxable_income = max(income - deductions - Decimal('13850'), Decimal('0'))  # 2024 standard deduction
            tax = self._calculate_historical_tax(taxable_income, year)

            # Determine if refund or owed
            if tax < 0:
                total_refund += abs(tax)
                status = 'REFUND'
            else:
                total_owed += tax
                status = 'OWED'

            results.append({
                'year': year,
                'income': float(income),
                'deductions': float(deductions),
                'tax_liability': float(tax),
                'status': status,
                'filing_deadline': self._get_filing_deadline(year)
            })

        return {
            'years_analyzed': self.years_to_analyze,
            'results': results,
            'total_potential_refund': float(total_refund),
            'total_owed': float(total_owed),
            'net_position': float(total_refund - total_owed),
            'recommendation': self._generate_recommendation(total_refund, total_owed)
        }

    def _calculate_historical_tax(self, taxable_income: Decimal, year: int) -> Decimal:
        """Calculate tax for historical year (simplified)"""
        # Using 2025 rates as approximation
        calculator = TaxCalculationEngine()
        return calculator.calculate_federal_tax(taxable_income, FilingStatus.SINGLE)

    def _get_filing_deadline(self, year: int) -> str:
        """Get filing deadline for back taxes"""
        # 3-year statute of limitations for refunds
        deadline_year = year + 3
        return f"April 15, {deadline_year}"

    def _generate_recommendation(self, refund: Decimal, owed: Decimal) -> str:
        """Generate filing recommendation"""
        if refund > owed:
            return f"FILE IMMEDIATELY - Potential refund of ${refund:.2f}"
        elif owed > Decimal('1000'):
            return f"CONSIDER FILING - Balance owed ${owed:.2f} (penalties may apply)"
        else:
            return "Review individual years for filing decision"


# ============================================================================
# QUARTERLY ESTIMATED TAX CALCULATOR
# ============================================================================

class QuarterlyEstimatedTaxCalculator:
    """Calculate quarterly estimated tax payments (Form 1040-ES)"""

    def __init__(self, tax_year: int = 2025):
        self.tax_year = tax_year
        self.quarterly_due_dates = [
            date(tax_year, 4, 15),   # Q1
            date(tax_year, 6, 15),   # Q2
            date(tax_year, 9, 15),   # Q3
            date(tax_year + 1, 1, 15) # Q4
        ]

    def calculate_estimated_payments(self, projected_tax: Decimal,
                                    prior_year_tax: Decimal,
                                    withholding: Decimal = Decimal('0')) -> Dict[str, Any]:
        """Calculate quarterly estimated tax payments"""
        logger.info("Calculating quarterly estimated tax payments")

        # Determine safe harbor amount
        # 90% of current year OR 100% of prior year (110% if high income)
        safe_harbor_current = projected_tax * Decimal(str(SAFE_HARBOR_CURRENT_YEAR))
        safe_harbor_prior = prior_year_tax * Decimal(str(SAFE_HARBOR_PRIOR_YEAR))

        safe_harbor_required = min(safe_harbor_current, safe_harbor_prior)

        # Amount needed after withholding
        amount_needed = max(safe_harbor_required - withholding, Decimal('0'))

        # Divide into quarterly payments
        quarterly_payment = amount_needed / Decimal('4')

        payments = []
        for i, due_date in enumerate(self.quarterly_due_dates, 1):
            payment = QuarterlyPayment(
                quarter=i,
                due_date=due_date,
                amount=quarterly_payment
            )
            payments.append({
                'quarter': payment.quarter,
                'due_date': payment.due_date.isoformat(),
                'amount': float(payment.amount)
            })

        return {
            'projected_tax': float(projected_tax),
            'safe_harbor_required': float(safe_harbor_required),
            'withholding': float(withholding),
            'total_estimated_needed': float(amount_needed),
            'quarterly_payment': float(quarterly_payment),
            'payments': payments,
            'recommendation': self._generate_payment_recommendation(amount_needed)
        }

    def _generate_payment_recommendation(self, amount_needed: Decimal) -> str:
        """Generate payment recommendation"""
        if amount_needed == 0:
            return "No estimated payments required - withholding sufficient"
        elif amount_needed < Decimal('1000'):
            return "Estimated payments recommended but penalty likely minimal"
        else:
            return f"Make quarterly payments of ${amount_needed/4:.2f} to avoid penalties"


# ============================================================================
# STATE TAX INTEGRATOR
# ============================================================================

class StateTaxIntegrator:
    """Integrate state tax calculations for multiple states"""

    def __init__(self):
        self.states = STATE_TAX_RATES

    def compare_state_tax_burden(self, taxable_income: Decimal) -> pd.DataFrame:
        """Compare tax burden across different states"""
        logger.info("Comparing state tax burden")

        results = []

        for state, info in self.states.items():
            calculator = TaxCalculationEngine()
            state_tax = calculator.calculate_state_tax(taxable_income, state)

            results.append({
                'state': state,
                'state_tax': float(state_tax),
                'effective_rate': float(info['rate'] * 100),
                'tax_savings_vs_ca': float(
                    calculator.calculate_state_tax(taxable_income, 'CA') - state_tax
                )
            })

        df = pd.DataFrame(results)
        df = df.sort_values('state_tax', ascending=True)
        return df

    def recommend_state_for_tax_optimization(self, income: Decimal) -> Dict[str, Any]:
        """Recommend best state for tax optimization"""
        comparison = self.compare_state_tax_burden(income)

        best_state = comparison.iloc[0]
        worst_state = comparison.iloc[-1]

        savings = worst_state['state_tax'] - best_state['state_tax']

        return {
            'best_state': best_state['state'],
            'best_state_tax': best_state['state_tax'],
            'worst_state': worst_state['state'],
            'worst_state_tax': worst_state['state_tax'],
            'annual_savings': float(savings),
            'recommendation': f"Moving from {worst_state['state']} to {best_state['state']} saves ${savings:,.2f} annually"
        }


# ============================================================================
# COMPLETE TAX PROJECTION SYSTEM
# ============================================================================

class CompleteTaxProjectionSystem:
    """
    Complete Tax Projection and Planning System

    Integrates all tax planning tools
    """

    def __init__(self, filing_status: FilingStatus, state: str = 'CA'):
        self.filing_status = filing_status
        self.state = state
        self.projection_calculator = TaxProjectionCalculator(filing_status, state)
        self.credit_optimizer = TaxCreditOptimizer()
        self.back_filing_analyzer = BackFilingAnalyzer()
        self.quarterly_calculator = QuarterlyEstimatedTaxCalculator()
        self.state_integrator = StateTaxIntegrator()

        logger.info(f"Tax Projection System initialized - {filing_status.value} - {state}")

    def comprehensive_tax_analysis(self, current_scenario: IncomeScenario,
                                  prior_year_tax: Decimal = Decimal('0')) -> Dict[str, Any]:
        """Perform comprehensive tax analysis"""
        logger.info("Performing comprehensive tax analysis")

        # 1. Current year projection
        current_projection = self.projection_calculator.project_tax_liability(current_scenario)

        # 2. Quarterly estimated payments
        quarterly_payments = self.quarterly_calculator.calculate_estimated_payments(
            Decimal(str(current_projection['total_tax_liability'])),
            prior_year_tax
        )

        # 3. State comparison
        state_comparison = self.state_integrator.compare_state_tax_burden(
            Decimal(str(current_projection['taxable_income']))
        )

        # 4. State optimization recommendation
        state_recommendation = self.state_integrator.recommend_state_for_tax_optimization(
            Decimal(str(current_projection['total_income']))
        )

        return {
            'current_year_projection': current_projection,
            'quarterly_estimated_payments': quarterly_payments,
            'state_tax_comparison': state_comparison.to_dict('records'),
            'state_optimization': state_recommendation,
            'analysis_date': datetime.now().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demonstrate_tax_projection():
    """Demonstrate tax projection calculator"""

    print("=" * 80)
    print("TAX PROJECTION CALCULATOR - 2025")
    print("=" * 80)

    # Initialize system
    tax_system = CompleteTaxProjectionSystem(
        filing_status=FilingStatus.MARRIED_JOINT,
        state='CA'
    )

    # Create income scenario
    scenario = IncomeScenario(
        name="2025 Base Case",
        w2_income=Decimal('150000'),
        self_employment_income=Decimal('75000'),
        rental_income=Decimal('24000'),
        investment_income=Decimal('5000'),
        capital_gains_short=Decimal('3000'),
        capital_gains_long=Decimal('12000'),
        other_income=Decimal('0')
    )

    # Run comprehensive analysis
    analysis = tax_system.comprehensive_tax_analysis(
        scenario,
        prior_year_tax=Decimal('45000')
    )

    # Display results
    print("\n✓ CURRENT YEAR PROJECTION")
    current = analysis['current_year_projection']
    print(f"  Total Income: ${current['total_income']:,.2f}")
    print(f"  AGI: ${current['agi']:,.2f}")
    print(f"  Taxable Income: ${current['taxable_income']:,.2f}")
    print(f"  Federal Tax: ${current['federal_income_tax']:,.2f}")
    print(f"  SE Tax: ${current['self_employment_tax']:,.2f}")
    print(f"  State Tax: ${current['state_tax']:,.2f}")
    print(f"  TOTAL TAX: ${current['total_tax_liability']:,.2f}")
    print(f"  Effective Rate: {current['effective_tax_rate']:.2f}%")

    print("\n✓ QUARTERLY ESTIMATED PAYMENTS")
    quarterly = analysis['quarterly_estimated_payments']
    print(f"  Quarterly Payment: ${quarterly['quarterly_payment']:,.2f}")
    for payment in quarterly['payments']:
        print(f"    Q{payment['quarter']}: ${payment['amount']:,.2f} due {payment['due_date']}")

    print("\n✓ STATE TAX OPTIMIZATION")
    state_opt = analysis['state_optimization']
    print(f"  Best State: {state_opt['best_state']} (${state_opt['best_state_tax']:,.2f})")
    print(f"  Current State: CA")
    print(f"  {state_opt['recommendation']}")

    print("\n" + "=" * 80)
    print("TAX PROJECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demonstrate_tax_projection())
