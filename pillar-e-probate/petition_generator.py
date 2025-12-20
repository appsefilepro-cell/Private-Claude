"""
Probate Petition Generator - California Judicial Council Forms
Automates generation of DE-series probate forms for estate administration
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

class ProbatePetitionGenerator:
    """Generates California probate court petitions and forms"""

    def __init__(self, templates_dir="pillar-e-probate/templates"):
        self.templates_dir = templates_dir
        self.forms_generated = []

    def generate_de111_petition(self, estate_info: Dict[str, Any]) -> str:
        """
        Generate DE-111: Petition for Probate

        Args:
            estate_info: Dictionary containing:
                - decedent_name: Full legal name
                - decedent_dod: Date of death
                - decedent_address: Last known address
                - petitioner_name: Person filing petition
                - petitioner_relationship: Relationship to decedent
                - will_exists: Boolean
                - trust_exists: Boolean
                - estimated_estate_value: Dollar amount
                - heirs: List of heir dictionaries

        Returns:
            Formatted petition text in markdown format
        """
        petition = f"""# PETITION FOR PROBATE
## Judicial Council Form DE-111

**SUPERIOR COURT OF CALIFORNIA**
**COUNTY OF LOS ANGELES**

---

### Case Information

**Case Number:** [To be assigned by court]
**Hearing Date:** [To be set]
**Dept:** Probate
**Time:** 8:30 AM

---

### ESTATE OF: {estate_info['decedent_name']}, Decedent

---

## 1. Publication will be in (specify name of newspaper):

The Daily Journal (Los Angeles)

---

## 2. Petitioner (name of each):

{estate_info['petitioner_name']}

requests that:

☒ a. Decedent's will and codicils, if any, be admitted to probate.
☒ b. {estate_info['petitioner_name']} be appointed:
    ☒ (1) executor
    ☐ (2) administrator with will annexed
    ☐ (3) administrator
    ☐ (4) special administrator

☒ c. Full authority be granted to administer under the Independent Administration of Estates Act.
☐ d. Bond not be required for the reasons stated in item 3d.
☒ e. Bond be fixed at: ${estate_info.get('bond_amount', estate_info['estimated_estate_value'])}
    ☐ to be furnished by an authorized surety company
    ☒ or as otherwise provided by law.

---

## 3. Decedent Information

**a. Decedent's name:** {estate_info['decedent_name']}

**b. Date of death:** {estate_info['decedent_dod']}

**c. Place of death:**
   ☐ County of Los Angeles, State of California
   ☒ Other: {estate_info.get('death_location', 'Harris County, Texas')}

**d. Street address, city, and county of decedent's residence at time of death:**
   {estate_info['decedent_address']}

**e. Character and estimated value of the property of the estate:**

   **Personal property:** ${estate_info.get('personal_property_value', 0):,.2f}
   **Real property:** ${estate_info.get('real_property_value', 0):,.2f}
   **Total:** ${estate_info['estimated_estate_value']:,.2f}

---

## 4. Will and Codicils

{'☒' if estate_info.get('will_exists') else '☐'} a. Decedent died testate. The will dated {estate_info.get('will_date', 'N/A')} and codicils, if any, are attached.

{'☒' if not estate_info.get('will_exists') else '☐'} b. Decedent died intestate.

---

## 5. Appointments and Authorizations

**a. Appointment of personal representative:**

{estate_info['petitioner_name']} is named as executor in the will and consents to act.

**b. Relationship to decedent:**

{estate_info['petitioner_relationship']} (Son/Child)

**c. Reasons for appointment:**

Petitioner is the natural son of decedent and is named in the will as executor. Petitioner is fully qualified and willing to serve as personal representative of the estate.

---

## 6. Residence of Decedent

At the time of death, decedent was:

☒ a. A resident of the county named above
☐ b. A nonresident of California

---

## 7. Heirs and Devisees

**Total heirs:** {len(estate_info.get('heirs', []))}

"""

        # Add each heir
        for idx, heir in enumerate(estate_info.get('heirs', []), 1):
            petition += f"""
