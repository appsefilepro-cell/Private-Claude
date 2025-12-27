#!/usr/bin/env python3
"""
COMPREHENSIVE DAMAGES CALCULATOR SUITE
Interactive calculator for credit, personal injury, and business loss damages

Features:
- Credit Damages: FDCRA ($1000 per violation), FCRA ($100-$1000 per violation)
- Personal Injury: Medical expenses, lost wages, pain/suffering, 5-year disability
- Business Loss: Revenue loss, opportunity cost, reputation damages
- Interactive web calculator (Streamlit)
- Generate demand letters with calculated amounts
- Export to PDF

Author: Thurman Robinson Jr
Date: 2025-12-27
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class DamageType(Enum):
    """Types of damages"""
    CREDIT = "Credit Reporting Damages"
    PERSONAL_INJURY = "Personal Injury Damages"
    BUSINESS_LOSS = "Business Loss Damages"
    EMPLOYMENT = "Employment Discrimination Damages"
    HOUSING = "Housing Discrimination Damages"


class InjurySeverity(Enum):
    """Personal injury severity levels"""
    MINOR = "Minor (sprains, bruises, soft tissue)"
    MODERATE = "Moderate (fractures, surgery required)"
    SEVERE = "Severe (permanent disability, disfigurement)"
    CATASTROPHIC = "Catastrophic (paralysis, brain injury)"


# Pain and suffering multipliers by severity
PAIN_MULTIPLIERS = {
    InjurySeverity.MINOR: (1.5, 3.0),
    InjurySeverity.MODERATE: (3.0, 5.0),
    InjurySeverity.SEVERE: (5.0, 8.0),
    InjurySeverity.CATASTROPHIC: (8.0, 10.0)
}


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CreditDamages:
    """Credit reporting damages calculation"""
    # FCRA violations
    fcra_violations: int = 0
    fcra_per_violation: int = 1000  # $100-$1000 range

    # FDCRA violations
    fdcra_violations: int = 0
    fdcra_per_violation: int = 1000  # $1000 per violation

    # Additional damages
    credit_denials: int = 0
    higher_interest_cost: float = 0.0
    emotional_distress: float = 5000.0

    # Punitive multiplier
    punitive_multiplier: float = 2.0

    def calculate_total(self) -> Dict[str, float]:
        """Calculate total credit damages"""
        # Statutory damages
        fcra_statutory = self.fcra_violations * self.fcra_per_violation
        fdcra_statutory = self.fdcra_violations * self.fdcra_per_violation
        total_statutory = fcra_statutory + fdcra_statutory

        # Economic damages
        economic = self.higher_interest_cost

        # Non-economic damages
        non_economic = self.emotional_distress

        # Total actual damages
        actual_damages = total_statutory + economic + non_economic

        # Punitive damages (can be 2-3x actual for willful violations)
        punitive = actual_damages * self.punitive_multiplier

        # Total
        total = actual_damages + punitive

        return {
            'fcra_statutory': fcra_statutory,
            'fdcra_statutory': fdcra_statutory,
            'total_statutory': total_statutory,
            'economic_damages': economic,
            'non_economic_damages': non_economic,
            'actual_damages': actual_damages,
            'punitive_damages': punitive,
            'total_damages': total,
            'attorney_fees_recoverable': True,
            'costs_recoverable': True
        }

    def generate_breakdown(self) -> str:
        """Generate detailed damages breakdown"""
        calc = self.calculate_total()

        breakdown = f"""
CREDIT DAMAGES CALCULATION
{'='*80}

STATUTORY DAMAGES:
------------------
FCRA Violations ({self.fcra_violations} × ${self.fcra_per_violation:,}):     ${calc['fcra_statutory']:,.2f}
FDCRA Violations ({self.fdcra_violations} × ${self.fdcra_per_violation:,}):   ${calc['fdcra_statutory']:,.2f}
                                        ____________
Total Statutory Damages:                ${calc['total_statutory']:,.2f}

ECONOMIC DAMAGES:
-----------------
Higher Interest Costs:                   ${calc['economic_damages']:,.2f}

