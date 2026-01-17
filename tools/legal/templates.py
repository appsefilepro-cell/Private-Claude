"""
Legal Document Templates
Pre-formatted templates for common legal documents
"""

# Motion templates
MOTION_TEMPLATES = {
    'preliminary_injunction': """
NOTICE OF MOTION FOR PRELIMINARY INJUNCTION

TO: {defendant_name} AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that on {hearing_date}, at {hearing_time}, or as soon thereafter as the matter may be heard, in Department {dept_number} of the above-entitled Court, located at {court_address}, {plaintiff_name} will move the Court for an order granting a preliminary injunction against {defendant_name}.

The motion will be based on this Notice, the Memorandum of Points and Authorities, the Declaration of {declarant_name}, and all exhibits attached thereto, the pleadings and papers on file in this action, and such other matters as may be presented at the hearing.

Dated: {date}

Respectfully submitted,

_________________________
{attorney_name}
Attorney for Plaintiff
""",
    
    'tro': """
EX PARTE APPLICATION FOR TEMPORARY RESTRAINING ORDER

TO THE COURT:

Plaintiff {plaintiff_name} respectfully applies ex parte for a Temporary Restraining Order (TRO) against Defendant {defendant_name}, without notice, restraining Defendant from {conduct_to_restrain}.

This application is made pursuant to [statute] and is supported by the Declaration of {declarant_name} filed herewith.

RELIEF REQUESTED:

Plaintiff requests that this Court issue a Temporary Restraining Order:

1. Restraining Defendant from {specific_conduct};
2. Requiring Defendant to {affirmative_relief};
3. Setting a hearing on Plaintiff's Motion for Preliminary Injunction within {days} days;
4. Granting such other and further relief as the Court deems just and proper.

GROUNDS FOR RELIEF:

This ex parte application is necessary because {explanation_of_urgency}.

Dated: {date}

Respectfully submitted,

_________________________
{attorney_name}
Attorney for Plaintiff
""",
    
    'summary_judgment': """
NOTICE OF MOTION FOR SUMMARY JUDGMENT

TO ALL PARTIES AND THEIR ATTORNEYS OF RECORD:

PLEASE TAKE NOTICE that on {hearing_date}, at {hearing_time}, or as soon thereafter as the matter may be heard, Plaintiff {plaintiff_name} will move this Court for an order granting summary judgment in favor of Plaintiff and against Defendant {defendant_name} on all causes of action alleged in the Complaint.

This motion is made on the grounds that there is no triable issue of material fact and Plaintiff is entitled to judgment as a matter of law.

The motion will be based on this Notice, the Memorandum of Points and Authorities, the Separate Statement of Undisputed Material Facts, the Declaration of {declarant_name} with exhibits, all pleadings and papers on file, and such other matters as may be presented at the hearing.

Dated: {date}

Respectfully submitted,

_________________________
{attorney_name}
Attorney for Plaintiff
"""
}

# Discovery templates
DISCOVERY_TEMPLATES = {
    'interrogatories': """
PLAINTIFF'S FIRST SET OF INTERROGATORIES TO DEFENDANT

TO: {defendant_name}
TO: {defendant_attorney}

Pursuant to [Code of Civil Procedure], Plaintiff {plaintiff_name} propounds the following Interrogatories to Defendant {defendant_name}, to be answered under oath within thirty (30) days from service hereof.

DEFINITIONS

1. "YOU" or "YOUR" means Defendant {defendant_name} and all persons acting on behalf of Defendant.

2. "DOCUMENT" means any written, recorded, or graphic matter, however produced or reproduced.

3. "COMMUNICATION" means any transmission of information by any means.

4. "IDENTIFY" when used with respect to a person means to state the person's full name, address, telephone number, and job title.

INTERROGATORIES

INTERROGATORY NO. 1:
State your full name, current address, and all addresses where you have resided during the past five (5) years.

INTERROGATORY NO. 2:
Identify all persons with knowledge of facts relevant to the claims or defenses in this action.

INTERROGATORY NO. 3:
Describe in detail the factual basis for each affirmative defense you have asserted in your Answer.

INTERROGATORY NO. 4:
Identify all documents that support each affirmative defense you have asserted.

INTERROGATORY NO. 5:
State the amount of damages, if any, that you claim in this action, and describe how you calculated that amount.

[Continue with specific case-related interrogatories...]

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
""",

    'rfp': """
PLAINTIFF'S FIRST REQUEST FOR PRODUCTION OF DOCUMENTS

TO: {defendant_name}
TO: {defendant_attorney}

Pursuant to [Code of Civil Procedure], Plaintiff {plaintiff_name} requests that Defendant {defendant_name} produce for inspection and copying the documents described below within thirty (30) days from service hereof.

DEFINITIONS

[Same as interrogatories]

REQUESTS FOR PRODUCTION

REQUEST NO. 1:
All DOCUMENTS concerning any contract, agreement, or understanding between YOU and Plaintiff.

REQUEST NO. 2:
All COMMUNICATIONS between YOU and Plaintiff from {start_date} to {end_date}.

REQUEST NO. 3:
All DOCUMENTS concerning any payments received from or made to Plaintiff.

REQUEST NO. 4:
All DOCUMENTS concerning YOUR policies, procedures, or guidelines relevant to {subject_matter}.

REQUEST NO. 5:
All DOCUMENTS identified in YOUR responses to Plaintiff's Interrogatories.

[Continue with specific document requests...]

The documents shall be produced at the offices of {attorney_name}, located at {address}, or as otherwise mutually agreed.

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
""",

    'rfa': """
PLAINTIFF'S FIRST REQUEST FOR ADMISSIONS

TO: {defendant_name}
TO: {defendant_attorney}

Pursuant to [Code of Civil Procedure], Plaintiff {plaintiff_name} requests that Defendant {defendant_name} admit the truth of the following matters within thirty (30) days from service hereof.

DEFINITIONS

[Same as interrogatories]

REQUESTS FOR ADMISSION

REQUEST FOR ADMISSION NO. 1:
Admit that YOU entered into a contract with Plaintiff on or about {date}.

REQUEST FOR ADMISSION NO. 2:
Admit that the document attached as Exhibit A is a true and correct copy of the contract between YOU and Plaintiff.

REQUEST FOR ADMISSION NO. 3:
Admit that YOU received payment from Plaintiff in the amount of ${amount} on {date}.

REQUEST FOR ADMISSION NO. 4:
Admit that YOU failed to perform YOUR obligations under the contract.

REQUEST FOR ADMISSION NO. 5:
Admit that Plaintiff suffered damages as a result of YOUR breach of contract.

[Continue with specific admissions...]

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
"""
}