**Heir {idx}:**
- Name: {heir['name']}
- Age: {heir.get('age', 'Adult')}
- Relationship: {heir['relationship']}
- Address: {heir.get('address', 'On file with court')}
"""

        petition += f"""

---

## 8. Surviving Spouse

{'☒' if estate_info.get('surviving_spouse') else '☐'} Decedent's surviving spouse is: {estate_info.get('surviving_spouse_name', 'N/A')}

Surviving spouse's interest in the estate:

{estate_info.get('spouse_interest_description', 'Community property interest as provided by California Probate Code')}

---

## 9. Trust Information

{'☒' if estate_info.get('trust_exists') else '☐'} Decedent was the settlor of a trust.

Trust name: {estate_info.get('trust_name', 'N/A')}
Trust date: {estate_info.get('trust_date', 'N/A')}

☒ A Certificate of Trust is attached (required by Prob. Code §16061.8)

---

## 10. Special Administration

{'☒' if estate_info.get('request_special_admin') else '☐'} Special administration is requested for the following reasons:

{estate_info.get('special_admin_reasons', 'To preserve estate assets and prevent waste or dissipation during pendency of probate proceedings.')}

---

## 11. Elder Abuse Allegations

{'☒' if estate_info.get('elder_abuse_alleged') else '☐'} Petitioner alleges financial elder abuse occurred.

**Description:**

{estate_info.get('elder_abuse_description', 'Decedent was subject to financial exploitation by surviving spouse, including unauthorized withdrawals, transfers, and misappropriation of estate funds exceeding $25,000. Detailed evidence is attached.')}

**Statutory basis:** Welfare & Institutions Code §15610.30 (financial abuse of elder)

**Relief requested:**
- Freeze of estate assets
- Removal of adverse party as trustee
- Surcharge for misappropriated funds
- Investigation and possible criminal referral

---

## 12. Verification

I declare under penalty of perjury under the laws of the State of California that the foregoing is true and correct.

Date: {datetime.now().strftime('%B %d, %Y')}

_______________________________
{estate_info['petitioner_name']}, Petitioner (Pro Se)

Address: {estate_info.get('petitioner_address', '')}
Phone: {estate_info.get('petitioner_phone', '')}
Email: {estate_info.get('petitioner_email', '')}

---

**Form Adopted for Mandatory Use**
**Judicial Council of California**
**DE-111 [Rev. January 1, 2025]**

---

**ATTACHMENTS:**
1. Death Certificate (certified copy)
2. Will and Codicils (if applicable)
3. Certificate of Trust
4. Copy of Trust (if applicable)
5. Declaration re: Elder Abuse with exhibits
6. Notice of Petition to Administer Estate (DE-121)
7. Duties and Liabilities of Personal Representative (DE-147)
8. Proposed Letters (DE-150)

**TOTAL PAGES:** [To be determined after assembly]

"""

        self.forms_generated.append(('DE-111', petition))
        return petition

    def generate_de121_notice(self, estate_info: Dict[str, Any], hearing_date: str = None) -> str:
        """
        Generate DE-121: Notice of Petition to Administer Estate

        Args:
            estate_info: Estate information dictionary
            hearing_date: Hearing date (if set), format: 'YYYY-MM-DD'

        Returns:
            Notice text in markdown format
        """
        if not hearing_date:
            # Default to 45 days from now (typical probate hearing window)
            hearing_datetime = datetime.now() + timedelta(days=45)
            hearing_date = hearing_datetime.strftime('%B %d, %Y')
        else:
            hearing_datetime = datetime.strptime(hearing_date, '%Y-%m-%d')
            hearing_date = hearing_datetime.strftime('%B %d, %Y')

        notice = f"""# NOTICE OF PETITION TO ADMINISTER ESTATE
## Judicial Council Form DE-121

---

**ESTATE OF:** {estate_info['decedent_name']}, also known as {estate_info.get('decedent_aka', estate_info['decedent_name'])}

**CASE NUMBER:** [Assigned by court]

---

To all heirs, beneficiaries, creditors, contingent creditors, and persons who may otherwise be interested in the will or estate, or both, of:

**{estate_info['decedent_name']}**

---