NON-ECONOMIC DAMAGES:
---------------------
Emotional Distress:                      ${calc['non_economic_damages']:,.2f}

ACTUAL DAMAGES SUBTOTAL:                 ${calc['actual_damages']:,.2f}

PUNITIVE DAMAGES:
-----------------
(Actual damages × {self.punitive_multiplier}):          ${calc['punitive_damages']:,.2f}

{'='*80}
TOTAL DAMAGES:                           ${calc['total_damages']:,.2f}
{'='*80}

ADDITIONAL RECOVERABLE:
- Attorney's fees (pursuant to statute)
- Court costs and filing fees
- Expert witness fees
- Investigation costs
"""
        return breakdown


@dataclass
class PersonalInjuryDamages:
    """Personal injury damages calculation"""
    # Medical expenses
    emergency_room: float = 0.0
    hospital_stay_days: int = 0
    hospital_cost_per_day: float = 3000.0
    surgery_costs: float = 0.0
    doctor_visits: float = 0.0
    physical_therapy: float = 0.0
    medications: float = 0.0
    medical_equipment: float = 0.0
    future_medical: float = 0.0

    # Lost wages
    missed_work_days: int = 0
    daily_wage: float = 0.0
    lost_bonuses: float = 0.0
    lost_promotions: float = 0.0

    # Future lost earnings (5-year disability)
    disability_years: int = 0
    annual_salary: float = 0.0

    # Pain and suffering
    injury_severity: InjurySeverity = InjurySeverity.MODERATE
    pain_multiplier: float = 4.0  # Default moderate

    # Property damage
    vehicle_damage: float = 0.0
    personal_property: float = 0.0

    # Quality of life
    permanent_disability: bool = False
    permanent_disfigurement: bool = False
    loss_of_consortium: bool = False

    def calculate_total(self) -> Dict[str, float]:
        """Calculate total personal injury damages"""
        # Medical expenses (special damages - economic)
        total_medical = (
            self.emergency_room +
            (self.hospital_stay_days * self.hospital_cost_per_day) +
            self.surgery_costs +
            self.doctor_visits +
            self.physical_therapy +
            self.medications +
            self.medical_equipment +
            self.future_medical
        )

        # Lost wages (special damages - economic)
        past_lost_wages = (self.missed_work_days * self.daily_wage) + self.lost_bonuses + self.lost_promotions
        future_lost_wages = self.disability_years * self.annual_salary
        total_lost_wages = past_lost_wages + future_lost_wages

        # Property damage (special damages - economic)
        property_damage = self.vehicle_damage + self.personal_property

        # Total special damages (economic)
        special_damages = total_medical + total_lost_wages + property_damage

        # Pain and suffering (general damages - non-economic)
        # Standard calculation: special damages × pain multiplier
        base_pain_suffering = special_damages * self.pain_multiplier

        # Adjustments for permanent conditions
        pain_suffering = base_pain_suffering
        if self.permanent_disability:
            pain_suffering += 100000  # Add $100k for permanent disability
        if self.permanent_disfigurement:
            pain_suffering += 50000   # Add $50k for disfigurement
        if self.loss_of_consortium:
            pain_suffering += 50000   # Add $50k for loss of consortium

        # Total general damages (non-economic)
        general_damages = pain_suffering

        # Total compensatory damages
        compensatory = special_damages + general_damages

        # Punitive damages (rare in personal injury unless gross negligence)
        # Conservative estimate: 0 unless specified
        punitive = 0.0

        # Total
        total = compensatory + punitive

        return {
            'medical_expenses': total_medical,
            'past_lost_wages': past_lost_wages,
            'future_lost_wages': future_lost_wages,
            'total_lost_wages': total_lost_wages,
            'property_damage': property_damage,
            'special_damages': special_damages,
            'pain_and_suffering': pain_suffering,
            'general_damages': general_damages,
            'compensatory_damages': compensatory,
            'punitive_damages': punitive,
            'total_damages': total
        }

    def generate_breakdown(self) -> str:
        """Generate detailed damages breakdown"""
        calc = self.calculate_total()

        breakdown = f"""