# Declaration templates
DECLARATION_TEMPLATES = {
    'standard': """
DECLARATION OF {declarant_name}

I, {declarant_name}, declare as follows:

1. I am {description_of_declarant}. I have personal knowledge of the facts set forth in this declaration and, if called as a witness, I could and would testify competently thereto.

2. {Statement of facts - numbered paragraphs}

3. [Continue with factual statements...]

I declare under penalty of perjury under the laws of [State/United States] that the foregoing is true and correct.

Executed on {date}, at {city}, {state}.

_________________________
{declarant_name}
""",

    'authentication': """
DECLARATION OF AUTHENTICITY OF DOCUMENTS

I, {declarant_name}, declare as follows:

1. I am the {title} of {party_name}. I have personal knowledge of the facts stated in this declaration.

2. Attached as Exhibit A is a true and correct copy of {document_description}.

3. I am the custodian of records for {document_type}.

4. The attached documents were prepared in the ordinary course of business at or near the time of the events recorded.

5. It is the regular practice of our organization to make such records.

I declare under penalty of perjury under the laws of [State/United States] that the foregoing is true and correct.

Executed on {date}, at {city}, {state}.

_________________________
{declarant_name}
"""
}

# Trial templates
TRIAL_TEMPLATES = {
    'witness_list': """
PLAINTIFF'S FINAL WITNESS LIST

Pursuant to the Court's Pre-Trial Order, Plaintiff {plaintiff_name} submits the following Final Witness List:

1. {witness_name}
   Address: {address}
   Expected Testimony: {summary_of_testimony}
   Time Estimate: {time}

2. {witness_name}
   [Continue...]

EXPERT WITNESSES:

1. {expert_name}
   Qualifications: {qualifications}
   Expected Testimony: {summary}
   Time Estimate: {time}

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
""",

    'exhibit_list': """
PLAINTIFF'S FINAL EXHIBIT LIST

Pursuant to the Court's Pre-Trial Order, Plaintiff {plaintiff_name} submits the following Final Exhibit List:

Exhibit A: {description}
Exhibit B: {description}
Exhibit C: {description}

[Continue with all exhibits...]

All exhibits will be pre-marked and available for inspection by opposing counsel prior to trial.

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
""",

    'jury_instructions': """
PLAINTIFF'S PROPOSED JURY INSTRUCTIONS

Plaintiff {plaintiff_name} respectfully submits the following proposed jury instructions:

INSTRUCTION NO. 1: Elements of [Claim]
To establish [claim], Plaintiff must prove by a preponderance of the evidence:
1. {element_1}
2. {element_2}
3. {element_3}
[Continue...]

INSTRUCTION NO. 2: Burden of Proof
[Standard instruction on preponderance of evidence]

INSTRUCTION NO. 3: Damages
[Instruction on calculating damages]

[Continue with all necessary instructions...]

Dated: {date}

_________________________
{attorney_name}
Attorney for Plaintiff
"""
}

def get_template(template_type: str, template_name: str) -> str:
    """Get a specific template by type and name"""
    templates = {
        'motion': MOTION_TEMPLATES,
        'discovery': DISCOVERY_TEMPLATES,
        'declaration': DECLARATION_TEMPLATES,
        'trial': TRIAL_TEMPLATES
    }
    return templates.get(template_type, {}).get(template_name, "")

def fill_template(template: str, **kwargs) -> str:
    """Fill a template with provided values"""
    return template.format(**kwargs)
