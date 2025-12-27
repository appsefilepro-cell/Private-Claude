
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