PERSONAL INJURY DAMAGES CALCULATION
{'='*80}

SPECIAL DAMAGES (Economic):
---------------------------
Medical Expenses:
  Emergency Room:                        ${self.emergency_room:,.2f}
  Hospital Stay ({self.hospital_stay_days} days @ ${self.hospital_cost_per_day:,.2f}):
                                         ${self.hospital_stay_days * self.hospital_cost_per_day:,.2f}
  Surgery Costs:                         ${self.surgery_costs:,.2f}
  Doctor Visits:                         ${self.doctor_visits:,.2f}
  Physical Therapy:                      ${self.physical_therapy:,.2f}
  Medications:                           ${self.medications:,.2f}
  Medical Equipment:                     ${self.medical_equipment:,.2f}
  Future Medical:                        ${self.future_medical:,.2f}
                                         ____________
  Total Medical:                         ${calc['medical_expenses']:,.2f}

Lost Wages:
  Past Lost Wages ({self.missed_work_days} days):
                                         ${calc['past_lost_wages']:,.2f}
  Future Lost Wages ({self.disability_years} years):
                                         ${calc['future_lost_wages']:,.2f}
                                         ____________
  Total Lost Wages:                      ${calc['total_lost_wages']:,.2f}

Property Damage:
  Vehicle Damage:                        ${self.vehicle_damage:,.2f}
  Personal Property:                     ${self.personal_property:,.2f}
                                         ____________
  Total Property:                        ${calc['property_damage']:,.2f}

TOTAL SPECIAL DAMAGES:                   ${calc['special_damages']:,.2f}

GENERAL DAMAGES (Non-Economic):
-------------------------------
Pain and Suffering:
  Base ({self.injury_severity.value}):
  (Special damages × {self.pain_multiplier})
                                         ${calc['pain_and_suffering']:,.2f}
"""

        if self.permanent_disability:
            breakdown += "  Permanent Disability Adjustment:      +$100,000\n"
        if self.permanent_disfigurement:
            breakdown += "  Permanent Disfigurement Adjustment:   +$50,000\n"
        if self.loss_of_consortium:
            breakdown += "  Loss of Consortium:                   +$50,000\n"

        breakdown += f"""
TOTAL GENERAL DAMAGES:                   ${calc['general_damages']:,.2f}

{'='*80}
TOTAL COMPENSATORY DAMAGES:              ${calc['compensatory_damages']:,.2f}

Punitive Damages (if applicable):        ${calc['punitive_damages']:,.2f}

{'='*80}
TOTAL DAMAGES:                           ${calc['total_damages']:,.2f}
{'='*80}
"""
        return breakdown


@dataclass
class BusinessLossDamages:
    """Business loss damages calculation"""
    # Revenue loss
    lost_revenue_monthly: float = 0.0
    months_affected: int = 0

    # Lost profits
    profit_margin: float = 0.20  # 20% default

    # Lost opportunities
    lost_contracts_value: float = 0.0
    lost_clients_value: float = 0.0

    # Reputation damages
    reputation_repair_cost: float = 0.0
    lost_goodwill: float = 0.0

    # Operating costs during disruption
    continued_overhead: float = 0.0

    # Future earnings impact
    future_revenue_impact_years: int = 0
    projected_annual_revenue: float = 0.0
    future_impact_percentage: float = 0.10  # 10% reduction

    # Mitigation costs
    alternative_arrangements: float = 0.0
    recovery_costs: float = 0.0

    def calculate_total(self) -> Dict[str, float]:
        """Calculate total business loss damages"""
        # Lost revenue
        total_lost_revenue = self.lost_revenue_monthly * self.months_affected

        # Lost profits
        lost_profits = total_lost_revenue * self.profit_margin

        # Lost opportunities
        lost_opportunities = self.lost_contracts_value + self.lost_clients_value

        # Reputation damages
        reputation_damages = self.reputation_repair_cost + self.lost_goodwill

        # Continued overhead during disruption
        overhead = self.continued_overhead

        # Future earnings impact
        annual_future_impact = self.projected_annual_revenue * self.future_impact_percentage
        total_future_impact = annual_future_impact * self.future_revenue_impact_years

        # Mitigation costs
        mitigation = self.alternative_arrangements + self.recovery_costs

        # Total economic damages
        economic_damages = (
            lost_profits +
            lost_opportunities +
            overhead +
            total_future_impact +
            mitigation
        )

        # Non-economic damages (reputation)
        non_economic = reputation_damages

        # Total
        total = economic_damages + non_economic

        return {
            'lost_revenue': total_lost_revenue,
            'lost_profits': lost_profits,
            'lost_opportunities': lost_opportunities,
            'reputation_damages': reputation_damages,
            'overhead_costs': overhead,
            'future_earnings_impact': total_future_impact,
            'mitigation_costs': mitigation,
            'economic_damages': economic_damages,
            'non_economic_damages': non_economic,
            'total_damages': total
        }

    def generate_breakdown(self) -> str:
        """Generate detailed damages breakdown"""
        calc = self.calculate_total()

        breakdown = f"""
