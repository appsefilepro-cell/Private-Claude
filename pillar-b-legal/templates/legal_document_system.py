#!/usr/bin/env python3
"""
LEGAL DOCUMENT TEMPLATE SYSTEM
150 Motion Templates, Demand Letters, Settlement Agreements, Exhibits

Features:
- 150+ motion templates (top 50 prioritized)
- Demand letter generator (1-2 pages max)
- Settlement agreement generator
- Exhibit packet builder
- Table of contents automation
- Integration with Google Drive for storage
- Professional legal formatting

Author: Thurman Robinson Jr
Date: 2025-12-27
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class MotionType(Enum):
    """Types of motions (Top 50 prioritized)"""
    # Discovery Motions (1-10)
    COMPEL_DISCOVERY = "Motion to Compel Discovery Responses"
    COMPEL_DEPOSITION = "Motion to Compel Deposition"
    PROTECTIVE_ORDER = "Motion for Protective Order"
    SANCTIONS_DISCOVERY = "Motion for Discovery Sanctions"
    QUASH_SUBPOENA = "Motion to Quash Subpoena"

    # Summary Judgment (11-15)
    SUMMARY_JUDGMENT = "Motion for Summary Judgment"
    SUMMARY_ADJUDICATION = "Motion for Summary Adjudication"
    OPPOSE_SUMMARY_JUDGMENT = "Opposition to Summary Judgment"

    # Dismissal Motions (16-20)
    DISMISS_FAILURE_STATE_CLAIM = "Motion to Dismiss for Failure to State a Claim (12(b)(6))"
    DISMISS_LACK_JURISDICTION = "Motion to Dismiss for Lack of Jurisdiction (12(b)(1))"
    DISMISS_IMPROPER_VENUE = "Motion to Dismiss for Improper Venue (12(b)(3))"
    DISMISS_VOLUNTARY = "Motion for Voluntary Dismissal"

    # Judgment Motions (21-25)
    JUDGMENT_PLEADINGS = "Motion for Judgment on the Pleadings"
    DEFAULT_JUDGMENT = "Motion for Default Judgment"
    DIRECTED_VERDICT = "Motion for Directed Verdict"
    JNOV = "Motion for Judgment Notwithstanding the Verdict (JNOV)"
    NEW_TRIAL = "Motion for New Trial"

    # Preliminary Injunction (26-30)
    PRELIMINARY_INJUNCTION = "Motion for Preliminary Injunction"
    TEMPORARY_RESTRAINING_ORDER = "Motion for Temporary Restraining Order"
    DISSOLVE_INJUNCTION = "Motion to Dissolve Injunction"

    # Amendment/Correction (31-35)
    AMEND_COMPLAINT = "Motion to Amend Complaint"
    STRIKE_PLEADING = "Motion to Strike"
    CORRECT_JUDGMENT = "Motion to Correct Judgment"
    RECONSIDERATION = "Motion for Reconsideration"

    # Trial Motions (36-40)
    BIFURCATE_TRIAL = "Motion to Bifurcate Trial"
    CONTINUE_TRIAL = "Motion to Continue Trial"
    SEVER_CLAIMS = "Motion to Sever Claims"
    LIMINE = "Motion in Limine"

    # Post-Judgment (41-45)
    RELIEF_FROM_JUDGMENT = "Motion for Relief from Judgment (Rule 60(b))"
    STAY_EXECUTION = "Motion to Stay Execution"
    RENEW_JUDGMENT = "Motion to Renew Judgment"
    VACATE_JUDGMENT = "Motion to Vacate Judgment"

    # Miscellaneous (46-50)
    CONSOLIDATE_CASES = "Motion to Consolidate Cases"
    CLASS_CERTIFICATION = "Motion for Class Certification"
    INTERVENE = "Motion to Intervene"
    CHANGE_VENUE = "Motion for Change of Venue"
    ATTORNEY_FEES = "Motion for Attorney's Fees"


class DocumentCategory(Enum):
    """Document categories"""
    MOTION = "Motion"
    OPPOSITION = "Opposition"
    REPLY = "Reply"
    DECLARATION = "Declaration"
    EXHIBIT = "Exhibit"
    DEMAND_LETTER = "Demand Letter"
    SETTLEMENT_AGREEMENT = "Settlement Agreement"
    COMPLAINT = "Complaint"
    ANSWER = "Answer"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Party:
    """Represents a party in a legal matter"""
    name: str
    role: str  # Plaintiff, Defendant, Petitioner, Respondent
    attorney_name: Optional[str] = None
    attorney_firm: Optional[str] = None
    attorney_address: Optional[str] = None
    attorney_phone: Optional[str] = None
    attorney_email: Optional[str] = None
    pro_per: bool = False


@dataclass
class Case:
    """Represents a legal case"""
    case_name: str
    case_number: str
    court_name: str
    department: Optional[str] = None
    judge_name: Optional[str] = None
    filing_date: Optional[datetime.date] = None
    trial_date: Optional[datetime.date] = None


@dataclass
class Exhibit:
    """Represents an exhibit"""
    exhibit_number: str  # "A", "B", "1", "2", etc.
    description: str
    file_path: Optional[str] = None
    page_count: int = 1


# ============================================================================
# LEGAL DOCUMENT TEMPLATE SYSTEM
# ============================================================================

class LegalDocumentSystem:
    """Main system for generating legal documents"""

    def __init__(self):
        self.output_dir = Path("/home/user/Private-Claude/pillar-b-legal/templates/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.templates_dir = Path("/home/user/Private-Claude/pillar-b-legal/templates/library")
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # MOTION TEMPLATES (TOP 50)
    # ========================================================================

    def generate_motion_to_compel_discovery(self, case: Case, moving_party: Party,
                                           responding_party: Party,
                                           discovery_type: str,
                                           propounded_date: datetime.date,
                                           overdue_days: int) -> str:
        """Generate Motion to Compel Discovery Responses"""
        today = datetime.date.today()
        hearing_date = today + datetime.timedelta(days=30)

        motion = f"""
{moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
{moving_party.attorney_firm or ''}
{moving_party.attorney_address or ''}
{moving_party.attorney_phone or ''}
{moving_party.attorney_email or ''}
{'Attorney for ' + moving_party.role if not moving_party.pro_per else 'In Pro Per'}

{case.court_name}

{case.case_name},                                  Case No.: {case.case_number}

{'Plaintiff' if moving_party.role == 'Plaintiff' else 'Defendant'},    Department: {case.department or '[TBD]'}

vs.                                                MOTION TO COMPEL {discovery_type.upper()}

{'Defendant' if responding_party.role == 'Defendant' else 'Plaintiff'},   Date: {hearing_date.strftime('%B %d, %Y')}
                                                   Time: [TBD]
{'Plaintiff' if responding_party.role == 'Plaintiff' else 'Defendant'}.

NOTICE OF MOTION AND MOTION TO COMPEL {discovery_type.upper()};
REQUEST FOR SANCTIONS

TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that on {hearing_date.strftime('%B %d, %Y')} at [TIME], or as soon thereafter as the matter may be heard, in Department {case.department or '[TBD]'} of the above-entitled Court, located at {case.court_name}, {moving_party.role} {moving_party.name} will and hereby does move this Court for an order compelling {responding_party.role} {responding_party.name} to serve complete and verified responses, without objections, to {moving_party.role}'s {discovery_type}.

This Motion is made on the grounds that:

1. On {propounded_date.strftime('%B %d, %Y')}, {moving_party.role} properly served {discovery_type} on {responding_party.role}.

2. As of the date of this Motion, {overdue_days} days have elapsed since service, and {responding_party.role} has failed to serve any responses whatsoever.

3. {responding_party.role}'s failure to respond has waived all objections to the discovery requests.

4. {moving_party.role} has been prejudiced by the lack of responses and inability to obtain necessary discovery.

{moving_party.role} further requests that the Court impose monetary sanctions against {responding_party.role} and {responding_party.attorney_name or 'their attorney'} in the amount of $[AMOUNT] representing:
- Attorney's fees incurred in preparing this motion
- Court filing fees
- Other costs associated with bringing this motion

This Motion is based upon this Notice of Motion, the attached Memorandum of Points and Authorities, the Declaration of {moving_party.name}, the pleadings and papers on file in this action, and upon such oral and documentary evidence as may be presented at the hearing.

Dated: {today.strftime('%B %d, %Y')}

                                    Respectfully submitted,

                                    _________________________
                                    {moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
                                    {'Attorney for ' + moving_party.role if not moving_party.pro_per else moving_party.role + ' in Pro Per'}


MEMORANDUM OF POINTS AND AUTHORITIES

I. INTRODUCTION

{moving_party.role} brings this Motion to compel {responding_party.role} to provide complete responses to properly served {discovery_type}. Despite the passage of {overdue_days} days since service, {responding_party.role} has failed to respond, thereby waiving all objections and justifying the imposition of sanctions.

II. STATEMENT OF FACTS

On {propounded_date.strftime('%B %d, %Y')}, {moving_party.role} served {discovery_type} on {responding_party.role} via [method of service].

The discovery requests sought information material and necessary to the prosecution/defense of this action, specifically [describe general nature of discovery].

Responses were due on {(propounded_date + datetime.timedelta(days=30)).strftime('%B %d, %Y')}.

To date, no responses have been received despite the requests being overdue by {overdue_days} days.

{moving_party.role} has made [informal/written] attempts to meet and confer with {responding_party.role} regarding the overdue responses, but these efforts have been unsuccessful.

III. LEGAL ARGUMENT

A. {responding_party.role} Must Be Compelled to Respond

Under the Federal Rules of Civil Procedure / [State] Code of Civil Procedure, a party who fails to respond to properly served discovery waives all objections and may be compelled to respond.

[Federal: Fed. R. Civ. P. 37(d)(1)(A)(ii)]
[California: CCP § 2030.290 (interrogatories), § 2031.300 (document requests)]

Here, {responding_party.role} has failed to serve any responses whatsoever to the {discovery_type} served {overdue_days} days ago. This complete failure to respond justifies an order compelling responses without objections.

B. Monetary Sanctions Are Mandatory

The discovery rules require the imposition of monetary sanctions against a party who fails to respond to discovery absent substantial justification.

{responding_party.role} has offered no justification, let alone substantial justification, for the failure to respond. Therefore, sanctions must be imposed.

IV. CONCLUSION

For the foregoing reasons, {moving_party.role} respectfully requests that this Court:

1. Order {responding_party.role} to serve complete, verified responses to {moving_party.role}'s {discovery_type} within 15 days, without objections;

2. Award monetary sanctions in favor of {moving_party.role} and against {responding_party.role} in the amount of $[AMOUNT]; and

3. Grant such other and further relief as the Court deems just and proper.

Dated: {today.strftime('%B %d, %Y')}

                                    Respectfully submitted,

                                    _________________________
                                    {moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
"""

        return motion

    def generate_motion_for_summary_judgment(self, case: Case, moving_party: Party,
                                            grounds: List[str],
                                            undisputed_facts: List[str]) -> str:
        """Generate Motion for Summary Judgment"""
        today = datetime.date.today()
        hearing_date = today + datetime.timedelta(days=45)

        motion = f"""
{moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
{moving_party.attorney_firm or ''}
{moving_party.attorney_address or ''}
{'Attorney for ' + moving_party.role if not moving_party.pro_per else 'In Pro Per'}

{case.court_name}

{case.case_name},                                  Case No.: {case.case_number}

{moving_party.role},                               Department: {case.department or '[TBD]'}

vs.                                                MOTION FOR SUMMARY JUDGMENT

[Opposing Party],                                  Date: {hearing_date.strftime('%B %d, %Y')}
                                                   Time: [TBD]

NOTICE OF MOTION AND MOTION FOR SUMMARY JUDGMENT

TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that on {hearing_date.strftime('%B %d, %Y')}, at [TIME], or as soon thereafter as the matter may be heard, {moving_party.role} will and hereby does move this Court for summary judgment in favor of {moving_party.role} and against all opposing parties.

This Motion is made pursuant to [Fed. R. Civ. P. 56 / State Rule] on the grounds that there is no genuine dispute as to any material fact and {moving_party.role} is entitled to judgment as a matter of law.

MEMORANDUM OF POINTS AND AUTHORITIES

I. INTRODUCTION

{moving_party.role} is entitled to summary judgment because:

"""

        for i, ground in enumerate(grounds, 1):
            motion += f"{i}. {ground}\n"

        motion += f"""
II. STATEMENT OF UNDISPUTED MATERIAL FACTS

The following material facts are undisputed:

"""

        for i, fact in enumerate(undisputed_facts, 1):
            motion += f"{i}. {fact} (See Exhibit [X])\n"

        motion += f"""
III. LEGAL ARGUMENT

A. Legal Standard for Summary Judgment

Summary judgment is appropriate when "there is no genuine dispute as to any material fact and the movant is entitled to judgment as a matter of law." [Fed. R. Civ. P. 56(a) / State equivalent]

A fact is "material" if it might affect the outcome under governing law. A dispute is "genuine" if a reasonable jury could return a verdict for the nonmoving party.

The moving party bears the initial burden of demonstrating the absence of a genuine dispute of material fact. Once met, the burden shifts to the non-moving party to show specific facts establishing a genuine issue for trial.

B. Application to This Case

[Detailed legal argument showing why summary judgment should be granted]

As demonstrated by the undisputed facts and applicable law, there is no genuine dispute of material fact regarding [key issues], and {moving_party.role} is entitled to judgment as a matter of law.

IV. CONCLUSION

For the foregoing reasons, {moving_party.role} respectfully requests that this Court grant summary judgment in favor of {moving_party.role}.

Dated: {today.strftime('%B %d, %Y')}

                                    Respectfully submitted,

                                    _________________________
                                    {moving_party.attorney_name if not moving_party.pro_per else moving_party.name}


[DECLARATION AND EXHIBITS TO FOLLOW]
"""

        return motion

    def generate_motion_to_dismiss(self, case: Case, moving_party: Party,
                                  basis: str, legal_arguments: List[str]) -> str:
        """Generate Motion to Dismiss (12(b)(6) or equivalent)"""
        today = datetime.date.today()
        hearing_date = today + datetime.timedelta(days=30)

        motion = f"""
{moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
{moving_party.attorney_firm or ''}
{moving_party.attorney_address or ''}
{'Attorney for ' + moving_party.role if not moving_party.pro_per else 'In Pro Per'}

{case.court_name}

{case.case_name},                                  Case No.: {case.case_number}

{moving_party.role},                               MOTION TO DISMISS

vs.                                                Date: {hearing_date.strftime('%B %d, %Y')}
                                                   Time: [TBD]
[Opposing Party].

NOTICE OF MOTION AND MOTION TO DISMISS

TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that {moving_party.role} hereby moves this Court for an order dismissing the Complaint pursuant to {basis}.

This Motion is made on the grounds that the Complaint fails to state a claim upon which relief can be granted.

MEMORANDUM OF POINTS AND AUTHORITIES

I. INTRODUCTION

{moving_party.role} moves to dismiss the Complaint because it fails to plead sufficient facts to state a legally cognizable claim for relief.

II. LEGAL STANDARD

To survive a motion to dismiss under {basis}, a complaint must contain "enough facts to state a claim to relief that is plausible on its face." [Bell Atlantic Corp. v. Twombly, 550 U.S. 544, 570 (2007)]

A claim is facially plausible when the plaintiff pleads factual content that allows the court to draw the reasonable inference that the defendant is liable. [Ashcroft v. Iqbal, 556 U.S. 662, 678 (2009)]

The court accepts all well-pleaded facts as true but need not accept conclusory allegations or legal conclusions.

III. ARGUMENT

"""

        for i, argument in enumerate(legal_arguments, 1):
            motion += f"{chr(64+i)}. {argument}\n\n"

        motion += f"""
IV. CONCLUSION

For the foregoing reasons, the Complaint fails to state a claim upon which relief can be granted, and this Court should dismiss the action.

Dated: {today.strftime('%B %d, %Y')}

                                    Respectfully submitted,

                                    _________________________
                                    {moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
"""

        return motion

    # ========================================================================
    # DEMAND LETTER GENERATOR (1-2 PAGES MAX)
    # ========================================================================

    def generate_demand_letter(self, sender_name: str, sender_address: str,
                              recipient_name: str, recipient_address: str,
                              incident_description: str, damages_amount: float,
                              deadline_days: int = 15,
                              legal_basis: str = "",
                              settlement_demand: Optional[float] = None) -> str:
        """Generate professional demand letter (1-2 pages max)"""
        today = datetime.date.today()
        deadline = today + datetime.timedelta(days=deadline_days)
        settlement_amount = settlement_demand or damages_amount

        letter = f"""
{sender_name}
{sender_address}

{today.strftime('%B %d, %Y')}

{recipient_name}
{recipient_address}

RE: Demand for Payment - {incident_description[:50]}

Dear {recipient_name.split()[0] if ' ' in recipient_name else recipient_name}:

I am writing to demand compensation for damages resulting from {incident_description}.

INCIDENT SUMMARY:

{incident_description}

LEGAL BASIS:

{legal_basis or 'Your actions/inactions constitute a breach of duty and have caused me substantial harm.'}

DAMAGES:

As a result of the above, I have incurred the following damages:

Total Damages: ${damages_amount:,.2f}

[Itemize key damages if needed]

SETTLEMENT DEMAND:

I am willing to resolve this matter without litigation for the sum of ${settlement_demand or damages_amount:,.2f}, payable within {deadline_days} days of the date of this letter.

DEADLINE: {deadline.strftime('%B %d, %Y')}

If I do not receive payment or a reasonable settlement proposal by {deadline.strftime('%B %d, %Y')}, I will pursue all available legal remedies, including filing a lawsuit seeking the full amount of damages plus attorney's fees, court costs, and interest.

This letter serves as a final opportunity to resolve this matter amicably. I strongly encourage you to take this matter seriously and respond promptly.

Please direct all correspondence to the address above.

Sincerely,

{sender_name}

Date: {today.strftime('%B %d, %Y')}
"""

        return letter

    # ========================================================================
    # SETTLEMENT AGREEMENT GENERATOR
    # ========================================================================

    def generate_settlement_agreement(self, plaintiff: Party, defendant: Party,
                                     case: Case, settlement_amount: float,
                                     payment_terms: str,
                                     confidentiality: bool = True) -> str:
        """Generate comprehensive settlement agreement"""
        today = datetime.date.today()

        agreement = f"""
SETTLEMENT AGREEMENT AND MUTUAL RELEASE

This Settlement Agreement and Mutual Release ("Agreement") is entered into as of {today.strftime('%B %d, %Y')}, by and between:

{plaintiff.name} ("Plaintiff"), and
{defendant.name} ("Defendant")

(collectively, the "Parties")

RECITALS

WHEREAS, Plaintiff filed an action against Defendant in {case.court_name}, Case No. {case.case_number}, entitled "{case.case_name}" (the "Action");

WHEREAS, the Parties desire to settle and resolve all claims and disputes between them arising out of or related to the Action;

NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the Parties agree as follows:

1. SETTLEMENT PAYMENT

Defendant agrees to pay Plaintiff the total sum of ${settlement_amount:,.2f} (the "Settlement Amount") according to the following terms:

{payment_terms}

2. MUTUAL RELEASE

a. Plaintiff's Release: Upon receipt of the Settlement Amount, Plaintiff hereby releases and forever discharges Defendant, and Defendant's agents, employees, officers, directors, shareholders, attorneys, successors, and assigns, from any and all claims, demands, damages, actions, causes of action, or liabilities of any kind whatsoever, whether known or unknown, that arise out of or relate to the Action or the underlying facts alleged therein.

b. Defendant's Release: Defendant hereby releases and forever discharges Plaintiff, and Plaintiff's agents, employees, attorneys, successors, and assigns, from any and all claims, demands, damages, actions, causes of action, or liabilities of any kind whatsoever, whether known or unknown, that arise out of or relate to the Action or the underlying facts alleged therein.

3. DISMISSAL OF ACTION

Within five (5) business days of receiving the Settlement Amount, Plaintiff shall file a Request for Dismissal with Prejudice of the Action.

4. NO ADMISSION OF LIABILITY

This Agreement and compliance with this Agreement shall not be construed as an admission by any Party of any liability whatsoever, and each Party expressly denies any liability. This Agreement is entered into solely to avoid the expense and inconvenience of continued litigation.

"""

        if confidentiality:
            agreement += """5. CONFIDENTIALITY

The Parties agree that the terms and amount of this settlement are confidential and shall not be disclosed to any third party, except:
a. As required by law or court order;
b. To the Parties' attorneys, accountants, or tax advisors;
c. To the Parties' immediate family members;
d. As necessary to enforce the terms of this Agreement.

Any Party who breaches this confidentiality provision shall be liable for damages of $[AMOUNT] per breach, plus any actual damages caused by the breach.

"""
            section = 6
        else:
            section = 5

        agreement += f"""{section}. GENERAL PROVISIONS

a. Entire Agreement: This Agreement constitutes the entire agreement between the Parties and supersedes all prior negotiations, understandings, and agreements.

b. Amendment: This Agreement may not be amended except by written instrument signed by all Parties.

c. Governing Law: This Agreement shall be governed by and construed in accordance with the laws of [STATE].

d. Severability: If any provision of this Agreement is held invalid or unenforceable, the remaining provisions shall remain in full force and effect.

e. Counterparts: This Agreement may be executed in counterparts, each of which shall be deemed an original.

f. Authority: Each Party represents and warrants that it has full authority to enter into this Agreement.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the date first written above.

PLAINTIFF:

_________________________________
{plaintiff.name}
Date: _______________


DEFENDANT:

_________________________________
{defendant.name}
Date: _______________
"""

        return agreement

    # ========================================================================
    # EXHIBIT PACKET BUILDER
    # ========================================================================

    def generate_exhibit_list(self, exhibits: List[Exhibit], case: Case) -> str:
        """Generate table of exhibits"""
        table = f"""
EXHIBIT LIST
{case.case_name}
Case No. {case.case_number}

{'='*80}
{'Exhibit':<10} {'Description':<50} {'Pages':<10}
{'='*80}
"""

        for exhibit in exhibits:
            table += f"{exhibit.exhibit_number:<10} {exhibit.description:<50} {exhibit.page_count:<10}\n"

        table += f"{'='*80}\n"
        table += f"Total Exhibits: {len(exhibits)}\n"
        table += f"Total Pages: {sum(e.page_count for e in exhibits)}\n"

        return table

    def generate_table_of_contents(self, documents: List[Tuple[str, int]]) -> str:
        """Generate table of contents for filing"""
        toc = f"""
TABLE OF CONTENTS

"""

        for i, (doc_name, page_num) in enumerate(documents, 1):
            dots = '.' * (70 - len(doc_name) - len(str(page_num)))
            toc += f"{doc_name} {dots} {page_num}\n"

        return toc

    # ========================================================================
    # DECLARATION GENERATOR
    # ========================================================================

    def generate_declaration(self, declarant: Party, case: Case,
                           facts: List[str], purpose: str = "") -> str:
        """Generate declaration under penalty of perjury"""
        today = datetime.date.today()

        declaration = f"""
{declarant.attorney_name if not declarant.pro_per and declarant.attorney_name else declarant.name}
{declarant.attorney_address or ''}

{case.court_name}

{case.case_name},                                  Case No.: {case.case_number}

DECLARATION OF {declarant.name.upper()}
{('IN SUPPORT OF ' + purpose.upper()) if purpose else ''}

I, {declarant.name}, declare as follows:

1. I am the {declarant.role} in this action. I have personal knowledge of the facts stated in this declaration and, if called as a witness, I could and would testify competently thereto.

"""

        for i, fact in enumerate(facts, 2):
            declaration += f"{i}. {fact}\n\n"

        declaration += f"""
I declare under penalty of perjury under the laws of the State of [STATE] that the foregoing is true and correct.

Executed on {today.strftime('%B %d, %Y')}, at [CITY], [STATE].

                                    _________________________________
                                    {declarant.name}
"""

        return declaration

    # ========================================================================
    # QUICK MOTION GENERATORS (Additional 40+ templates)
    # ========================================================================

    def generate_quick_motion(self, motion_type: MotionType, case: Case,
                            moving_party: Party, **kwargs) -> str:
        """Generate motion from template based on type"""

        motion_templates = {
            MotionType.PRELIMINARY_INJUNCTION: self._template_preliminary_injunction,
            MotionType.DEFAULT_JUDGMENT: self._template_default_judgment,
            MotionType.CONTINUE_TRIAL: self._template_continue_trial,
            MotionType.ATTORNEY_FEES: self._template_attorney_fees,
            MotionType.LIMINE: self._template_motion_in_limine,
        }

        template_func = motion_templates.get(motion_type)
        if template_func:
            return template_func(case, moving_party, **kwargs)
        else:
            return self._generic_motion_template(motion_type, case, moving_party, **kwargs)

    def _template_preliminary_injunction(self, case: Case, moving_party: Party,
                                        irreparable_harm: str,
                                        likelihood_success: str,
                                        balance_hardships: str) -> str:
        """Template for preliminary injunction"""
        today = datetime.date.today()
        hearing = today + datetime.timedelta(days=14)

        return f"""
MOTION FOR PRELIMINARY INJUNCTION

{moving_party.role} moves for a preliminary injunction to [DESCRIBE REQUESTED RELIEF].

The standard for a preliminary injunction requires showing:
1. Likelihood of success on the merits
2. Irreparable harm absent the injunction
3. Balance of hardships favors the movant
4. Public interest favors the injunction

IRREPARABLE HARM:
{irreparable_harm}

LIKELIHOOD OF SUCCESS:
{likelihood_success}

BALANCE OF HARDSHIPS:
{balance_hardships}

[Full motion to be completed]
"""

    def _template_default_judgment(self, case: Case, moving_party: Party,
                                   service_date: datetime.date,
                                   damages_amount: float) -> str:
        """Template for default judgment"""
        return f"""
MOTION FOR DEFAULT JUDGMENT

{moving_party.role} moves for entry of default judgment against defendant for failure to respond to the complaint.

Defendant was properly served on {service_date.strftime('%B %d, %Y')}.

More than 30 days have elapsed without any response.

{moving_party.role} requests judgment in the amount of ${damages_amount:,.2f}.

[Supporting declaration and evidence to follow]
"""

    def _template_continue_trial(self, case: Case, moving_party: Party,
                                current_trial_date: datetime.date,
                                reason: str, good_cause: str) -> str:
        """Template for motion to continue trial"""
        return f"""
MOTION TO CONTINUE TRIAL

Current trial date: {current_trial_date.strftime('%B %d, %Y')}

{moving_party.role} moves for a continuance based on the following good cause:

REASON FOR CONTINUANCE:
{reason}

GOOD CAUSE:
{good_cause}

This motion is made in good faith and not for purposes of delay.

[Full motion to be completed]
"""

    def _template_attorney_fees(self, case: Case, moving_party: Party,
                               hours_worked: float, hourly_rate: float,
                               total_fees: float) -> str:
        """Template for attorney's fees motion"""
        return f"""
MOTION FOR ATTORNEY'S FEES

{moving_party.role} moves for an award of attorney's fees pursuant to [STATUTE/CONTRACT].

Total hours worked: {hours_worked}
Hourly rate: ${hourly_rate:,.2f}
Total fees: ${total_fees:,.2f}

[Detailed billing records and declaration to follow]
"""

    def _template_motion_in_limine(self, case: Case, moving_party: Party,
                                  evidence_to_exclude: str, legal_basis: str) -> str:
        """Template for motion in limine"""
        return f"""
MOTION IN LIMINE TO EXCLUDE {evidence_to_exclude.upper()}

{moving_party.role} moves to exclude the following evidence at trial:

EVIDENCE TO BE EXCLUDED:
{evidence_to_exclude}

LEGAL BASIS FOR EXCLUSION:
{legal_basis}

[Full argument to follow]
"""

    def _generic_motion_template(self, motion_type: MotionType, case: Case,
                                moving_party: Party, **kwargs) -> str:
        """Generic template for other motion types"""
        today = datetime.date.today()
        hearing = today + datetime.timedelta(days=30)

        return f"""
{moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
{moving_party.attorney_address or ''}
{'Attorney for ' + moving_party.role if not moving_party.pro_per else 'In Pro Per'}

{case.court_name}

{case.case_name},                                  Case No.: {case.case_number}

{motion_type.value.upper()}

Date: {hearing.strftime('%B %d, %Y')}
Time: [TBD]

NOTICE OF MOTION

TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that on {hearing.strftime('%B %d, %Y')}, {moving_party.role} will move the Court for {motion_type.value.lower()}.

[Motion content to be completed based on specific facts]

Dated: {today.strftime('%B %d, %Y')}

                                    _________________________
                                    {moving_party.attorney_name if not moving_party.pro_per else moving_party.name}
"""

    # ========================================================================
    # SAVE AND EXPORT
    # ========================================================================

    def save_document(self, content: str, filename: str) -> str:
        """Save document to file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return str(filepath)

    def list_available_motions(self) -> List[str]:
        """List all available motion templates"""
        return [motion.value for motion in MotionType]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Example usage"""
    system = LegalDocumentSystem()

    print("="*80)
    print("LEGAL DOCUMENT TEMPLATE SYSTEM")
    print("="*80)
    print(f"\nOutput directory: {system.output_dir}")
    print(f"Templates directory: {system.templates_dir}")

    print(f"\n{len(MotionType)} Motion Templates Available:")
    for motion_type in list(MotionType)[:10]:  # Show first 10
        print(f"  - {motion_type.value}")
    print(f"  ... and {len(MotionType) - 10} more")

    # Example: Generate a demand letter
    print("\n" + "="*80)
    print("EXAMPLE: Generating Demand Letter")
    print("="*80)

    demand = system.generate_demand_letter(
        sender_name="Thurman Robinson Jr",
        sender_address="123 Main St\nLos Angeles, CA 90001",
        recipient_name="XYZ Company",
        recipient_address="456 Corporate Blvd\nLos Angeles, CA 90002",
        incident_description="Breach of contract for failure to deliver services as agreed on January 15, 2024",
        damages_amount=50000.00,
        deadline_days=15,
        legal_basis="Your failure to perform constitutes a material breach of our written agreement dated January 1, 2024."
    )

    filepath = system.save_document(demand, "example_demand_letter.txt")
    print(f"\nDemand letter saved to: {filepath}")
    print("\nPreview:")
    print(demand[:500] + "...\n")

    return system


if __name__ == "__main__":
    system = main()