## NOTICE OF HEARING

A PETITION FOR PROBATE has been filed by:

**{estate_info['petitioner_name']}** in the Superior Court of California, County of Los Angeles.

THE PETITION FOR PROBATE requests that **{estate_info['petitioner_name']}** be appointed as personal representative to administer the estate of the decedent.

THE PETITION requests {'the decedent's will and codicils, if any, be admitted to probate.' if estate_info.get('will_exists') else 'that the estate be administered without a will.'}

THE PETITION requests authority to administer the estate under the Independent Administration of Estates Act. (This authority will allow the personal representative to take many actions without obtaining court approval. Before taking certain very important actions, however, the personal representative will be required to give notice to interested persons unless they have waived notice or consented to the proposed action.) The independent administration authority will be granted unless an interested person files an objection to the petition and shows good cause why the court should not grant the authority.

---

## HEARING INFORMATION

**A HEARING on the petition will be held:**

**Date:** {hearing_date}
**Time:** 8:30 AM
**Dept:** Probate Department, Room TBD
**Address:** Superior Court of California, County of Los Angeles
         Stanley Mosk Courthouse
         111 North Hill Street
         Los Angeles, CA 90012

---

## YOUR RIGHTS AND OPTIONS

**IF YOU OBJECT** to the granting of the petition, you should appear at the hearing and state your objections or file written objections with the court before the hearing. Your appearance may be in person or by your attorney.

**IF YOU ARE A CREDITOR** or a contingent creditor of the decedent, you must file your claim with the court and mail a copy to the personal representative appointed by the court within the later of either (1) four months from the date of first issuance of letters to a general personal representative, as defined in section 58(b) of the California Probate Code, or (2) 60 days from the date of mailing or personal delivery to you of a notice under section 9052 of the California Probate Code.

**Other California statutes and legal authority** may affect your rights as a creditor. You may want to consult with an attorney knowledgeable in California law.

**YOU MAY EXAMINE** the file kept by the court. If you are a person interested in the estate, you may file with the court a Request for Special Notice (form DE-154) of the filing of an inventory and appraisal of estate assets or of any petition or account as provided in Probate Code section 1250. A Request for Special Notice form is available from the court clerk.

---

## ATTORNEY FOR PETITIONER

{estate_info.get('attorney_name', estate_info['petitioner_name'] + ' (Pro Se)')}
{estate_info.get('attorney_address', estate_info.get('petitioner_address', ''))}
{estate_info.get('attorney_phone', estate_info.get('petitioner_phone', ''))}
{estate_info.get('attorney_email', estate_info.get('petitioner_email', ''))}

---

**Form Adopted for Mandatory Use**
**Judicial Council of California**
**DE-121 [Rev. January 1, 2025]**

**NOTICE OF PETITION TO ADMINISTER ESTATE**

"""

        self.forms_generated.append(('DE-121', notice))
        return notice

    def generate_de150_letters(self, estate_info: Dict[str, Any]) -> str:
        """
        Generate DE-150: Letters (Testamentary/Administration)
        Proposed order for court signature
        """
        letters = f"""# LETTERS
## Judicial Council Form DE-150

**SUPERIOR COURT OF CALIFORNIA, COUNTY OF LOS ANGELES**

**ESTATE OF:** {estate_info['decedent_name']}, Decedent

**CASE NUMBER:** ___________________

---

## ORDER APPOINTING PERSONAL REPRESENTATIVE

The court finds that all notices required by law have been given. The court appoints:

**{estate_info['petitioner_name']}**

as personal representative of the Estate of {estate_info['decedent_name']}, decedent, with the following powers and limitations:

---

## POWERS GRANTED

☒ **Full Authority under the Independent Administration of Estates Act** (Probate Code §§10400-10592)

The personal representative is authorized to administer the estate without court supervision, including but not limited to:

- Collecting estate assets
- Paying debts and expenses of administration
- Selling personal property
- Managing estate investments
- Filing tax returns
- Making distributions to heirs/beneficiaries (subject to notice requirements)

**Limitations on Independent Administration:**

Personal representative may NOT, without court approval:
- Sell real property (requires notice and possible court approval)
- Borrow money on behalf of estate
- Exchange or grant options on estate property
- Complete a contract entered into by decedent to convey real or personal property

---

## BOND

☒ Bond is fixed at: ${estate_info.get('bond_amount', estate_info['estimated_estate_value']):,.2f}

☐ Bond is waived

---

## ISSUANCE OF LETTERS

Upon qualification (filing of bond and oath), the clerk is directed to issue Letters to {estate_info['petitioner_name']}.

---

## SPECIAL ORDERS (if applicable)

{'☒ Surviving spouse ' + estate_info.get('surviving_spouse_name', '') + ' is ORDERED to provide a full accounting of all community property assets, separate property of decedent, and all transactions involving estate funds from date of death to present.' if estate_info.get('elder_abuse_alleged') else ''}

{'☒ All financial accounts in the name of decedent or payable on death to estate are FROZEN pending further order of this court.' if estate_info.get('request_asset_freeze') else ''}

{'☒ The court retains jurisdiction to hear elder abuse allegations under Welfare & Institutions Code §15610.30.' if estate_info.get('elder_abuse_alleged') else ''}

---

## DATE OF ORDER

Date: __________________, 2025

____________________________________
Judge of the Superior Court

---

**CERTIFICATION OF LETTERS**

I certify that this document is a correct copy of the original on file in this court and that the letters issued to the personal representative appointed above have not been revoked, annulled, or set aside, and are still in full force and effect.

Date: __________________

____________________________________
Clerk, by __________________________, Deputy

---

**Form Adopted for Mandatory Use**
**Judicial Council of California**
**DE-150 [Rev. January 1, 2025]**

"""

        self.forms_generated.append(('DE-150', letters))
        return letters

    def generate_complete_petition_package(self, estate_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate complete petition package with all required forms

        Returns:
            Dictionary with form names as keys and content as values
        """
        package = {}

        # Generate core forms
        package['DE-111_Petition'] = self.generate_de111_petition(estate_info)
        package['DE-121_Notice'] = self.generate_de121_notice(estate_info)
        package['DE-150_Letters'] = self.generate_de150_letters(estate_info)

        # Generate cover letter
        package['Cover_Letter'] = self.generate_cover_letter(estate_info)

        # Generate table of contents
        package['Table_of_Contents'] = self.generate_table_of_contents()

        return package

    def generate_cover_letter(self, estate_info: Dict[str, Any]) -> str:
        """Generate professional cover letter for filing"""
        return f"""**{estate_info['petitioner_name']}**
{estate_info.get('petitioner_address', '')}
{estate_info.get('petitioner_phone', '')}
{estate_info.get('petitioner_email', '')}

Petitioner in Pro Per

{datetime.now().strftime('%B %d, %Y')}

Clerk of the Superior Court
County of Los Angeles - Probate Division
Stanley Mosk Courthouse
111 North Hill Street
Los Angeles, CA 90012

**Re: Filing of Petition for Probate**
     **Estate of {estate_info['decedent_name']}, Decedent**

Dear Clerk:

Enclosed please find for filing:

1. Petition for Probate (Form DE-111)
2. Notice of Petition to Administer Estate (Form DE-121)
3. Proposed Letters (Form DE-150)
4. Duties and Liabilities of Personal Representative (Form DE-147)
5. Certified Copy of Death Certificate
6. {'Copy of Will and Certificate of Trust' if estate_info.get('will_exists') else 'Certificate of Trust'}
7. {'Declaration re: Elder Abuse with Exhibits' if estate_info.get('elder_abuse_alleged') else 'Supporting Declaration'}
8. Civil Case Cover Sheet

**Total Filing Fee Enclosed:** {'$0.00 (Fee Waiver Approved - FW-001 on file)' if estate_info.get('fee_waiver') else '$465.00'}

Please file the enclosed documents and set a hearing date for the Petition for Probate at the court's earliest convenience.

{'Due to allegations of financial elder abuse by the surviving spouse and risk of asset dissipation, I respectfully request that the court consider the request for special administration on an expedited basis.' if estate_info.get('elder_abuse_alleged') else ''}

If there are any deficiencies in the filing or additional documents required, please contact me at the phone number or email address above.

Thank you for your assistance.

Respectfully submitted,

_______________________________
{estate_info['petitioner_name']}
Petitioner in Pro Per

"""

    def generate_table_of_contents(self) -> str:
        """Generate table of contents for petition package"""
        toc = """# TABLE OF CONTENTS
## Petition for Probate - Complete Filing Package

---

**Tab** | **Document** | **Form Number** | **Pages**
--------|-------------|----------------|----------
1 | Cover Letter | N/A | 1
2 | Table of Contents | N/A | 1
3 | Civil Case Cover Sheet | CM-010 | 2
4 | Petition for Probate | DE-111 | 3-6
5 | Notice of Petition to Administer Estate | DE-121 | 2
6 | Duties and Liabilities of Personal Representative | DE-147 | 2
7 | Proposed Letters | DE-150 | 2
8 | Death Certificate (Certified Copy) | N/A | 1
9 | Certificate of Trust | N/A | 2
10 | Copy of Trust Document | N/A | 15-25
11 | Declaration of Petitioner | N/A | 5-10
12 | Elder Abuse Evidence (if applicable) | N/A | 10-30
13 | Proposed Order for Special Administration (if requested) | N/A | 2

---

**TOTAL ESTIMATED PAGES:** 50-85

**FILING FEE:** $465.00 (or $0.00 if fee waiver approved)

**CASE TYPE:** Probate - Decedent Estate

**ESTIMATED ESTATE VALUE:** [To be determined from petition]

---

**Prepared by:** [Petitioner name]
**Date Prepared:** [Current date]
**Filing Method:** E-filing via LACourtConnect or in-person at clerk's window

"""
        return toc

    def save_package(self, package: Dict[str, str], output_dir="pillar-e-probate/output"):
        """Save all forms to files"""
        os.makedirs(output_dir, exist_ok=True)

        for form_name, content in package.items():
            filepath = os.path.join(output_dir, f"{form_name}.md")
            with open(filepath, 'w') as f:
                f.write(content)

        print(f"✅ Generated {len(package)} forms in {output_dir}/")
        return output_dir


# Example usage and test
if __name__ == "__main__":
    # Example estate information
    estate_info = {
        "decedent_name": "Thurman Earl Robinson Sr.",
        "decedent_dod": "February 15, 2025",
        "decedent_address": "Houston, Harris County, Texas",
        "death_location": "Houston, Texas",
        "petitioner_name": "Thurman Malik Robinson Jr.",
        "petitioner_relationship": "Son",
        "petitioner_address": "Address on file",
        "petitioner_phone": "(XXX) XXX-XXXX",
        "petitioner_email": "email@example.com",
        "will_exists": False,
        "trust_exists": True,
        "trust_name": "Robinson Family Trust",
        "trust_date": "2015",
        "estimated_estate_value": 500000,
        "personal_property_value": 100000,
        "real_property_value": 400000,
        "bond_amount": 500000,
        "surviving_spouse": True,
        "surviving_spouse_name": "Fatimah Calvin Moore",
        "spouse_interest_description": "Alleged community property interest - contested due to elder abuse allegations",
        "heirs": [
            {"name": "Thurman Malik Robinson Jr.", "relationship": "Son", "age": "Adult"},
            {"name": "[Other heirs]", "relationship": "Child/Sibling", "age": "Adult"}
        ],
        "request_special_admin": True,
        "special_admin_reasons": "To preserve estate assets and prevent further dissipation by adverse party",
        "elder_abuse_alleged": True,
        "elder_abuse_description": "Surviving spouse misappropriated approximately $25,000 from insurance proceeds, made unauthorized withdrawals from accounts, and isolated decedent from family.",
        "request_asset_freeze": True,
        "fee_waiver": False
    }

    # Generate petition package
    generator = ProbatePetitionGenerator()
    package = generator.generate_complete_petition_package(estate_info)

    # Save to files
    generator.save_package(package)

    print("\n✅ Probate Petition Generator Test Complete")
    print(f"Generated forms: {list(package.keys())}")