BUSINESS LOSS DAMAGES CALCULATION
{'='*80}

ECONOMIC DAMAGES:
-----------------
Lost Revenue:
  Monthly Lost Revenue: ${self.lost_revenue_monthly:,.2f}
  Months Affected: {self.months_affected}
  Total Lost Revenue:                    ${calc['lost_revenue']:,.2f}

Lost Profits:
  (Lost Revenue × {self.profit_margin:.0%} margin):
                                         ${calc['lost_profits']:,.2f}

Lost Opportunities:
  Lost Contracts:                        ${self.lost_contracts_value:,.2f}
  Lost Clients:                          ${self.lost_clients_value:,.2f}
                                         ____________
  Total Lost Opportunities:              ${calc['lost_opportunities']:,.2f}

Continued Overhead:                      ${calc['overhead_costs']:,.2f}

Future Earnings Impact:
  ({self.future_revenue_impact_years} years × ${calc['future_earnings_impact'] / max(self.future_revenue_impact_years, 1):,.2f}/year):
                                         ${calc['future_earnings_impact']:,.2f}

Mitigation Costs:
  Alternative Arrangements:              ${self.alternative_arrangements:,.2f}
  Recovery Costs:                        ${self.recovery_costs:,.2f}
                                         ____________
  Total Mitigation:                      ${calc['mitigation_costs']:,.2f}

TOTAL ECONOMIC DAMAGES:                  ${calc['economic_damages']:,.2f}

NON-ECONOMIC DAMAGES:
---------------------
Reputation Repair:                       ${self.reputation_repair_cost:,.2f}
Lost Goodwill:                           ${self.lost_goodwill:,.2f}
                                         ____________
TOTAL NON-ECONOMIC DAMAGES:              ${calc['non_economic_damages']:,.2f}

{'='*80}
TOTAL DAMAGES:                           ${calc['total_damages']:,.2f}
{'='*80}
"""
        return breakdown


# ============================================================================
# DEMAND LETTER GENERATOR
# ============================================================================

class DemandLetterGenerator:
    """Generate demand letters with calculated damages"""

    @staticmethod
    def generate_credit_demand(damages: CreditDamages, defendant_name: str,
                               defendant_address: str, plaintiff_name: str,
                               plaintiff_address: str) -> str:
        """Generate demand letter for credit damages"""
        calc = damages.calculate_total()
        today = datetime.date.today()
        deadline = today + datetime.timedelta(days=15)

        letter = f"""
{plaintiff_name}
{plaintiff_address}

{today.strftime('%B %d, %Y')}

{defendant_name}
{defendant_address}

RE: DEMAND FOR DAMAGES - FCRA/FDCRA VIOLATIONS

Dear Sir/Madam:

This letter constitutes a formal demand for damages resulting from your violations of the Fair Credit Reporting Act (FCRA) and Fair Debt Collection Reporting Act (FDCRA).

VIOLATIONS:

Your company has committed {damages.fcra_violations + damages.fdcra_violations} violations of federal consumer protection law, including:
- {damages.fcra_violations} FCRA violations
- {damages.fdcra_violations} FDCRA violations

DAMAGES CALCULATION:

{damages.generate_breakdown()}

SETTLEMENT DEMAND: ${calc['total_damages']:,.2f}

This demand includes:
- Statutory damages
- Economic damages for higher interest costs
- Non-economic damages for emotional distress
- Punitive damages for willful violations

In addition, I am entitled to recover attorney's fees and costs under 15 U.S.C. § 1681n(a)(3).

DEADLINE: {deadline.strftime('%B %d, %Y')}

You have 15 days to respond to this demand. If I do not receive a satisfactory settlement offer by {deadline.strftime('%B %d, %Y')}, I will file a lawsuit in federal court seeking the full amount of damages plus attorney's fees, costs, and any additional punitive damages.

Please direct all communications to the address above.

Sincerely,

{plaintiff_name}
Date: {today.strftime('%B %d, %Y')}
"""
        return letter

    @staticmethod
    def generate_personal_injury_demand(damages: PersonalInjuryDamages,
                                       defendant_name: str, defendant_address: str,
                                       plaintiff_name: str, plaintiff_address: str,
                                       incident_date: datetime.date,
                                       incident_description: str) -> str:
        """Generate demand letter for personal injury"""
        calc = damages.calculate_total()
        today = datetime.date.today()
        deadline = today + datetime.timedelta(days=30)

        letter = f"""
{plaintiff_name}
{plaintiff_address}

{today.strftime('%B %d, %Y')}

{defendant_name}
{defendant_address}

RE: DEMAND FOR DAMAGES - PERSONAL INJURY
    Date of Incident: {incident_date.strftime('%B %d, %Y')}

Dear Sir/Madam:

I am writing to demand compensation for injuries I sustained as a result of your negligence on {incident_date.strftime('%B %d, %Y')}.

INCIDENT DESCRIPTION:

{incident_description}

INJURIES SUSTAINED:

Injury Severity: {damages.injury_severity.value}
"""

        if damages.hospital_stay_days > 0:
            letter += f"Hospital Stay: {damages.hospital_stay_days} days\n"
        if damages.surgery_costs > 0:
            letter += "Surgery Required: Yes\n"
        if damages.permanent_disability:
            letter += "Permanent Disability: Yes\n"
        if damages.permanent_disfigurement:
            letter += "Permanent Disfigurement: Yes\n"

        letter += f"""
DAMAGES CALCULATION:

{damages.generate_breakdown()}

SETTLEMENT DEMAND: ${calc['total_damages']:,.2f}

This demand represents fair compensation for:
1. All medical expenses (past and future)
2. Lost wages and earning capacity
3. Pain and suffering
4. Permanent injuries and disability
5. Loss of quality of life

DEADLINE: {deadline.strftime('%B %d, %Y')}

You have 30 days to respond to this demand with a reasonable settlement offer. Failure to respond or offer reasonable compensation will result in the filing of a lawsuit seeking the full amount of damages plus costs and interest.

I am willing to negotiate in good faith, but the damages suffered are substantial and well-documented.

Please direct all communications to the address above or through my attorney.

Sincerely,

{plaintiff_name}
Date: {today.strftime('%B %d, %Y')}

Enclosures: Medical records, bills, wage statements
"""
        return letter

    @staticmethod
    def generate_business_loss_demand(damages: BusinessLossDamages,
                                     defendant_name: str, defendant_address: str,
                                     plaintiff_name: str, plaintiff_address: str,
                                     breach_description: str) -> str:
        """Generate demand letter for business losses"""
        calc = damages.calculate_total()
        today = datetime.date.today()
        deadline = today + datetime.timedelta(days=20)

        letter = f"""
{plaintiff_name}
{plaintiff_address}

{today.strftime('%B %d, %Y')}

{defendant_name}
{defendant_address}

RE: DEMAND FOR DAMAGES - BUSINESS LOSSES

Dear Sir/Madam:

I am writing to demand compensation for substantial business losses resulting from your breach of contract/negligence/misconduct.

DESCRIPTION OF BREACH:

{breach_description}

DAMAGES SUFFERED:

{damages.generate_breakdown()}

SETTLEMENT DEMAND: ${calc['total_damages']:,.2f}

These damages are well-documented and conservative. They include:
- Direct revenue losses
- Lost profit margins
- Lost business opportunities
- Damage to business reputation
- Future earnings impact over {damages.future_revenue_impact_years} years
- Mitigation and recovery costs

All damages are supported by financial records, contracts, and expert analysis.

DEADLINE: {deadline.strftime('%B %d, %Y')}

You have 20 days to respond with payment or a reasonable settlement proposal. Failure to do so will result in immediate legal action seeking the full amount of damages plus attorney's fees, costs, prejudgment interest, and any additional consequential damages.

This matter can be resolved amicably, but the damages are substantial and must be addressed promptly.

Sincerely,

{plaintiff_name}
Date: {today.strftime('%B %d, %Y')}

Enclosures: Financial statements, contracts, expert reports
"""
        return letter


# ============================================================================
# DAMAGES CALCULATOR SYSTEM
# ============================================================================

class DamagesCalculatorSystem:
    """Main system for calculating and managing damages"""

    def __init__(self):
        self.output_dir = Path("/home/user/Private-Claude/pillar-b-legal/damages/calculations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def calculate_credit_damages(self, fcra_violations: int, fdcra_violations: int,
                                higher_interest: float = 0.0,
                                emotional_distress: float = 5000.0) -> CreditDamages:
        """Calculate credit reporting damages"""
        damages = CreditDamages(
            fcra_violations=fcra_violations,
            fdcra_violations=fdcra_violations,
            higher_interest_cost=higher_interest,
            emotional_distress=emotional_distress
        )
        return damages

    def calculate_personal_injury(self, **kwargs) -> PersonalInjuryDamages:
        """Calculate personal injury damages"""
        damages = PersonalInjuryDamages(**kwargs)
        return damages

    def calculate_business_loss(self, **kwargs) -> BusinessLossDamages:
        """Calculate business loss damages"""
        damages = BusinessLossDamages(**kwargs)
        return damages

    def save_calculation(self, damages, filename: str) -> str:
        """Save damages calculation to file"""
        filepath = self.output_dir / filename

        if isinstance(damages, CreditDamages):
            content = damages.generate_breakdown()
        elif isinstance(damages, PersonalInjuryDamages):
            content = damages.generate_breakdown()
        elif isinstance(damages, BusinessLossDamages):
            content = damages.generate_breakdown()
        else:
            content = str(damages)

        with open(filepath, 'w') as f:
            f.write(content)

        return str(filepath)

    def generate_demand_letter(self, damages, damage_type: DamageType,
                              plaintiff_name: str, plaintiff_address: str,
                              defendant_name: str, defendant_address: str,
                              **kwargs) -> str:
        """Generate demand letter based on damage type"""
        generator = DemandLetterGenerator()

        if damage_type == DamageType.CREDIT:
            letter = generator.generate_credit_demand(
                damages, defendant_name, defendant_address,
                plaintiff_name, plaintiff_address
            )
        elif damage_type == DamageType.PERSONAL_INJURY:
            letter = generator.generate_personal_injury_demand(
                damages, defendant_name, defendant_address,
                plaintiff_name, plaintiff_address,
                kwargs.get('incident_date', datetime.date.today()),
                kwargs.get('incident_description', '')
            )
        elif damage_type == DamageType.BUSINESS_LOSS:
            letter = generator.generate_business_loss_demand(
                damages, defendant_name, defendant_address,
                plaintiff_name, plaintiff_address,
                kwargs.get('breach_description', '')
            )
        else:
            raise ValueError(f"Unsupported damage type: {damage_type}")

        # Save letter
        filename = f"demand_letter_{damage_type.name.lower()}_{datetime.date.today().isoformat()}.txt"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(letter)

        return str(filepath)

    def generate_comparison_report(self, scenarios: List[Tuple[str, any]]) -> str:
        """Generate comparison report for multiple damage scenarios"""
        report = f"""
DAMAGES COMPARISON REPORT
Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'='*80}

"""

        for name, damages in scenarios:
            if isinstance(damages, CreditDamages):
                calc = damages.calculate_total()
                total = calc['total_damages']
            elif isinstance(damages, PersonalInjuryDamages):
                calc = damages.calculate_total()
                total = calc['total_damages']
            elif isinstance(damages, BusinessLossDamages):
                calc = damages.calculate_total()
                total = calc['total_damages']
            else:
                total = 0

            report += f"{name}: ${total:,.2f}\n"

        report += f"\n{'='*80}\n"
        return report


# ============================================================================
# STREAMLIT WEB INTERFACE (To be run separately)
# ============================================================================

STREAMLIT_APP = '''
"""
Streamlit web interface for damages calculator
Run with: streamlit run damages_calculator_interface.py
"""

import streamlit as st
from damages_calculator_suite import *
import datetime

st.set_page_config(page_title="Damages Calculator Suite", layout="wide")

st.title("Comprehensive Damages Calculator")

# Sidebar for damage type selection
damage_type = st.sidebar.selectbox(
    "Select Damage Type",
    ["Credit Reporting", "Personal Injury", "Business Loss"]
)

calculator = DamagesCalculatorSystem()

# Credit Damages Calculator
if damage_type == "Credit Reporting":
    st.header("Credit Reporting Damages Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Violations")
        fcra_violations = st.number_input("FCRA Violations", min_value=0, value=5)
        fdcra_violations = st.number_input("FDCRA Violations", min_value=0, value=0)

        st.subheader("Economic Damages")
        higher_interest = st.number_input("Higher Interest Costs ($)", min_value=0.0, value=0.0, step=100.0)

        st.subheader("Non-Economic Damages")
        emotional_distress = st.number_input("Emotional Distress ($)", min_value=0.0, value=5000.0, step=1000.0)

    if st.button("Calculate Credit Damages"):
        damages = calculator.calculate_credit_damages(
            fcra_violations=int(fcra_violations),
            fdcra_violations=int(fdcra_violations),
            higher_interest=float(higher_interest),
            emotional_distress=float(emotional_distress)
        )

        with col2:
            st.subheader("Results")
            st.text(damages.generate_breakdown())

            calc = damages.calculate_total()
            st.metric("TOTAL DAMAGES", f"${calc['total_damages']:,.2f}")

# Personal Injury Calculator
elif damage_type == "Personal Injury":
    st.header("Personal Injury Damages Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Medical Expenses")
        er_cost = st.number_input("Emergency Room ($)", min_value=0.0, value=0.0, step=500.0)
        hospital_days = st.number_input("Hospital Days", min_value=0, value=0)
        surgery = st.number_input("Surgery Costs ($)", min_value=0.0, value=0.0, step=1000.0)
        doctor = st.number_input("Doctor Visits ($)", min_value=0.0, value=0.0, step=100.0)
        therapy = st.number_input("Physical Therapy ($)", min_value=0.0, value=0.0, step=100.0)
        meds = st.number_input("Medications ($)", min_value=0.0, value=0.0, step=50.0)

        st.subheader("Lost Wages")
        missed_days = st.number_input("Missed Work Days", min_value=0, value=0)
        daily_wage = st.number_input("Daily Wage ($)", min_value=0.0, value=0.0, step=50.0)

        st.subheader("Injury Severity")
        severity = st.selectbox("Severity", [s.value for s in InjurySeverity])

        permanent_disability = st.checkbox("Permanent Disability")
        permanent_disfigurement = st.checkbox("Permanent Disfigurement")

    if st.button("Calculate Personal Injury Damages"):
        severity_enum = [s for s in InjurySeverity if s.value == severity][0]
        multiplier = sum(PAIN_MULTIPLIERS[severity_enum]) / 2

        damages = calculator.calculate_personal_injury(
            emergency_room=float(er_cost),
            hospital_stay_days=int(hospital_days),
            surgery_costs=float(surgery),
            doctor_visits=float(doctor),
            physical_therapy=float(therapy),
            medications=float(meds),
            missed_work_days=int(missed_days),
            daily_wage=float(daily_wage),
            injury_severity=severity_enum,
            pain_multiplier=multiplier,
            permanent_disability=permanent_disability,
            permanent_disfigurement=permanent_disfigurement
        )

        with col2:
            st.subheader("Results")
            st.text(damages.generate_breakdown())

            calc = damages.calculate_total()
            st.metric("TOTAL DAMAGES", f"${calc['total_damages']:,.2f}")

# Business Loss Calculator
elif damage_type == "Business Loss":
    st.header("Business Loss Damages Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Loss")
        monthly_revenue = st.number_input("Monthly Lost Revenue ($)", min_value=0.0, value=0.0, step=1000.0)
        months = st.number_input("Months Affected", min_value=0, value=0)
        profit_margin = st.slider("Profit Margin (%)", min_value=0, max_value=100, value=20) / 100

        st.subheader("Lost Opportunities")
        lost_contracts = st.number_input("Lost Contracts Value ($)", min_value=0.0, value=0.0, step=5000.0)
        lost_clients = st.number_input("Lost Clients Value ($)", min_value=0.0, value=0.0, step=5000.0)

        st.subheader("Reputation")
        reputation_repair = st.number_input("Reputation Repair Cost ($)", min_value=0.0, value=0.0, step=1000.0)
        lost_goodwill = st.number_input("Lost Goodwill ($)", min_value=0.0, value=0.0, step=5000.0)

    if st.button("Calculate Business Loss Damages"):
        damages = calculator.calculate_business_loss(
            lost_revenue_monthly=float(monthly_revenue),
            months_affected=int(months),
            profit_margin=float(profit_margin),
            lost_contracts_value=float(lost_contracts),
            lost_clients_value=float(lost_clients),
            reputation_repair_cost=float(reputation_repair),
            lost_goodwill=float(lost_goodwill)
        )

        with col2:
            st.subheader("Results")
            st.text(damages.generate_breakdown())

            calc = damages.calculate_total()
            st.metric("TOTAL DAMAGES", f"${calc['total_damages']:,.2f}")
'''


# ============================================================================
# MAIN EXECUTION AND EXAMPLES
# ============================================================================

def main():
    """Example usage"""
    calculator = DamagesCalculatorSystem()

    print("Damages Calculator Suite Initialized")
    print(f"Output directory: {calculator.output_dir}")

    # Example: Credit damages
    print("\n" + "="*80)
    print("EXAMPLE: Credit Damages Calculation")
    print("="*80)

    credit_damages = calculator.calculate_credit_damages(
        fcra_violations=10,
        fdcra_violations=5,
        higher_interest=5000.0,
        emotional_distress=5000.0
    )

    print(credit_damages.generate_breakdown())

    # Example: Personal injury
    print("\n" + "="*80)
    print("EXAMPLE: Personal Injury Damages Calculation")
    print("="*80)

    injury_damages = calculator.calculate_personal_injury(
        emergency_room=2000.0,
        hospital_stay_days=5,
        surgery_costs=25000.0,
        doctor_visits=3000.0,
        physical_therapy=5000.0,
        medications=1000.0,
        missed_work_days=60,
        daily_wage=200.0,
        injury_severity=InjurySeverity.MODERATE,
        pain_multiplier=4.0,
        permanent_disability=True
    )

    print(injury_damages.generate_breakdown())

    # Save Streamlit app
    streamlit_file = Path("/home/user/Private-Claude/pillar-b-legal/damages/damages_calculator_interface.py")
    with open(streamlit_file, 'w') as f:
        f.write(STREAMLIT_APP)

    print(f"\n\nStreamlit interface saved to: {streamlit_file}")
    print("Run with: streamlit run damages_calculator_interface.py")

    return calculator


if __name__ == "__main__":
    calculator = main()
